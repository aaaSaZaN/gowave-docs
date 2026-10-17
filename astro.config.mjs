// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Published to GitHub Pages as https://aaasazan.github.io/gowave-docs/.
// With a custom domain, set `site` to it and remove `base`.
export default defineConfig({
	site: 'https://aaasazan.github.io',
	base: '/gowave-docs',
	integrations: [
		starlight({
			title: 'GoWave',
			logo: { src: './src/assets/logo.svg' },
			defaultLocale: 'root',
			locales: {
				root: { label: 'Русский', lang: 'ru' },
				en: { label: 'English', lang: 'en' },
			},
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/aaaSaZaN/gowave' }],
			editLink: { baseUrl: 'https://github.com/aaaSaZaN/gowave-docs/edit/main/' },
			customCss: ['./src/styles/custom.css'],
			components: {
				SiteTitle: './src/components/SiteTitle.astro',
			},
			sidebar: [
				{
					label: 'Обзор',
					translations: { en: 'Overview' },
					items: ['overview/quick-start', 'overview/components', 'overview/comparison'],
				},
				{
					label: 'Установка',
					translations: { en: 'Install' },
					items: [
						'install/requirements',
						'install/installer',
						'install/docker',
						'install/systemd',
						{
							label: 'Reverse proxy',
							items: ['install/reverse-proxy/overview', 'install/reverse-proxy/caddy', 'install/reverse-proxy/nginx'],
						},
						{
							label: 'Go-нода',
							translations: { en: 'Go node' },
							items: ['install/node/install', 'install/node/configuration', 'install/node/cli'],
						},
						'install/subscription-page',
						'install/updating',
					],
				},
				{
					label: 'Возможности',
					translations: { en: 'Features' },
					items: ['features/subscription-rules', 'features/templates', 'features/template-variables'],
				},
				{
					label: 'Миграция',
					translations: { en: 'Migration' },
					items: ['migration/remnawave', 'migration/pasarguard', 'migration/sqlite-to-docker', 'migration/postgres-18', 'migration/docker-node'],
				},
				{
					label: 'Справочник',
					translations: { en: 'Reference' },
					items: ['reference/cli', 'reference/environment', 'reference/compatibility'],
				},
				{
					label: 'Ещё',
					translations: { en: 'More' },
					items: ['benchmarks', 'development'],
				},
			],
		}),
	],
});
