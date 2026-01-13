#!/bin/bash
echo "Clearing all caches..."

# Clear Vite cache
rm -rf node_modules/.vite
rm -rf .vite

# Clear build output
rm -rf dist

# Clear browser cache hints (for development)
echo "Cache cleared! Please:"
echo "1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "2. Or restart your dev server: npm run dev"
