#!/bin/bash

# Script to help add workflow file via GitHub web interface
# Due to GitHub security restrictions, workflow files require special permissions

echo "🔧 Adding workflow file to GitHub..."
echo ""
echo "The workflow file needs to be added via GitHub's web interface."
echo "Opening the file creation page..."
echo ""

# Get the workflow file content
WORKFLOW_CONTENT=$(cat .github/workflows/deploy.yml)

# Create a temporary HTML file that can be used
cat > /tmp/workflow-content.txt << EOF
$WORKFLOW_CONTENT
EOF

echo "✅ Workflow file content saved to: /tmp/workflow-content.txt"
echo ""
echo "📋 Next steps:"
echo "1. Go to: https://github.com/sainisomesh/accessible-housing-matcher/new/main"
echo "2. In the file path box, type: .github/workflows/deploy.yml"
echo "3. Copy the content from /tmp/workflow-content.txt"
echo "4. Paste it into the editor"
echo "5. Click 'Commit new file'"
echo ""
echo "Or open the file to copy:"
echo "cat /tmp/workflow-content.txt"
echo ""

# Try to open browser (macOS)
open "https://github.com/sainisomesh/accessible-housing-matcher/new/main?filename=.github/workflows/deploy.yml" 2>/dev/null || echo "Please open the URL above manually"

