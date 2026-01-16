import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import vueTs from '@vue/eslint-config-typescript'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default [
    {
        name: 'app/files-to-lint',
        files: ['**/*.{js,mjs,jsx,ts,tsx,vue}'],
    },

    {
        name: 'app/files-to-ignore',
        ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
    },

    js.configs.recommended,
    ...pluginVue.configs['flat/essential'],
    ...vueTs(),
    {
        languageOptions: {
            globals: {
                // Browser globals
                window: 'readonly',
                document: 'readonly',
                console: 'readonly',
                alert: 'readonly',
                confirm: 'readonly',
                prompt: 'readonly',
                setTimeout: 'readonly',
                clearTimeout: 'readonly',
                setInterval: 'readonly',
                clearInterval: 'readonly',
                fetch: 'readonly',
                localStorage: 'readonly',
                sessionStorage: 'readonly',
                navigator: 'readonly',
                location: 'readonly',
                history: 'readonly',
            },
        },
    },
    skipFormatting,
]
