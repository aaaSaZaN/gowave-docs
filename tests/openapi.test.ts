import { describe, expect, test } from 'bun:test';
import document from '../public/api/openapi.json';
import {
	type ApiDocument,
	descriptionParts,
	groupOperations,
	matchesSearch,
} from '../src/lib/openapi';

describe('API reference', () => {
	test('renders every contract operation exactly once, including GoWave extensions', () => {
		const groups = groupOperations(document);
		const operations = groups.flatMap((group) => group.operations);
		expect(operations).toHaveLength(228);
		expect(new Set(operations.map((operation) => operation.id)).size).toBe(operations.length);
		expect(groups[0]?.name).toBe('gowave');
		expect(operations.find((operation) => operation.operationId === 'Login')?.requestBody).toEqual(
			document.paths['/api/auth/login'].post.requestBody,
		);
		expect(operations.find((operation) => operation.operationId === 'Login')?.responses).toEqual(
			document.paths['/api/auth/login'].post.responses,
		);
	});

	test('handles every HTTP method and ignores path metadata', () => {
		const paths = {
			'/api/test': {
				parameters: [],
				summary: 'Not an operation',
				get: {},
				post: {},
				put: {},
				patch: {},
				delete: {},
				head: {},
				options: {},
				trace: {},
			},
		};
		expect(groupOperations({ paths })[0]?.operations.map((operation) => operation.method)).toEqual([
			'GET',
			'POST',
			'PUT',
			'PATCH',
			'DELETE',
			'HEAD',
			'OPTIONS',
			'TRACE',
		]);
	});

	test('inherits security, respects public overrides and merges parameters by location', () => {
		const spec: ApiDocument = {
			security: [{ bearer: [] }],
			paths: {
				'/users/{id}': {
					parameters: [
						{ name: 'id', in: 'path', required: true },
						{ name: 'id', in: 'query' },
					],
					get: {},
					post: { security: [], parameters: [{ name: 'id', in: 'query', required: true }] },
				},
			},
		};
		const [get, post] = groupOperations(spec)[0]?.operations ?? [];
		expect(get?.security).toEqual([{ bearer: [] }]);
		expect(post?.security).toEqual([]);
		expect(post?.parameters).toEqual([
			{ name: 'id', in: 'path', required: true },
			{ name: 'id', in: 'query', required: true },
		]);
	});

	test('omits empty groups, uses a fallback tag and keeps duplicate operation IDs addressable', () => {
		const groups = groupOperations({
			tags: [{ name: 'empty' }],
			paths: {
				'/a': { get: { operationId: 'duplicate' } },
				'/b': { get: { operationId: 'duplicate' } },
			},
		});
		expect(groups.map((group) => group.name)).toEqual(['Other']);
		expect(new Set(groups[0]?.operations.map((operation) => operation.id)).size).toBe(2);
		expect(groupOperations({ paths: {} })).toEqual([]);
	});
});

describe('endpoint search', () => {
	test('matches every query word regardless of case, spacing or order', () => {
		expect(matchesSearch('PATCH /api/nodes Update a node', '  NODE   patch ')).toBe(true);
		expect(matchesSearch('GET /api/users List users', 'post users')).toBe(false);
		expect(matchesSearch('GET /api/users', '  ')).toBe(true);
	});

	test('searches operation descriptions and tags without interpreting query syntax', () => {
		const operation = groupOperations({
			paths: { '/api/test': { get: { tags: ['gowave'], description: 'IPv6 [::1]' } } },
		})[0]?.operations[0];
		expect(matchesSearch(operation?.searchText ?? '', 'gowave ipv6')).toBe(true);
		expect(matchesSearch(operation?.searchText ?? '', '[::1]')).toBe(true);
		expect(matchesSearch(operation?.searchText ?? '', '.*')).toBe(false);
	});
});

describe('API descriptions', () => {
	test('formats code and emphasis while keeping HTML as text', () => {
		expect(descriptionParts('Use `<token>` for **API access**.')).toEqual([
			{ type: 'text', text: 'Use ' },
			{ type: 'code', text: '<token>' },
			{ type: 'text', text: ' for ' },
			{ type: 'strong', text: 'API access' },
			{ type: 'text', text: '.' },
		]);
		expect(descriptionParts('<script>alert(1)</script>')[0]?.type).toBe('text');
	});

	test('preserves incomplete markup and code containing emphasis markers', () => {
		expect(descriptionParts('`**literal**`')[0]).toEqual({ type: 'code', text: '**literal**' });
		expect(descriptionParts('`unclosed **text')).toEqual([
			{ type: 'text', text: '`unclosed **text' },
		]);
		expect(descriptionParts('')).toEqual([]);
	});
});
