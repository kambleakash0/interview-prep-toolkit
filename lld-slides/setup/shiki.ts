// Slidev calls the default export to configure the Shiki code highlighter.
// (Avoid importing @slidev/types so we don't depend on it being hoisted.)
export default () => ({
  themes: {
    dark: 'one-dark-pro',
    light: 'github-light',
  },
})
