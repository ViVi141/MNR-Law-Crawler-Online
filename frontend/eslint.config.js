import js from '@eslint/js'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'
import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import vueTsConfig from '@vue/eslint-config-typescript'

export default [
  js.configs.recommended,
  ...vueTsConfig(),
  {
    files: ['**/*.{js,mjs,cjs,ts,vue}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    plugins: {
      vue,
      '@typescript-eslint': typescript,
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-unused-vars': 'off',
      '@typescript-eslint/no-explicit-any': 'warn', // 警告而非错误，允许在必要时使用any
      '@typescript-eslint/ban-ts-comment': 'warn',
      'no-useless-catch': 'warn',
    },
  },
  {
    ignores: [
      'dist',
      'node_modules',
      '*.config.js',
      '*.config.ts',
      'src/env.d.ts', // Vue 自动生成的类型定义文件，不应被 lint 检查
    ],
  },
]

