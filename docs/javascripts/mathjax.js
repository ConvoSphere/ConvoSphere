// MathJax Configuration for AI Chat Application Documentation
// This file configures MathJax for rendering mathematical expressions

window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true,
    packages: ['base', 'ams', 'noerrors', 'noundefined']
  },
  options: {
    ignoreHtmlClass: 'tex2jax_ignore',
    processHtmlClass: 'tex2jax_process',
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  },
  startup: {
    pageReady: () => {
      console.log('MathJax is loaded and ready');
    }
  },
  chtml: {
    displayAlign: 'left',
    displayIndent: '2em',
    minScale: 0.5,
    maxScale: 10,
    scale: 1,
    mtextInheritFont: true
  }
};

// Custom function to render math expressions
function renderMath() {
  if (window.MathJax) {
    MathJax.typesetPromise();
  }
}

// Re-render math when content changes (for dynamic content)
document.addEventListener('DOMContentLoaded', function() {
  // Initial render
  renderMath();
  
  // Re-render when navigation changes (for SPA-like behavior)
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList') {
        // Check if new math content was added
        const mathElements = mutation.target.querySelectorAll('.math, [class*="math"]');
        if (mathElements.length > 0) {
          renderMath();
        }
      }
    });
  });
  
  // Observe the main content area
  const contentArea = document.querySelector('.md-content');
  if (contentArea) {
    observer.observe(contentArea, {
      childList: true,
      subtree: true
    });
  }
});

// Export for use in other scripts
window.renderMath = renderMath; 