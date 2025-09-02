import { defineConfig } from 'vite'
// @ts-ignore
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
      "@/lib": resolve(__dirname, "./src/lib"),
      "@/components": resolve(__dirname, "./src/components"),
      "@/types": resolve(__dirname, "./src/types")
    }
  }
})
