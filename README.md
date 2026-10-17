# GoWave docs

Documentation and landing page for [GoWave](https://github.com/aaaSaZaN/gowave), built with [Astro Starlight](https://starlight.astro.build). Russian is the default locale, English lives under `src/content/docs/en/`.

```bash
npm install
npm run dev      # http://localhost:4321/gowave-docs/
npm run build    # static site in dist/
```

Pushing to `main` publishes the site to GitHub Pages (`.github/workflows/deploy.yml`). In the repository settings set **Pages → Source** to **GitHub Actions**.

## Benchmark data

`src/data/benchmarks.json` (landing bars) and `src/data/benchmark-tables.json` (benchmarks page) are generated from benchmark results by `scripts/site_data.py`, which also copies the SVG charts into `public/benchmarks/`. Update the text on the benchmarks pages when the numbers change.
