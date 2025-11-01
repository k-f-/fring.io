# fring.io v4 - Design Plan

## Philosophy

Building on v2 and v3's minimalist foundation while adding subtle modern enhancements:

- **Performance First**: Sub-1KB initial load, no JavaScript required
- **Content Over Form**: Text-focused, readable, accessible
- **Progressive Enhancement**: Works everywhere, enhanced where supported
- **Longevity**: Will look good in 10 years

## Design Evolution

### v1 → v2 → v3 → v4
- **v1**: Jekyll blog, complex build pipeline, feature-rich
- **v2**: Radical simplification, single HTML file, custom font
- **v3**: Refined v2, better font fallbacks, updated content
- **v4**: Modern minimalism with personality

## Proposed Enhancements

### 1. Visual Design
- **Color Palette**:
  - Add subtle color accents (muted blues/greens for links)
  - Optional dark mode with CSS `prefers-color-scheme`
  - Higher contrast for better accessibility

- **Typography**:
  - System font stack (continue v3's approach)
  - Optional: CSS variable font for personality without weight
  - Better hierarchy with font sizes

- **Layout**:
  - Keep max-width: 800px for readability
  - Add subtle visual rhythm with spacing
  - Consider CSS Grid for future flexibility

### 2. Content Additions
- **Now Page**: Update to 2025 (current v3 is from 2020)
- **Projects**: Small section for side projects/experiments
- **Uses**: Tools, software, gear you use (inspired by uses.tech)
- **Writing**: Short-form thoughts (not a full blog)
- **Contact**: Better contact info or form

### 3. Technical Improvements
- **Accessibility**:
  - Semantic HTML5 elements (`<main>`, `<article>`, `<section>`)
  - ARIA labels where needed
  - Keyboard navigation enhancement
  - Focus indicators

- **Performance**:
  - Inline critical CSS
  - Preload fonts if using custom fonts
  - Optimize images with WebP/AVIF
  - Add meta tags for social sharing (Open Graph)

- **SEO**:
  - Structured data (JSON-LD)
  - Better meta descriptions
  - Canonical URLs

### 4. Progressive Features
These work only if browser supports, degrade gracefully:

- **CSS Variables**: For theming
- **Dark Mode**: System preference detection
- **Smooth Scrolling**: For anchor links
- **CSS Animations**: Subtle fade-ins (optional)
- **View Transitions API**: Page transitions (future-proofing)

## Proposed Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kyle Fring</title>
  <meta name="description" content="Personal site of Kyle Fring - Data Engineer, Reader, Climber">

  <!-- Open Graph -->
  <meta property="og:title" content="Kyle Fring">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://fring.io">

  <!-- Inline critical CSS -->
  <style>/* ... */</style>
</head>
<body>
  <header>
    <h1>Kyle Fring</h1>
    <nav>
      <a href="#now">Now</a>
      <a href="#projects">Projects</a>
      <a href="#bookshelf">Bookshelf</a>
      <a href="#uses">Uses</a>
      <a href="#elsewhere">Elsewhere</a>
    </nav>
  </header>

  <main>
    <section id="now">
      <h2>Now</h2>
      <!-- Current status, updated regularly -->
    </section>

    <section id="projects">
      <h2>Projects</h2>
      <!-- Side projects, experiments -->
    </section>

    <section id="bookshelf">
      <h2>Bookshelf</h2>
      <!-- Collapsible by year? -->
    </section>

    <section id="uses">
      <h2>Uses</h2>
      <!-- Tools, software, gear -->
    </section>

    <section id="elsewhere">
      <h2>Elsewhere</h2>
      <!-- Social links, profiles -->
    </section>
  </main>

  <footer>
    <p><a href="#epilogue">Epilogue</a></p>
  </footer>
</body>
</html>
```

## Color Scheme Ideas

### Option 1: Monochrome++
```css
:root {
  --bg: #fefefe;
  --text: #333;
  --text-light: #666;
  --accent: #0066cc;
  --border: #ddd;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --text: #e0e0e0;
    --text-light: #999;
    --accent: #4d9fff;
    --border: #333;
  }
}
```

### Option 2: Warm Minimal
```css
:root {
  --bg: #fffef7;
  --text: #2c2c2c;
  --accent: #8b4513; /* saddle brown */
  --accent-light: #d2691e; /* chocolate */
}
```

### Option 3: Cool Minimal (Recommended)
```css
:root {
  --bg: #fafafa;
  --text: #1a1a1a;
  --text-muted: #6b7280;
  --accent: #2563eb; /* blue-600 */
  --accent-hover: #1d4ed8; /* blue-700 */
  --border: #e5e7eb;
  --code-bg: #f3f4f6;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a;
    --text: #f1f5f9;
    --text-muted: #94a3b8;
    --accent: #60a5fa; /* blue-400 */
    --accent-hover: #3b82f6; /* blue-500 */
    --border: #1e293b;
    --code-bg: #1e293b;
  }
}
```

## Typography Stack

```css
/* Primary */
font-family:
  -apple-system, BlinkMacSystemFont,
  "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell",
  "Fira Sans", "Droid Sans", "Helvetica Neue",
  sans-serif;

