#!/bin/bash

# Frontend Build Verification Script
# This script must pass before committing frontend changes

set -e  # Exit on any error

echo "🔍 Frontend Build Verification Starting..."
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to log test results
log_test() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $2${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to run tests and log results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}🧪 Testing: $test_name${NC}"
    
    if eval "$test_command" > /tmp/test_output 2>&1; then
        log_test 0 "$test_name"
    else
        log_test 1 "$test_name"
        echo "Error output:"
        cat /tmp/test_output
        return 1
    fi
}

echo "📁 Working directory: $(pwd)"

# 1. Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Must run from frontend directory${NC}"
    exit 1
fi

# 2. Check if required files exist
echo -e "${YELLOW}🔍 Checking required files...${NC}"
REQUIRED_FILES=(
    "src/lib/api.ts"
    "src/lib/utils.ts" 
    "src/components/LocationForm.tsx"
    "src/components/ui/button.tsx"
    "src/components/ui/card.tsx"
    "src/components/ui/input.tsx"
    "src/components/ui/textarea.tsx"
    "tsconfig.json"
    "tsconfig.app.json"
    "tsconfig.node.json"
    "vite.config.ts"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_test 0 "File exists: $file"
    else
        log_test 1 "File exists: $file"
    fi
done

# 3. Check TypeScript configuration
run_test "TypeScript configuration is valid" "npx tsc --noEmit --project tsconfig.json"

# 4. Check TypeScript compilation (build mode)
run_test "TypeScript build compilation (tsc -b)" "npx tsc -b"

# 5. Check if dependencies are installed
run_test "Dependencies are installed" "[ -d node_modules ]"

# 6. Check for TypeScript errors in source files
run_test "No TypeScript errors in app files" "npx tsc --noEmit --project tsconfig.app.json"

# 7. Check for TypeScript errors in config files
run_test "No TypeScript errors in node config" "npx tsc --noEmit --project tsconfig.node.json"

# 8. Run ESLint if available
if npx eslint --version > /dev/null 2>&1; then
    run_test "ESLint passes" "npx eslint . --max-warnings 0"
else
    echo -e "${YELLOW}⚠️  ESLint not available, skipping${NC}"
fi

# 9. Test full build process
echo -e "${YELLOW}🏗️  Testing full build process...${NC}"
rm -rf dist/  # Clean previous build

run_test "Full build process (npm run build)" "npm run build"

# 10. Check if build artifacts were created
BUILD_ARTIFACTS=(
    "dist/index.html"
    "dist/assets"
)

for artifact in "${BUILD_ARTIFACTS[@]}"; do
    if [ -e "$artifact" ]; then
        log_test 0 "Build artifact exists: $artifact"
    else
        log_test 1 "Build artifact exists: $artifact"
    fi
done

# 11. Check build size (warn if too large)
if [ -d "dist" ]; then
    BUILD_SIZE=$(du -sh dist | cut -f1)
    echo -e "${GREEN}📦 Build size: $BUILD_SIZE${NC}"
    
    # Convert to MB for comparison (rough)
    SIZE_MB=$(du -sm dist | cut -f1)
    if [ "$SIZE_MB" -gt 50 ]; then
        echo -e "${YELLOW}⚠️  Warning: Build size is larger than 50MB${NC}"
    fi
fi

# 12. Verify critical imports work
echo -e "${YELLOW}🔗 Verifying module imports...${NC}"
IMPORT_CHECK=$(mktemp)
cat > "$IMPORT_CHECK" << 'EOF'
import { geocodeApi } from './src/lib/api';
import { cn } from './src/lib/utils';
import { LocationForm } from './src/components/LocationForm';
import { Button } from './src/components/ui/button';

console.log('All imports successful');
EOF

# Note: This is a basic syntax check, actual runtime would need more setup
if npx tsc --noEmit --allowJs --checkJs "$IMPORT_CHECK" 2>/dev/null; then
    log_test 0 "Module imports syntax check"
else
    log_test 1 "Module imports syntax check"
fi
rm -f "$IMPORT_CHECK"

# Summary
echo ""
echo "==========================================="
echo -e "${GREEN}✅ Tests passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}❌ Tests failed: $TESTS_FAILED${NC}"
    echo ""
    echo -e "${RED}🚫 Build verification FAILED. Do not commit until all tests pass.${NC}"
    exit 1
else
    echo -e "${GREEN}🎉 All tests passed! Ready to commit.${NC}"
    echo ""
    echo "To commit your changes:"
    echo "  git add ."
    echo "  git commit -m 'fix: resolve TypeScript compilation issues'"
fi

# Clean up
rm -f /tmp/test_output