# GoWave docs

Documentation and landing page for [GoWave](https://github.com/aaaSaZaN/gowave), built with [Astro Starlight](https://starlight.astro.build). Russian is the default locale, English lives under `src/content/docs/en/`.

Use the Bun version in `package.json` and Node.js 22.23.4 or newer. Bun manages dependencies, scripts and tests; Astro runs on Node.js for compatibility with Pagefind's search index builder.

```bash
bun install --frozen-lockfile
bun run dev        # http://localhost:4321/gowave-docs/
bun run lint
bun run typecheck
bun run test
bun run build      # static site in dist/, including the search index
bun run check:build # internal links, local assets and API coverage
```

`bun.lock` pins the dependency tree. Direct dependencies use exact versions. Astro and Starlight provide Markdown/MDX, navigation, localization and search. Images are SVGs served through Astro's passthrough image service; no direct Sharp dependency is needed. Astro still lists Sharp as an optional transitive dependency.

The API reference at `/api/` is rendered from `public/api/openapi.json` by local Astro components with a small browser search script. Request and response schemas are displayed as expandable JSON. To update the contract, run `python3 scripts/sync_openapi.py /path/to/gowave` and rebuild the site.

Pushing to `main` publishes the site to GitHub Pages (`.github/workflows/deploy.yml`). In the repository settings set **Pages → Source** to **GitHub Actions**.

## Benchmark data

`src/data/benchmarks.json` (landing bars) and `src/data/benchmark-tables.json` (benchmarks page) are generated from benchmark results by `scripts/site_data.py`, which also copies the SVG charts into `public/benchmarks/`. Update the text on the benchmarks pages when the numbers change.
