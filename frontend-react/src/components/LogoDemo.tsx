import React from "react";
import { Logo } from "./Logo";
import { LogoWithText } from "./LogoWithText";
import "./Logo.css";

export const LogoDemo: React.FC = () => {
  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>ConvoSphere Logo Collection</h1>

      <section style={{ marginBottom: "3rem" }}>
        <h2>Logo Variants</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "2rem",
          }}
        >
          <div
            style={{
              textAlign: "center",
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Main Logo</h3>
            <Logo variant="main" />
            <p>Standard version with full animation</p>
          </div>

          <div
            style={{
              textAlign: "center",
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Text Logo</h3>
            <Logo variant="text" />
            <p>With integrated text and tagline</p>
          </div>

          <div
            style={{
              textAlign: "center",
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Icon Logo</h3>
            <Logo variant="icon" />
            <p>Compact version for UI elements</p>
          </div>

          <div
            style={{
              textAlign: "center",
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Minimal Logo</h3>
            <Logo variant="minimal" />
            <p>Favicon and small applications</p>
          </div>
        </div>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2>Logo with Text Components</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
            gap: "2rem",
          }}
        >
          <div
            style={{
              textAlign: "center",
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Horizontal Layout</h3>
            <LogoWithText layout="horizontal" />
            <p>Ideal for navigation headers</p>
          </div>

          <div
            style={{
              textAlign: "center",
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Vertical Layout</h3>
            <LogoWithText layout="vertical" />
            <p>Perfect for landing pages</p>
          </div>
        </div>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2>Size Variations</h2>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "1rem",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ textAlign: "center" }}>
            <Logo variant="icon" size={32} />
            <p>32px</p>
          </div>
          <div style={{ textAlign: "center" }}>
            <Logo variant="icon" size={48} />
            <p>48px</p>
          </div>
          <div style={{ textAlign: "center" }}>
            <Logo variant="icon" size={64} />
            <p>64px</p>
          </div>
          <div style={{ textAlign: "center" }}>
            <Logo variant="icon" size={96} />
            <p>96px</p>
          </div>
          <div style={{ textAlign: "center" }}>
            <Logo variant="icon" size={128} />
            <p>128px</p>
          </div>
        </div>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2>Theme Adaptation</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "2rem",
          }}
        >
          <div
            style={{
              textAlign: "center",
              padding: "2rem",
              backgroundColor: "#F7F9FB",
              borderRadius: "8px",
              border: "1px solid #eee",
            }}
          >
            <h3>Light Theme</h3>
            <Logo variant="main" size={120} />
            <p>Optimized for light backgrounds</p>
          </div>

          <div
            style={{
              textAlign: "center",
              padding: "2rem",
              backgroundColor: "#23224A",
              borderRadius: "8px",
              border: "1px solid #1A1A33",
            }}
          >
            <h3 style={{ color: "#F7F9FB" }}>Dark Theme</h3>
            <Logo variant="main" size={120} />
            <p style={{ color: "#F7F9FB" }}>Enhanced for dark backgrounds</p>
          </div>
        </div>
      </section>

      <section style={{ marginBottom: "3rem" }}>
        <h2>Usage Examples</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "2rem",
          }}
        >
          <div
            style={{
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Header Navigation</h3>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "1rem",
              }}
            >
              <LogoWithText layout="horizontal" showTagline={false} />
              <nav>
                <a
                  href="#"
                  style={{
                    marginLeft: "1rem",
                    textDecoration: "none",
                    color: "#23224A",
                  }}
                >
                  Home
                </a>
                <a
                  href="#"
                  style={{
                    marginLeft: "1rem",
                    textDecoration: "none",
                    color: "#23224A",
                  }}
                >
                  Chat
                </a>
                <a
                  href="#"
                  style={{
                    marginLeft: "1rem",
                    textDecoration: "none",
                    color: "#23224A",
                  }}
                >
                  Settings
                </a>
              </nav>
            </div>
          </div>

          <div
            style={{
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Loading State</h3>
            <div style={{ textAlign: "center" }}>
              <Logo variant="main" size={100} className="loading" />
              <p>Loading...</p>
            </div>
          </div>

          <div
            style={{
              padding: "1rem",
              border: "1px solid #eee",
              borderRadius: "8px",
            }}
          >
            <h3>Button Integration</h3>
            <button
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                padding: "0.75rem 1rem",
                border: "1px solid #5BC6E8",
                borderRadius: "6px",
                backgroundColor: "transparent",
                cursor: "pointer",
              }}
            >
              <Logo variant="icon" size={24} />
              Start Chat
            </button>
          </div>
        </div>
      </section>

      <section>
        <h2>Technical Information</h2>
        <div
          style={{
            backgroundColor: "#f5f5f5",
            padding: "1rem",
            borderRadius: "8px",
          }}
        >
          <h3>Features:</h3>
          <ul>
            <li>✅ Fully scalable SVG graphics</li>
            <li>✅ Smooth animations with SMIL</li>
            <li>✅ Theme-aware (light/dark mode)</li>
            <li>✅ Responsive design</li>
            <li>✅ Accessibility support</li>
            <li>✅ Reduced motion support</li>
            <li>✅ High contrast mode support</li>
            <li>✅ Print-friendly styles</li>
          </ul>

          <h3>File Sizes:</h3>
          <ul>
            <li>Main Logo: ~4.2KB</li>
            <li>Text Logo: ~5.1KB</li>
            <li>Icon Logo: ~3.8KB</li>
            <li>Minimal Logo: ~2.9KB</li>
            <li>Dark Theme: ~4.5KB</li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default LogoDemo;
