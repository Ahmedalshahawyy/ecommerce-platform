module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended'
  ],
  parserOptions: {
    ecmaFeatures: { jsx: true },
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  settings: { react: { version: 'detect' } },
  rules: {
    // New JSX transform makes importing React unnecessary
    'react/react-in-jsx-scope': 'off'
  }
}
