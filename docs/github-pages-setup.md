# GitHub Pages Setup Guide

This guide explains how to set up and configure GitHub Pages for the AI Chat Application documentation.

## Overview

The documentation is automatically built and deployed to GitHub Pages using GitHub Actions. The setup includes:

- **Automatic builds** on push to main branch
- **MkDocs with Material theme** for modern documentation
- **Mermaid diagrams** for architecture visualization
- **Responsive design** for all devices
- **Search functionality** across all pages

## Repository Configuration

### 1. GitHub Pages Settings

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Configure the following settings:

```
Source: Deploy from a branch
Branch: gh-pages
Folder: / (root)
```

4. Click **Save**

### 2. Repository Permissions

Ensure the following permissions are set:

- **Actions**: Read and write permissions
- **Pages**: Read and write permissions
- **Contents**: Read permissions

## Workflow Configuration

The GitHub Actions workflow (`.github/workflows/docs.yml`) handles:

### Build Process

1. **Checkout**: Fetches the repository with full history
2. **Python Setup**: Uses Python 3.11 with pip caching
3. **System Dependencies**: Installs OpenGL libraries for `materialx`
4. **Python Dependencies**: Installs all MkDocs dependencies
5. **Build**: Runs `mkdocs build --strict`
6. **Deploy**: Uploads to GitHub Pages

### Trigger Conditions

The workflow triggers on:

- Push to `main` or `master` branch
- Changes to `docs/`, `mkdocs.yml`, or workflow files
- Manual trigger via `workflow_dispatch`

## Configuration Files

### mkdocs.yml

Key GitHub Pages specific settings:

```yaml
site_url: https://lichtbaer.github.io/ai-chat-app/
repo_name: lichtbaer/ai-chat-app
repo_url: https://github.com/lichtbaer/ai-chat-app
edit_uri: edit/main/docs/
```

### .nojekyll

Prevents Jekyll from processing the site:

```
# This file tells GitHub Pages not to process the site with Jekyll
```

### CNAME (Optional)

For custom domains:

```
your-domain.com
```

## Troubleshooting

### Common Issues

#### 1. Build Failures

**Problem**: GitHub Actions build fails
**Solution**: Check the workflow logs for specific errors

```bash
# Common fixes:
# - Update Python version in workflow
# - Check dependency versions
# - Verify file paths
```

#### 2. OpenGL Dependencies

**Problem**: `materialx` build fails
**Solution**: The workflow includes system dependencies:

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev
```

#### 3. Missing Files

**Problem**: 404 errors on GitHub Pages
**Solution**: Ensure all files are committed and the build succeeds

#### 4. Jekyll Processing

**Problem**: Jekyll processes the site incorrectly
**Solution**: Ensure `.nojekyll` file is present in the `docs/` directory

### Debugging Steps

1. **Check Workflow Logs**:
   - Go to **Actions** tab in GitHub
   - Click on the latest workflow run
   - Review build logs for errors

2. **Test Locally**:
   ```bash
   # Install dependencies
   pip install -r docs/requirements-docs.txt
   
   # Build locally
   mkdocs build
   
   # Check for errors
   mkdocs build --strict
   ```

3. **Verify Configuration**:
   ```bash
   # Validate mkdocs.yml
   mkdocs build --strict
   
   # Check for missing files
   mkdocs build --verbose
   ```

## Performance Optimization

### Build Optimization

1. **Dependency Caching**: The workflow uses pip caching
2. **Selective Triggers**: Only builds on relevant changes
3. **Concurrent Deployments**: Prevents deployment conflicts

### Site Optimization

1. **Minification**: Enabled via `mkdocs-minify-plugin`
2. **Image Optimization**: Use optimized images
3. **Code Highlighting**: Pygments for syntax highlighting

## Security Considerations

### Repository Security

1. **Branch Protection**: Protect the main branch
2. **Required Reviews**: Require PR reviews for documentation changes
3. **Dependency Scanning**: Regularly update dependencies

### Content Security

1. **No Sensitive Data**: Never commit API keys or secrets
2. **Public Content**: All documentation is public
3. **External Links**: Verify all external links

## Monitoring

### Build Status

Monitor build status via:

- GitHub Actions dashboard
- Repository badges
- Email notifications (if configured)

### Site Analytics

Optional analytics via Google Analytics:

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## Customization

### Theme Customization

Custom styles in `docs/stylesheets/extra.css`:

```css
:root {
  --md-primary-fg-color: #3f51b5;
  --md-primary-fg-color--light: #757de8;
  --md-primary-fg-color--dark: #002984;
}
```

### Navigation

Customize navigation in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Getting Started:
    - Quick Start: getting-started/quick-start.md
    - Installation: getting-started/installation.md
```

## Best Practices

### Documentation Standards

1. **Consistent Structure**: Follow established patterns
2. **Clear Navigation**: Logical page organization
3. **Regular Updates**: Keep documentation current
4. **Code Examples**: Include working code samples

### Maintenance

1. **Regular Reviews**: Monthly documentation reviews
2. **Dependency Updates**: Keep dependencies current
3. **Link Validation**: Check external links regularly
4. **Performance Monitoring**: Monitor site performance

## Support

For issues with GitHub Pages setup:

1. Check [GitHub Pages documentation](https://docs.github.com/en/pages)
2. Review [MkDocs documentation](https://www.mkdocs.org/)
3. Check workflow logs for specific errors
4. Create an issue in the repository

## Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)