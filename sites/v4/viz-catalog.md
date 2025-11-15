# Visualization Catalog - fring.io v4

Complete reference for all ASCII visualizations with unique identifiers.

## Overview

Total Visualizations: **17**
- Books Data: 5 variations
- Career Data: 4 variations
- Site Structure: 3 variations
- Reading Data: 2 visualizations
- Location Data: 1 visualization
- Tech/Decade Data: 2 visualizations

## Naming Convention

Format: `VIZ-{DATA}-{STYLE}-{NUMBER}`

- **DATA**: Source category (BOOKS, CAREER, SITE, TECH, READING, DECADE)
- **STYLE**: Visualization type (HBAR, VBAR, LINE, TREE, etc.)
- **NUMBER**: Sequential ID within category

## Books Visualizations

### VIZ-BOOKS-HBAR-001: Horizontal Bars
**Location**: sites/v4/index.html:150
**Function**: `generate_books_bar_chart()`
**Description**: Horizontal bar chart showing books per year (2015-2020 + prior)
**Features**:
- Descending year order (newest first)
- Integrated statistics header
- Sparkline trend indicator
- Prior books shown with lighter shade (░)

**Key Elements**:
- Solid blocks (█) for recent years
- Light blocks (░) for prior books
- Vertical separator (│)
- Continuous bars (no gaps)

---

### VIZ-BOOKS-VBAR-002: Vertical Bars
**Location**: sites/v4/index.html:204
**Function**: `generate_books_vertical_bars()`
**Description**: Vertical bar chart (rotated 90 degrees from horizontal)
**Features**:
- Each column represents a year
- Height proportional to book count
- Year labels at bottom

**Key Elements**:
- Block characters (█)
- 20-row height maximum
- Compact year notation (last 2 digits)

---

### VIZ-BOOKS-LINE-003: Line Graph
**Location**: sites/v4/index.html:230
**Function**: `generate_books_line_graph()`
**Description**: Line graph showing reading trend over years
**Features**:
- Diagonal lines connect data points
- Y-axis with numeric scale
- Trend visualization with slope indicators

**Key Elements**:
- Diagonal characters (╱ ╲)
- Horizontal connector (─)
- Data point marker (●)
- Axis characters (│ └)

---

### VIZ-BOOKS-SPARK-004: Compact Sparklines
**Location**: sites/v4/index.html:252
**Function**: `generate_books_sparkline()`
**Description**: Three variations of sparkline with statistics
**Features**:
- Blocks sparkline (▁▂▃▄▅▆▇█)
- Dots sparkline (· ○ ◉ ●)
- Bars sparkline (┆ │)
- Compact horizontal layout

**Key Elements**:
- Multiple character sets for same data
- Statistics summary
- Year notation (2-digit)

---

### VIZ-BOOKS-DOT-005: Dot Plot
**Location**: sites/v4/index.html:263
**Function**: `generate_books_dot_plot()`
**Description**: Scatter plot using dots to show distribution
**Features**:
- Each row represents one book
- Stacked dots per year
- Easy visual comparison

**Key Elements**:
- Dot markers (●)
- Y-axis numeric scale
- X-axis with full years

---

## Career Visualizations

### VIZ-CAREER-VERT-001: Vertical Upward
**Location**: sites/v4/index.html:163
**Function**: `generate_career_timeline()`
**Description**: Vertical timeline with upward progression
**Features**:
- Career progression moves bottom-to-top
- Current role marked with ▲
- Duration annotations

**Key Elements**:
- Vertical line (│)
- Branches (├──)
- Arrow indicator (◄──)
- Upward arrow (▲)

---

### VIZ-CAREER-HORIZ-002: Horizontal Timeline
**Location**: sites/v4/index.html:291
**Function**: `generate_career_horizontal()`
**Description**: Horizontal Gantt-style timeline
**Features**:
- Timeline from 2006-2025
- Year markers every 5 years
- Duration bars for each role

**Key Elements**:
- Horizontal bars (├─►)
- Year markers (┬)
- Timeline axis

---

### VIZ-CAREER-COMPACT-003: Compact Timeline
**Location**: sites/v4/index.html:301
**Function**: `generate_career_compact()`
**Description**: Minimal single-line timeline with abbreviations
**Features**:
- One-line representation
- Abbreviated role titles
- Legend for abbreviations

