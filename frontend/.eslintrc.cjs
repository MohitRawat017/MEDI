module.exports = {
    root: true,
    env: { browser: true, es2020: true },
    extends: [
        'eslint:recommended',
        'plugin:react/recommended',
        'plugin:react-hooks/recommended',
    ],
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
    },
    plugins: ['react-refresh'],
    settings: { react: { version: 'detect' } },
    rules: {
        'react/prop-types': 'off',
        'react/react-in-jsx-scope': 'off',
        'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
        'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
    ignorePatterns: ['dist', 'node_modules'],
};
