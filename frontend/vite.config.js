import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/upload_prescription/': 'http://localhost:8000',
            '/ask_prescription/': 'http://localhost:8000',
            '/upload_pdfs/': 'http://localhost:8000',
            '/ask/': 'http://localhost:8000',
        },
    },
})
