# AI Chat Application Documentation

This directory contains the documentation for the AI Chat Application, built with MkDocs and Material theme.

## Local Development

To build and serve the documentation locally:

```bash
# Install dependencies
pip install -r requirements-docs.txt

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## GitHub Pages

The documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch.

- **Live Site**: https://lichtbaer.github.io/ai-chat-app/
- **Source**: This directory
- **Build**: GitHub Actions workflow in `.github/workflows/docs.yml`

## Structure

- `index.md` - Main landing page
- `getting-started/` - Installation and setup guides
- `architecture/` - System design and architecture documentation
- `api/` - API reference documentation
- `deployment/` - Deployment guides
- `stylesheets/` - Custom CSS styles
- `javascripts/` - Custom JavaScript files
- `includes/` - Reusable content snippets

## Configuration

The documentation is configured via `mkdocs.yml` in the root directory. Key features:

- Material theme with dark/light mode
- Mermaid diagrams for architecture
- Search functionality
- Responsive design
- Git revision dates
- Code highlighting
- Admonitions and callouts 