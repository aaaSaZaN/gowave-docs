import { matchesSearch } from '../lib/openapi';

const search = document.querySelector<HTMLInputElement>('#api-search');
const count = document.querySelector('#result-count');
const empty = document.querySelector<HTMLElement>('#no-results');
const operations = [...document.querySelectorAll<HTMLDetailsElement>('[data-operation]')];
const groups = [...document.querySelectorAll<HTMLElement>('[data-api-group]')];
const links = [...document.querySelectorAll<HTMLElement>('[data-nav-operation]')];
const navigation = [...document.querySelectorAll<HTMLElement>('[data-nav-group]')];

function filter() {
	const visible = new Set<string>();
	for (const operation of operations) {
		operation.hidden = !matchesSearch(operation.dataset.search ?? '', search?.value ?? '');
		if (!operation.hidden) visible.add(operation.id);
	}
	for (const link of links) link.hidden = !visible.has(link.dataset.navOperation ?? '');
	for (const group of groups) {
		group.hidden = !group.querySelector('[data-operation]:not([hidden])');
	}
	for (const group of navigation) {
		group.hidden = !group.querySelector('[data-nav-operation]:not([hidden])');
	}
	if (count) count.textContent = `${visible.size} endpoints`;
	if (empty) empty.hidden = visible.size > 0;
}

function openLinkedOperation() {
	let id: string;
	try {
		id = decodeURIComponent(location.hash.slice(1));
	} catch {
		return;
	}
	const target = document.getElementById(id);
	if (!(target instanceof HTMLDetailsElement)) return;
	if (search) search.value = '';
	filter();
	target.open = true;
	target.scrollIntoView();
}

search?.addEventListener('input', filter);
window.addEventListener('hashchange', openLinkedOperation);
openLinkedOperation();
