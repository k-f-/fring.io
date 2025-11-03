# Content Management System

This directory contains **version-agnostic canonical content** for fring.io. All site versions (v2, v3, v4, etc.) can consume this data.

## Current Implementation

### books.json
- **Status:** ✅ Implemented
- **Purpose:** Canonical book list
- **Format:** JSON with year, title, yearLabel, dateAdded
- **Tools:**
  - `infrastructure/addbook.sh` - Add books
  - `infrastructure/regenerate_html.py` - Generate v3 HTML
- **Workflow:**
  ```bash
  ./infrastructure/addbook.sh "Book Title" 2025
  python3 infrastructure/regenerate_html.py
  git commit -am "Add book"
  ```

### now.json
- **Status:** ✅ Implemented
- **Purpose:** Current activities and status (/now page content)
- **Format:** JSON with location, sections (life/work/future), links
- **Source:** Extracted from v3 HTML

### career.json
- **Status:** ✅ Implemented
- **Purpose:** Professional experience and career history
- **Format:** JSON with summary, experience array, education, certifications, preferences
- **Source:** Extracted from LinkedIn profile

## Future Expansions

### 1. Apple Notes Integration (PLANNED - Mac Mini)
**Goal:** Automatically sync content from iCloud Notes to JSON

**Architecture:**
- Mac mini runs daily launchd job
- Reads specific notes from iCloud (e.g., "fring.io-books")
- Parses note content → updates JSON
- Auto-commits and pushes to GitHub
- GitHub Actions deploys to live site

**Note Format Examples:**
```
Note: "fring.io-books"
2025 | The Pragmatic Programmer
2024 | Foundation
<2015 | Dune

Note: "fring.io-now"
Last updated: 2025-11-02
Currently working on: New site design
Reading: Foundation
```

**Benefits:**
- Update from iPhone/iPad → auto-syncs everywhere
- Simple text interface
- iCloud handles sync/backup
- No web admin needed

**Implementation TODO:**
- [ ] Create `infrastructure/sync_notes_to_json.sh`
- [ ] Create `infrastructure/parse_notes_to_json.py`
- [ ] Create launchd plist for daily runs
- [ ] Setup Mac mini for 24/7 operation
- [ ] Test auto-commit workflow
- [ ] Add error notifications (email/slack?)

### 2. Additional Content Sections (PLANNED)

#### about.json
**Purpose:** Bio, contact info, social links
```json
{
  "name": "Kyle Fring",
  "location": "Chattanooga, TN",
  "bio": "Program Director at Fortune 500...",
  "contact": {
    "email": null,
    "github": "k-f-",
    "linkedin": "kfring"
  }
}
```

#### now.json
**Purpose:** Current activities (/now page)
```json
{
  "lastUpdated": "2025-11-02",
  "sections": {
    "life": "Most mornings I sweat at Crux...",
    "work": "Program Director for Fortune 500...",
    "reading": "Foundation",
    "projects": ["fring.io v4", "Bookshelf automation"]
  }
}
```

#### experience.json
**Purpose:** Work history, CV data
```json
{
  "jobs": [
    {
      "title": "Program Director",
      "company": "Fortune 500 Managed Care",
      "startDate": "2020-01",
      "endDate": null,
      "description": "Lead cross-functional initiatives...",
      "skills": ["Data Engineering", "Analytics", "Strategy"]
    }
  ],
  "education": [...],
  "certifications": [...]
}
```

#### projects.json
**Purpose:** Side projects, open source
```json
{
  "projects": [
    {
      "name": "fring.io",
      "description": "Personal website with monorepo architecture",
      "url": "https://fring.io",
      "status": "active",
      "tags": ["web", "static-site"]
    }
  ]
}
```

#### notes.json (Blog/Journal)
**Purpose:** Long-form writing
```json
{
  "notes": [
    {
      "title": "Why I love PragmataPro",
      "slug": "pragmatapro",
      "published": "2025-11-02",
      "updated": "2025-11-03",
      "tags": ["design", "typography"],
      "body": "Markdown content...",
      "source": "Apple Notes"
    }
  ]
}
```

### 3. Per-Section Modification Tools

Each section would get its own tooling:

**infrastructure/update_now.sh**
```bash
./infrastructure/update_now.sh --life "New life update" --reading "Foundation"
```

**infrastructure/add_project.sh**
```bash
./infrastructure/add_project.sh "Project Name" "https://github.com/..."
```

**infrastructure/add_job.sh**
```bash
./infrastructure/add_job.sh "Program Director" "Company" "2020-01"
```

## Benefits of This Approach

1. **Version Agnostic:** v2, v3, v4 all read same data
2. **Multiple Outputs:** Generate HTML, RSS, JSON API, sitemap
3. **Single Source of Truth:** Content lives in one place
4. **Easy Editing:** Simple JSON or Notes.app
5. **Portable:** Take content to any platform
6. **Searchable:** Can build search index from JSON
7. **Backup Friendly:** JSON is easy to backup/version control

## Workflow Overview

```
┌─────────────────┐
│  Apple Notes    │  (iPhone/iPad/Mac)
│  - Books        │
│  - Now updates  │
│  - Blog posts   │
└────────┬────────┘
         │ (daily sync via Mac mini)
         ↓
┌─────────────────┐
│  content/*.json │  (Canonical data)
│  - books.json   │
│  - now.json     │
│  - notes.json   │
└────────┬────────┘
         │ (regenerate scripts)
         ↓
┌─────────────────┐
│  sites/v3/      │  (HTML output)
│  sites/v4/      │
│  sites/api/     │  (JSON API)
│  sites/rss/     │  (RSS feed)
└─────────────────┘
         │
         ↓ (GitHub Actions)
┌─────────────────┐
│  Live Site      │
└─────────────────┘
```

## Implementation Priority

1. ✅ books.json (DONE)
2. ✅ now.json (DONE)
3. ✅ career.json (DONE - experience/CV data)
4. 📌 Apple Notes sync for books (Mac mini setup)
5. 🔜 about.json (simple, high value)
6. 🔜 notes.json (blog posts)
7. 🔜 projects.json

## Notes

- All JSON files include `meta` section with version and lastUpdated
- All dates in ISO 8601 format
- All content markdown-compatible where possible
- Git history provides audit trail of all changes