**Key Elements**:
- Arrow connectors (→)
- Abbreviations (PD, SDA, etc.)
- Legend section

---

### VIZ-CAREER-TREE-004: Organization View
**Location**: sites/v4/index.html:312
**Function**: `generate_career_tree()`
**Description**: Tree structure grouped by company
**Features**:
- Hierarchical company view
- Multiple roles per company
- Tree-style connectors

**Key Elements**:
- Tree branches (├── └──)
- Nested structure (│)
- Company grouping

---

## Site Structure Visualizations

### VIZ-SITE-TREE-001: Phylogenetic Tree
**Location**: sites/v4/index.html:182
**Function**: `generate_site_tree()`
**Description**: Phylogenetic-style site map with clickable links
**Features**:
- Hierarchical site structure
- Clickable HTML anchors
- Book counts per year

**Key Elements**:
- Complex branching (┌─┬─┐│├─┤└─┴─┘)
- HTML anchor tags
- Aligned structure

---

### VIZ-SITE-INDENT-002: Indented List
**Location**: sites/v4/index.html:324
**Function**: `generate_site_indent()`
**Description**: Simple indented list with Unicode tree chars
**Features**:
- Clean hierarchical view
- Standard tree notation
- Clickable links

**Key Elements**:
- Tree characters (├─ └─)
- Indentation levels
- Root node (□)

---

### VIZ-SITE-BOXES-003: Box Layout
**Location**: sites/v4/index.html:344
**Function**: `generate_site_boxes()`
**Description**: Card/box-style navigation grid
**Features**:
- 4-column grid layout
- Box-drawing characters
- Compact stats per section

**Key Elements**:
- Box frames (┌─┬─┐│├─┤└─┴─┘)
- Grid structure
- Aligned columns

---

## New Data Visualizations

### VIZ-TECH-STACK-001: Technology Timeline
**Location**: sites/v4/index.html:357
**Function**: `generate_tech_stack()`
**Description**: Current tech stack and experience timeline
**Features**:
- Categorized tech skills
- Timeline by technology area
- Current focus indicator

**Key Elements**:
- Bullet points (▪)
- Timeline bars (━)
- Current marker (◄──)

---

### VIZ-READING-VEL-001: Reading Velocity
**Location**: sites/v4/index.html:388
**Function**: `generate_reading_velocity()`
**Description**: Reading pace analysis with visual indicators
**Features**:
- Pace classification (High/Above/Below/Slow)
- Visual density bars
- Comparison to average

**Key Elements**:
- Block shades (█ ▓ ▒ ░)
- Pace indicators (▲ ▼)
- Bar length varies by pace

---

### VIZ-DECADE-DIST-001: Decade Distribution
**Location**: sites/v4/index.html:462
**Function**: `generate_decade_distribution()`
**Description**: Reading distribution by decade/era
**Features**:
- Era analysis
- Boxed summary statistics
- Reading phase breakdown

**Key Elements**:
- Box frame (┌─┐│├─┤└─┘)
- Progress bars
- Era labels

---

### VIZ-READING-CAL-001: Calendar Heatmap
**Location**: sites/v4/index.html:479
**Function**: `generate_reading_calendar()`
**Description**: GitHub-style calendar heatmap showing reading activity over time
**Features**:
- Week-by-week activity grid
- Month labels across top
- Intensity-based shading
- Shows peak reading year (2017)

**Key Elements**:
- Activity dots (·)
- Intensity blocks (░ ▒ ▓ █)
- 52-week horizontal grid
- Day-of-week labels (Mon/Wed/Fri/Sun)

---

### VIZ-LOCATION-ROAD-001: Chattanooga Highway Intersection
**Location**: sites/v4/index.html:492
**Function**: `generate_location_roadways()`
**Description**: Phylogenetic tree-style diagram showing major highway convergence in Chattanooga
**Features**:
- Three interstate highways (I-75, I-24, I-59)
- Directional flow (N/S/W/SW)
- Distance annotations to major cities
- The "75/24 Split" central hub visualization

**Key Elements**:
- Double-line characters (║ ═ ╬) for major highways
- Diagonal characters (╱) for branches
- City labels with distances
- Hub status annotation
- Location marker 📍

