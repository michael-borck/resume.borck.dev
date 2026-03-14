import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://resume.borck.dev',
  integrations: [
    starlight({
      title: 'resume.borck.dev',
      favicon: '/favicon.svg',
      logo: {
        src: './src-astro/assets/logo.svg',
        replacesTitle: true,
      },
      description: 'Michael Borck — Interactive resume experiences',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/michael-borck' },
        { icon: 'linkedin', label: 'LinkedIn', href: 'https://linkedin.com/in/michaelborck' },
        { icon: 'external', label: 'borck.dev', href: 'https://borck.dev' },
      ],
      customCss: ['./src-astro/styles/custom.css'],
      sidebar: [
        { label: 'Home', link: '/' },
      ],
    }),
  ],
  srcDir: './src-astro',
  publicDir: './public-astro',
});
