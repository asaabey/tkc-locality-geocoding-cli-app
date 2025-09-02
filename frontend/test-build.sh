#!/bin/bash

# Simple Frontend Build Test - Must pass before commit
set -e

echo "=== Frontend Build Verification ==="
echo "Working directory: $(pwd)"

# Check we're in the right place
if [ ! -f "package.json" ]; then
    echo "ERROR: Must run from frontend directory"
    exit 1
fi

# Test 1: Check critical files exist
echo "1. Checking critical files..."
FILES_TO_CHECK=(
    "src/lib/api.ts"
    "src/lib/utils.ts"
    "src/components/LocationForm.tsx"
    "tsconfig.json"
    "tsconfig.app.json"
    "vite.config.ts"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        exit 1
    fi
done

# Test 2: TypeScript compilation
echo "2. Testing TypeScript compilation..."
if npx tsc -b; then
    echo "  ✓ TypeScript compilation successful"
else
    echo "  ✗ TypeScript compilation failed"
    exit 1
fi

# Test 3: Full build process
echo "3. Testing full build process..."
# Clean previous build
rm -rf dist/

if npm run build; then
    echo "  ✓ Build successful"
else
    echo "  ✗ Build failed"
    exit 1
fi

# Test 4: Check build outputs
echo "4. Checking build outputs..."
if [ -f "dist/index.html" ]; then
    echo "  ✓ index.html generated"
else
    echo "  ✗ index.html missing"
    exit 1
fi

if [ -d "dist/assets" ]; then
    echo "  ✓ assets directory generated"
else
    echo "  ✗ assets directory missing"
    exit 1
fi

# Success
echo ""
echo "🎉 ALL TESTS PASSED!"
echo ""
echo "The frontend build is working correctly."
echo "You can safely commit these changes."
echo ""
echo "To commit:"
echo "  git add ."
echo "  git commit -m 'fix: resolve TypeScript compilation issues for Netlify build'"