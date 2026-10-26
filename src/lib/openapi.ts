const methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'] as const;
type Method = (typeof methods)[number];
type Security = Record<string, string[]>[];

interface Parameter {
	name?: string;
	in?: string;
	$ref?: string;
	[key: string]: unknown;
}

interface Operation {
	operationId?: string;
	summary?: string;
	description?: string;
	tags?: string[];
	parameters?: Parameter[];
	requestBody?: unknown;
	responses?: Record<string, unknown>;
	security?: Security;
	deprecated?: boolean;
}

export interface ApiDocument {
	paths: Record<string, Partial<Record<Method, Operation>> & { parameters?: Parameter[] }>;
	tags?: { name: string; description?: string }[];
	security?: Security;
}

export interface ApiOperation extends Operation {
	id: string;
	method: string;
	path: string;
	parameters: Parameter[];
	security: Security;
	searchText: string;
}

export function groupOperations(document: ApiDocument) {
	const groups = new Map(
		document.tags?.map((tag) => [tag.name, { ...tag, operations: [] as ApiOperation[] }]),
	);
	const ids = new Set<string>();
	for (const [path, item] of Object.entries(document.paths)) {
		for (const method of methods) {
			const operation = item[method];
			if (!operation) continue;
			const name = operation.tags?.[0] ?? 'Other';
			let group = groups.get(name);
			if (!group) {
				group = { name, description: undefined, operations: [] };
				groups.set(name, group);
			}
			const candidate = operation.operationId ?? `${method}-${path}`;
			let id = candidate;
			while (ids.has(id)) id += '-duplicate';
			ids.add(id);
			// Operation parameters override path parameters with the same name and location.
			const parameters = new Map(
				[...(item.parameters ?? []), ...(operation.parameters ?? [])].map((parameter) => [
					parameter.$ref ?? `${parameter.in}:${parameter.name}`,
					parameter,
				]),
			);
			group.operations.push({
				...operation,
				id,
				path,
				method: method.toUpperCase(),
				parameters: [...parameters.values()],
				security: operation.security ?? document.security ?? [],
				searchText: [
					method,
					path,
					operation.operationId,
					operation.summary,
					operation.description,
					...(operation.tags ?? []),
				]
					.filter(Boolean)
					.join(' '),
			});
		}
	}
	return [...groups.values()].filter((group) => group.operations.length > 0);
}

export function matchesSearch(text: string, query: string) {
	const value = text.toLowerCase();
	return query
		.toLowerCase()
		.trim()
		.split(/\s+/)
		.every((term) => value.includes(term));
}

// OpenAPI descriptions in this contract use inline code and bold text.
// Keep them as text tokens so Astro escapes their contents when rendering.
export function descriptionParts(text: string) {
	return text
		.split(/(`[^`]+`|\*\*[^*]+\*\*)/g)
		.filter(Boolean)
		.map((part) => {
			if (part.startsWith('`') && part.endsWith('`'))
				return { type: 'code', text: part.slice(1, -1) };
			if (part.startsWith('**') && part.endsWith('**'))
				return { type: 'strong', text: part.slice(2, -2) };
			return { type: 'text', text: part };
		});
}