/* Monospace (for code, headings) */
font-family:
  ui-monospace, 'SF Mono', 'Cascadia Code', 'Source Code Pro',
  Menlo, Monaco, 'Courier New', monospace;

/* Optional: Serif for body text */
font-family:
  'Iowan Old Style', 'Palatino Linotype', 'URW Palladio L',
  P052, serif;
```

## New Content Ideas

### Projects Section
```markdown
## Projects

**fring.io Infrastructure** - This site's deployment pipeline using GitHub Actions, S3, and CloudFront ([repo](https://github.com/k-f-/fring.io))

**[Project Name]** - Brief description with tech stack

**[Experiment]** - Something you're tinkering with
```

### Uses Section
```markdown
## Uses

### Editor & Terminal
- **Editor**: VS Code, Vim
- **Terminal**: iTerm2, zsh
- **Font**: [Your preferred font]

### Development
- **Languages**: Python, SQL, Bash
- **Tools**: Docker, Git, AWS CLI

### Productivity
- **Notes**: Obsidian, Notion
- **Reading**: Kindle, Safari Books

### Hardware
- **Laptop**: [Model]
- **Monitor**: [Model]
```

### Writing Section (Optional)
Short-form thoughts, not full blog posts:

```markdown
## Writing

**2025-01-15** - Thoughts on [topic]

**2024-12-20** - Quick note about [something]
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up v4.fring.io infrastructure
- [ ] Create basic HTML structure
- [ ] Implement color scheme and typography
- [ ] Dark mode support
- [ ] Accessibility audit

### Phase 2: Content (Week 2)
- [ ] Update Now page (2025 content)
- [ ] Add Projects section
- [ ] Add Uses section
- [ ] Migrate Bookshelf from v3
- [ ] Update Elsewhere links

### Phase 3: Polish (Week 3)
- [ ] SEO meta tags and structured data
- [ ] Social sharing cards (Open Graph)
- [ ] Performance optimization
- [ ] Cross-browser testing
- [ ] Mobile responsiveness check

### Phase 4: Deploy (Week 4)
- [ ] Deploy to v4.fring.io
- [ ] Get feedback
- [ ] Iterate based on feedback
- [ ] Promote to main (fring.io)

## Inspiration Sites

- [Brutalist Websites](https://brutalistwebsites.com)
- [uses.tech](https://uses.tech)
- [nownownow.com](https://nownownow.com)
- [motherfuckingwebsite.com](http://motherfuckingwebsite.com)
- [txti.es](http://txti.es)

## Metrics for Success

- **Load Time**: < 500ms (first paint)
- **Size**: < 5KB HTML (uncompressed)
- **Size**: < 10KB total (with CSS)
- **Lighthouse Score**: 100/100/100/100
- **Works without JS**: ✅
- **Works on Lynx browser**: ✅
- **Readable on mobile**: ✅
- **Printable**: ✅

## Future Considerations

- **RSS Feed**: For writing section
- **Webmentions**: For social interactions
- **Analytics**: Privacy-focused (Plausible, umami)
- **Comments**: Giscus (GitHub Discussions)
- **Newsletter**: Buttondown, Substack

## Questions to Answer

1. **Custom domain for projects?** (projects.fring.io)
2. **Subdomain for writing?** (blog.fring.io or writing.fring.io)
3. **Photo gallery?** (climbing, travels)
4. **Resume/CV page?** (resume.fring.io or /cv)
5. **Interactive elements?** (e.g., theme switcher button)

## Design Principles

1. **Fast**: Every byte counts
2. **Accessible**: Everyone can use it
3. **Sustainable**: Low energy, long-lasting
4. **Honest**: No tracking, no BS
5. **Personal**: Reflects your personality
6. **Timeless**: Won't look dated in 5 years

## Technical Constraints

- **No JavaScript required**: Progressive enhancement only
- **No frameworks**: Vanilla HTML/CSS
- **No build step**: Direct HTML (optional: minimal CSS processing)
- **No analytics**: Privacy-first (or privacy-focused only)
- **No cookies**: GDPR-friendly by default

## Next Steps

1. Review this plan and provide feedback
2. Choose color scheme (1, 2, or 3)
3. Decide on new sections (Projects, Uses, Writing)
4. Set up v4.fring.io infrastructure
5. Start building!
