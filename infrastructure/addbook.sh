#!/bin/bash
set -euo pipefail

# addbook.sh - Add a book to the canonical books.json
# Usage: ./addbook.sh "Book Title" [year]
#
# Examples:
#   ./addbook.sh "The Lord of the Rings"        # Uses current year
#   ./addbook.sh "Foundation" 2024              # Specific year
#   ./addbook.sh "Some Really Long Title That Goes On Forever" 2023  # Truncates at 73 chars

TITLE="${1:-}"
YEAR="${2:-$(date +%Y)}"
MAX_TITLE_LENGTH=73
BOOKS_JSON="content/books.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

if [[ -z "$TITLE" ]]; then
    echo "Usage: $0 <title> [year]"
    echo "Example: $0 \"The Lord of the Rings\" 2024"
    exit 1
fi

# Truncate title if too long
if [[ ${#TITLE} -gt $MAX_TITLE_LENGTH ]]; then
    TITLE="${TITLE:0:$MAX_TITLE_LENGTH}"
    echo "⚠️  Title truncated to $MAX_TITLE_LENGTH characters"
fi

# Add book to JSON using Python
python3 - <<EOF
import json
from datetime import datetime

# Load existing books
with open('$BOOKS_JSON', 'r') as f:
    data = json.load(f)

# Create new book entry
new_book = {
    "title": "$TITLE",
    "year": $YEAR,
    "yearLabel": None,
    "dateAdded": datetime.now().isoformat()
}

# Add to beginning (newest first)
data['books'].insert(0, new_book)

# Update meta
data['meta']['lastUpdated'] = datetime.now().isoformat()

# Save
with open('$BOOKS_JSON', 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ Added: [$YEAR] $TITLE")
print(f"  Total books: {len(data['books'])}")
EOF

echo ""
echo "Next steps:"
echo "  1. Run: python3 infrastructure/regenerate_html.py"
echo "  2. Review changes: git diff sites/v3/index.html"
echo "  3. Commit: git add content/books.json sites/v3/index.html && git commit"
