// Slidev calls the default export to get global Mermaid options.
// (Avoid importing @slidev/types so we don't depend on it being hoisted.)
export default () => ({
  theme: 'base',
  themeVariables: {
    fontFamily: 'Fira Code, ui-monospace, monospace',
    primaryColor: '#0b1324',
    primaryTextColor: '#e6eefb',
    primaryBorderColor: '#22d3ee',
    lineColor: '#38bdf8',
    secondaryColor: '#161f38',
    secondaryBorderColor: '#a78bfa',
    secondaryTextColor: '#e6eefb',
    tertiaryColor: '#0b1324',
    tertiaryBorderColor: '#334155',
    noteBkgColor: '#161f38',
    noteTextColor: '#8aa0c0',
    noteBorderColor: '#334155',
  },
})
