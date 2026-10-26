import assert from 'node:assert/strict';
import { resolve } from 'node:path';
import config from '../astro.config.mjs';
import document from '../public/api/openapi.json';
import { groupOperations } from '../src/lib/openapi';

const directory = resolve('dist');
const site = new URL(`${config.base}/`, config.site);
const files = new Set(await Array.fromAsync(new Bun.Glob('**/*').scan(directory)));
const pages = new Map<string, { ids: Set<string>; links: string[]; operations: number }>();

for (const file of files) {
	if (!file.endsWith('.html')) continue;
	const page = { ids: new Set<string>(), links: [] as string[], operations: 0 };
	const rewriter = new HTMLRewriter()
		.on('[id]', {
			element(element) {
				const id = element.getAttribute('id');
				if (id) page.ids.add(id);
			},
		})
		.on(
			'a[href], link[rel="stylesheet"], link[rel="icon"], link[rel="preload"], link[rel="modulepreload"]',
			{
				element(element) {
					const href = element.getAttribute('href');
					if (href) page.links.push(href);
				},
			},
		)
		.on('script[src], img[src]', {
			element(element) {
				const src = element.getAttribute('src');
				if (src) page.links.push(src);
			},
		})
		.on('[data-operation]', {
			element() {
				page.operations++;
			},
		});
	await rewriter.transform(new Response(Bun.file(`${directory}/${file}`))).text();
	pages.set(file, page);
}

assert(pages.size > 0, 'Build contains no HTML pages');
assert(files.has('pagefind/pagefind.js'), 'Search index is missing');
const api = pages.get('api/index.html');
assert(api, 'API reference is missing');
assert.equal(api.operations, groupOperations(document).flatMap((group) => group.operations).length);
assert(
	api.links.every((link) => new URL(link, site).origin === site.origin),
	'API reference loads an external resource',
);

let count = 0;
for (const [file, page] of pages) {
	const url = new URL(file.replace(/index\.html$/, ''), site);
	for (const link of page.links) {
		const target = new URL(link, url);
		if (target.origin !== site.origin) continue;
		assert(
			target.pathname.startsWith(site.pathname),
			`${file}: link outside deployment base: ${link}`,
		);
		let path = decodeURIComponent(target.pathname.slice(site.pathname.length));
		if (path === '' || path.endsWith('/')) path += 'index.html';
		else if (files.has(`${path}/index.html`)) path += '/index.html';
		assert(files.has(path), `${file}: missing target: ${link}`);
		const destination = pages.get(path);
		if (target.hash && destination) {
			assert(
				destination.ids.has(decodeURIComponent(target.hash.slice(1))),
				`${file}: missing anchor: ${link}`,
			);
		}
		count++;
	}
}
console.log(
	`Checked ${pages.size} HTML pages, ${count} local links and assets, ${api.operations} API operations and the search index.`,
);
