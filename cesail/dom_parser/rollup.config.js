// Rollup configuration for DOM Parser bundling
import resolve from '@rollup/plugin-node-resolve';

export default {
  input: 'src/js/index.js',
  output: {
    file: 'dist/dom-parser.js',
    format: 'iife',
    name: 'DOMParserExtract',
    sourcemap: true,
  },
  plugins: [
    resolve(),
  ],
  external: [], // No external dependencies for now
  treeshake: true,
  minify: false // Set to true for production builds
}; 