---

## Quick Reference

### By Data Source

| Data Source | Visualization Count | IDs |
|------------|-------------------|-----|
| Books | 5 | VIZ-BOOKS-HBAR-001 through VIZ-BOOKS-DOT-005 |
| Career | 4 | VIZ-CAREER-VERT-001 through VIZ-CAREER-TREE-004 |
| Site | 3 | VIZ-SITE-TREE-001 through VIZ-SITE-BOXES-003 |
| Tech | 1 | VIZ-TECH-STACK-001 |
| Reading | 2 | VIZ-READING-VEL-001, VIZ-READING-CAL-001 |
| Decade | 1 | VIZ-DECADE-DIST-001 |
| Location | 1 | VIZ-LOCATION-ROAD-001 |

### By Visualization Style

| Style | Description | Examples |
|-------|-------------|----------|
| Bar Charts | Horizontal/vertical bars | HBAR-001, VBAR-002 |
| Line Graphs | Connected trend lines | LINE-003 |
| Sparklines | Compact inline trends | SPARK-004 |
| Dot Plots | Scatter/distribution | DOT-005 |
| Timelines | Temporal sequences | VERT-001, HORIZ-002, COMPACT-003 |
| Trees | Hierarchical structures | TREE-001, TREE-004 |
| Lists | Indented hierarchies | INDENT-002 |
| Boxes | Grid layouts | BOXES-003 |

### Unicode Character Reference

| Character Type | Examples | Used In |
|---------------|----------|---------|
| Box Drawing | ┌─┬─┐│├─┤└─┴─┘ | TREE, BOXES, INDENT |
| Blocks | █ ▓ ▒ ░ | All bar charts |
| Sparklines | ▁▂▃▄▅▆▇█ | SPARK-004 |
| Dots | ● ◉ ○ · | SPARK-004, DOT-005 |
| Arrows | ► ◄ ▲ ▼ | CAREER, READING-VEL |
| Diagonal | ╱ ╲ | LINE-003 |
| Lines | ━ ─ │ ┆ | Various |

## HTML Integration

All visualizations use:
- **Class**: `visualization` for consistent styling
- **ID**: `viz-{lowercase-id}` for direct linking
- **Data Attribute**: `data-viz-id="{UPPERCASE-ID}"` for programmatic access

Example:
```html
<pre class="visualization" id="viz-books-hbar-001" data-viz-id="VIZ-BOOKS-HBAR-001">
...
</pre>
```

## Generator Script

File: `sites/v4/generate_visualizations.py`

To regenerate all visualizations:
```bash
cd sites/v4
python3 generate_visualizations.py
```

Each function follows naming convention: `generate_{data}_{style}()`

## Future Enhancement Ideas

- [ ] Interactive toggling between permutations
- [ ] Dark mode color variants
- [ ] Additional chart types (pie, radar)
- [x] Calendar heatmap (GitHub-style)
- [ ] Animation sequences
- [ ] Export to PNG/SVG
- [ ] Dynamic data updates
- [ ] Responsive sizing variants
- [ ] Horizontal grid layouts for side-by-side comparisons

## Version History

- **v1.2** (2025-11-14): Visualization Fixes & Location Map
  - **Fixed**: VIZ-BOOKS-LINE-003 spacing (3-char spacing per data point)
  - **Fixed**: VIZ-CAREER-HORIZ-002 order (newest roles first)
  - **Enhanced**: VIZ-SITE-INDENT-002 hyperlinks (12 links total)
    - Added Chattanooga Wikipedia link
    - Added year section links (#b2020, #b2019, etc.)
  - **New**: VIZ-LOCATION-ROAD-001 Chattanooga highway intersection
  - 17 total visualizations

- **v1.1** (2025-11-14): Week 1 Quick Wins
  - Added calendar heatmap visualization (VIZ-READING-CAL-001)
  - Integrated visualization styling with site aesthetic
  - CSS Grid horizontal layouts for side-by-side display
  - 16 total visualizations

- **v1.0** (2025-11-14): Initial catalog with 15 visualizations
  - 3 original visualizations
  - 12 new permutations
  - Complete identifier system
  - Full HTML integration
