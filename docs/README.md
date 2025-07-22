# AI Assistant Platform Documentation

This directory contains the comprehensive documentation for the AI Assistant Platform, built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

## 📚 Documentation Structure

```
docs/
├── mkdocs.yml              # MkDocs configuration
├── index.md                # Homepage
├── requirements-docs.txt   # Documentation dependencies
├── stylesheets/            # Custom CSS styles
│   └── extra.css
├── javascripts/            # Custom JavaScript
│   └── mathjax.js
├── getting-started/        # Getting started guides
├── architecture/           # System architecture
├── development/            # Development guides
├── api/                    # API documentation
├── features/               # Feature documentation
├── deployment/             # Deployment guides
└── project/                # Project information
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Install documentation dependencies:**
   ```bash
   cd docs
   pip install -r requirements-docs.txt
   ```

2. **Serve documentation locally:**
   ```bash
   mkdocs serve
   ```

3. **Open your browser:**
   Navigate to http://127.0.0.1:8000

### Using Makefile Commands

From the project root, you can use the following Makefile commands:

```bash
# Install documentation dependencies
make docs-install

# Serve documentation locally
make docs-serve

# Build documentation
make docs-build

# Deploy to GitHub Pages
make docs-deploy

# Clean build files
make docs-clean
```

## 📖 Documentation Sections

### Getting Started
- **Quick Start**: Get up and running in minutes
- **Installation**: Detailed installation instructions
- **Configuration**: Environment and service setup

### Architecture
- **Overview**: High-level system architecture
- **Backend**: FastAPI backend design
- **Frontend**: Frontend architecture (planned)
- **Database**: Database design and schema

### Development
- **Setup**: Development environment setup
- **Testing**: Running tests and test coverage
- **Contributing**: How to contribute to the project
- **Code Style**: Coding standards and conventions

### API Reference
- **Overview**: API design principles
- **Authentication**: Authentication and authorization
- **Endpoints**: Complete API endpoint reference
- **Models**: Data models and schemas

### Features
- **AI Integration**: AI provider integration details
- **Internationalization**: Multi-language support
- **Security**: Security features and best practices
- **Tools**: Tool integration and execution

### Deployment
- **Docker**: Containerized deployment
- **Production**: Production deployment guide
- **Monitoring**: Monitoring and observability

### Project
- **Status**: Current project status and progress
- **Roadmap**: Development roadmap and timeline
- **Changelog**: Version history and changes

## 🎨 Customization

### Styling

Custom styles are defined in `stylesheets/extra.css`:

- Custom color scheme
- Feature cards
- Status badges
- Timeline styling
- Responsive design
- Dark mode support

### JavaScript

Custom JavaScript functionality in `javascripts/mathjax.js`:

- MathJax configuration for mathematical expressions
- Custom initialization scripts

### Configuration

The main configuration is in `mkdocs.yml`:

- Site metadata
- Theme configuration
- Navigation structure
- Markdown extensions
- Plugins

## 🔧 Development

### Adding New Pages

1. Create a new Markdown file in the appropriate directory
2. Add the page to the navigation in `mkdocs.yml`
3. Follow the existing documentation style

### Styling Guidelines

- Use consistent heading hierarchy (H1 → H2 → H3)
- Include code examples with syntax highlighting
- Use admonitions for important information
- Add links to related documentation
- Include screenshots for UI elements

### Code Examples

Use fenced code blocks with language specification:

```python
def example_function():
    """Example function with docstring."""
    return "Hello, World!"
```

### Admonitions

Use admonitions for important information:

!!! info "Information"
    This is an informational note.

!!! warning "Warning"
    This is a warning message.

!!! danger "Danger"
    This is a danger message.

!!! success "Success"
    This is a success message.

## 📦 Building and Deployment

### Local Build

```bash
# Build the documentation
mkdocs build

# The built site will be in the `site/` directory
```

### GitHub Pages Deployment

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# This will build and deploy to the `gh-pages` branch
```

### Custom Domain

To use a custom domain:

1. Add the domain to `mkdocs.yml`:
   ```yaml
   site_url: https://your-domain.com
   ```

2. Create a `CNAME` file in the `docs/` directory with your domain

3. Deploy with `mkdocs gh-deploy`

## 🔍 Search and Navigation

### Search Features

- Full-text search across all pages
- Search suggestions
- Search result highlighting
- Keyboard shortcuts (Ctrl+K)

### Navigation

- Hierarchical navigation structure
- Breadcrumb navigation
- Previous/Next page navigation
- Table of contents for each page

## 📱 Responsive Design

The documentation is fully responsive and works on:

- Desktop computers
- Tablets
- Mobile phones
- Print media

## 🌙 Dark Mode

The documentation supports both light and dark modes:

- Automatic detection based on system preferences
- Manual toggle in the header
- Consistent styling across both themes

## 🔗 External Links

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)

## 🤝 Contributing to Documentation

We welcome contributions to improve the documentation:

1. **Report Issues**: Create an issue for documentation problems
2. **Suggest Improvements**: Propose new sections or improvements
3. **Submit Changes**: Create pull requests with documentation updates
4. **Review Changes**: Help review documentation pull requests

### Documentation Standards

- Write clear, concise content
- Use proper grammar and spelling
- Include code examples where appropriate
- Keep information up to date
- Follow the existing style guide

## 📄 License

The documentation is licensed under the same license as the project (MIT License).

---

For questions about the documentation, please:

- Check the [MkDocs documentation](https://www.mkdocs.org/)
- Review existing documentation for examples
- Create an issue for specific problems
- Contact the development team 

## 🏢 Enterprise Features

### SSO (Single Sign-On)
- Unterstützung für OIDC, SAML, OAuth2 (Google, Microsoft, etc.)
- SSO-Login, Callback und Account-Linking
- Just-in-Time-Provisionierung und Mapping von SSO-Attributen
- SSO-Konfigurationsanleitung im Deployment-Bereich

### Erweiterte RBAC
- Hierarchische Rollen (Super Admin, Admin, Manager, User, Guest)
- Gruppenbasierte Rechte und Bereichs-Admins
- Feingranulare Rechteverwaltung (z.B. auf Ressourcenebene)
- Admin-UI für Rollen, Rechte, Gruppen

### Security & Self-Service
- 2FA/MFA (TOTP, WebAuthn)
- Self-Service-UI für User (API-Token, 2FA, Account-Löschung)
- Bulk-Import/-Export von Usern/Rollen
- DSGVO-Features (Datenexport, Account-Löschung)

### Audit-Log
- Audit-Log-API und UI für Admins
- Logging aller sicherheitsrelevanten Events (Login, SSO, Rollenänderungen) 