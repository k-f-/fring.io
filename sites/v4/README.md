# v4 - ASCII Visualization Experiments

## Overview

This version explores data visualization using extended monospace fonts with advanced box-drawing and Unicode characters. Inspired by ASCII art phylogenetic trees and data charts.

## Features

### Data Visualizations

1. **Reading Activity Bar Chart**
   - Horizontal bar chart showing books read per year (2015-2020)
   - Uses block characters (█) for visual bars
   - Data source: `content/books.json`

2. **Career Timeline**
   - Gantt-style timeline visualization
   - Shows professional roles from 2006-present
   - Uses box-drawing characters: `├─┤►`
   - Data source: `content/career.json`

3. **Site Structure Tree**
   - Hierarchical tree diagram (phylogenetic tree style)
   - Visualizes website content organization
   - Uses extended Unicode: `┌─┬─┐│├─┤└─┴─┘`

4. **Reading Statistics**
   - Statistical summary with sparkline
   - Uses block characters: `▁▂▃▄▅▆▇█`
   - Genre distribution tree

## Technical Implementation

### Fonts
- Uses extended monospace font with ligatures for enhanced box-drawing
- Font files: `fonts/monospace-ext-*.ttf`
- Fallback chain: `'Monospace Extended', 'SF Mono', SFMono-Regular, ui-monospace, monospace`

### Styling
- All visualizations in `<pre class="visualization">` blocks
- Fixed-width font ensures proper alignment
- Responsive font sizing (0.85rem)
- Light background with accent border

### Data Processing
- Python script: `generate_visualizations.py`
- Reads canonical JSON data from `content/` directory
- Generates ASCII art programmatically
- Can be regenerated when data changes

## Box-Drawing Characters Used

```
Lines:     ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
Arrows:    ◄ ► ▲ ▼
Blocks:    █ ▓ ▒ ░
Sparkline: ▁ ▂ ▃ ▄ ▅ ▆ ▇ █
```

## Usage

### Viewing Locally
```bash
cd sites/v4
python3 -m http.server 8888
# Open http://localhost:8888
```

### Regenerating Visualizations
```bash
cd sites/v4
python3 generate_visualizations.py
# Copy output into HTML manually or update script to auto-inject
```

## Future Enhancements

- [ ] Dynamic visualization generation (JavaScript)
- [ ] Dark mode color scheme support
- [ ] Additional chart types (pie charts, scatter plots)
- [ ] Interactive elements (hover states, tooltips)
- [ ] More data sources (music, projects, skills)
- [ ] Animated ASCII charts
- [ ] Export visualizations as images

## Philosophy

Continues the fring.io tradition of:
- Minimal dependencies
- Fast loading
- Text-first design
- Accessibility
- Progressive enhancement
- No JavaScript required (static visualizations)

## References

- [Box Drawing Unicode Block](https://en.wikipedia.org/wiki/Box-drawing_character)
- [Block Elements Unicode](https://en.wikipedia.org/wiki/Block_Elements)
- ASCII art phylogenetic trees for inspiration
