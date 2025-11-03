#!/bin/bash
set -euo pipefail

# addbook.sh - Add a book to the bookshelf with proper alignment
# Usage: ./addbook.sh "Book Title" [year]
#
# Examples:
#   ./addbook.sh "The Lord of the Rings"        # Uses current year
#   ./addbook.sh "Foundation" 2024              # Specific year
#   ./addbook.sh "Some Really Long Title That Goes On Forever" 2023  # Truncates

TITLE="${1:-}"
YEAR="${2:-$(date +%Y)}"
MAX_TITLE_LENGTH=73
BOOK_FILE="../sites/v3/index.html"

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

# Pad title to exactly MAX_TITLE_LENGTH
PADDED_TITLE=$(printf "%-${MAX_TITLE_LENGTH}s" "$TITLE")

# Format the book line
BOOK_LINE="| ${YEAR} | ${PADDED_TITLE}|"

echo "Adding book:"
echo "$BOOK_LINE"
echo ""
echo "Please manually add this line to $BOOK_FILE in the correct chronological position."
echo "Or pipe to clipboard: echo \"$BOOK_LINE\" | pbcopy"
