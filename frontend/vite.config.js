import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // If your GitHub Pages URL includes a repository name (not just username.github.io),
  // uncomment and update the base path below:
  // base: '/repository-name/',
  // Example: if your repo is "accessible-housing", and your site is at:
  // https://username.github.io/accessible-housing/
  // Then set: base: '/accessible-housing/'
})

