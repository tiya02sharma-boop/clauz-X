import React from 'react';

interface FooterProps {
  onNavigateSection: (id: string) => void;
  onGetStarted: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigateSection, onGetStarted }) => {
  return (
    <footer style={{ backgroundColor: 'var(--color-bg)', borderTop: '1px solid var(--color-border)', padding: '5rem 0 3rem' }}>
      <div className="container">
        
        {/* Top Footer Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr 1fr 1fr',
            gap: '3.5rem',
            paddingBottom: '4rem',
            borderBottom: '1px solid var(--color-border)'
          }}
          className="footer-grid"
        >
          {/* Brand Column */}
          <div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem', marginBottom: '1rem' }}>
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.03em', color: 'var(--color-black)' }}>
                CLAUZ
              </span>
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-brick)' }}>
                X
              </span>
            </div>

            <p style={{ fontSize: '1rem', color: 'var(--color-black)', fontFamily: 'var(--font-serif)', fontStyle: 'italic', marginBottom: '1rem' }}>
              "Compliance, simplified."
            </p>

            <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', maxWidth: '340px', lineHeight: 1.6 }}>
              The modern regulatory intelligence and obligation mapping platform built exclusively for Indian small and medium enterprises.
            </p>
          </div>

          {/* Navigation Column */}
          <div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-brick)', marginBottom: '1.25rem', letterSpacing: '0.08em' }}>
              Product
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button onClick={() => onNavigateSection('product-preview')} style={footerLinkBtnStyle}>Overview</button>
              <button onClick={() => onNavigateSection('features')} style={footerLinkBtnStyle}>Applicability Engine</button>
              <button onClick={() => onNavigateSection('features')} style={footerLinkBtnStyle}>Compliance Calendar</button>
              <button onClick={() => onNavigateSection('features')} style={footerLinkBtnStyle}>Ask Clauz X</button>
              <button onClick={() => onNavigateSection('features')} style={footerLinkBtnStyle}>WhatsApp Reminders</button>
            </div>
          </div>

          {/* How It Works & Company */}
          <div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-brick)', marginBottom: '1.25rem', letterSpacing: '0.08em' }}>
              Platform
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button onClick={() => onNavigateSection('how-it-works')} style={footerLinkBtnStyle}>How It Works</button>
              <button onClick={() => onNavigateSection('why-clauz-x')} style={footerLinkBtnStyle}>Why Clauz X</button>
              <button onClick={onGetStarted} style={footerLinkBtnStyle}>Interactive MSME Demo</button>
              <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>India Regulatory Coverage</span>
            </div>
          </div>

          {/* Legal Column */}
          <div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-brick)', marginBottom: '1.25rem', letterSpacing: '0.08em' }}>
              Legal & Trust
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', color: 'var(--color-muted)' }}>
              <span style={{ cursor: 'pointer' }}>Privacy Policy</span>
              <span style={{ cursor: 'pointer' }}>Terms of Service</span>
              <span style={{ cursor: 'pointer' }}>Security & Data Encryption</span>
              <span style={{ cursor: 'pointer' }}>Statutory Disclaimer</span>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div
          style={{
            paddingTop: '2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            fontSize: '0.8125rem',
            color: 'var(--color-muted)',
            fontFamily: 'var(--font-mono)'
          }}
        >
          <div>
            © 2026 Clauz X Technologies India Pvt Ltd. All rights reserved.
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <span>Made with precision for Indian Enterprises</span>
            <span style={{ color: 'var(--color-brick)' }}>●</span>
            <span>CIN: U72900MH2026PTC402918</span>
          </div>
        </div>

      </div>

      <style>{`
        @media (max-width: 860px) {
          .footer-grid {
            grid-template-columns: 1fr 1fr !important;
            gap: 2.5rem !important;
          }
        }
        @media (max-width: 540px) {
          .footer-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </footer>
  );
};

const footerLinkBtnStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  textAlign: 'left',
  padding: 0,
  fontSize: '0.875rem',
  color: 'var(--color-muted)',
  cursor: 'pointer',
  fontFamily: 'var(--font-sans)',
  transition: 'color var(--transition-fast)'
};
