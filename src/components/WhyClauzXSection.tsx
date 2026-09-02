import React from 'react';

export const WhyClauzXSection: React.FC = () => {
  return (
    <section id="why-clauz-x" className="bg-brick section-padding" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Decorative fine background pattern */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.04) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          pointerEvents: 'none',
          zIndex: 0
        }}
      />

      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        {/* Section Header */}
        <div style={{ maxWidth: '720px', marginBottom: '5rem' }}>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.14em',
              color: 'var(--color-beige)',
              marginBottom: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <span style={{ width: '6px', height: '6px', backgroundColor: 'var(--color-beige)', borderRadius: '50%' }} />
            OUR CORE PILLARS
          </div>

          <h2
            style={{
              fontSize: 'clamp(2.5rem, 5vw, 4.25rem)',
              lineHeight: 1.05,
              color: '#FFFFFF',
              letterSpacing: '-0.02em'
            }}
          >
            Built around three things.
          </h2>
        </div>

        {/* 3 Large Columns with bold serif numbers and typography */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '3.5rem',
            paddingTop: '3rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.2)'
          }}
          className="why-grid"
        >
          {/* Column 01 */}
          <div>
            <span
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(3rem, 5vw, 4.5rem)',
                color: 'var(--color-beige)',
                lineHeight: 1,
                display: 'block',
                marginBottom: '1.5rem',
                fontWeight: 400
              }}
            >
              01
            </span>
            <h3
              style={{
                fontSize: '1.75rem',
                color: '#FFFFFF',
                marginBottom: '1rem',
                letterSpacing: '-0.01em'
              }}
            >
              PERSONALIZED
            </h3>
            <p style={{ fontSize: '1.125rem', color: 'rgba(255, 255, 255, 0.85)', lineHeight: 1.65 }}>
              Your compliance view starts with your business. No generic checklist fatigue — only the exact statutory rules that govern your entity.
            </p>
          </div>

          {/* Column 02 */}
          <div>
            <span
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(3rem, 5vw, 4.5rem)',
                color: 'var(--color-beige)',
                lineHeight: 1,
                display: 'block',
                marginBottom: '1.5rem',
                fontWeight: 400
              }}
            >
              02
            </span>
            <h3
              style={{
                fontSize: '1.75rem',
                color: '#FFFFFF',
                marginBottom: '1rem',
                letterSpacing: '-0.01em'
              }}
            >
              GROUNDED
            </h3>
            <p style={{ fontSize: '1.125rem', color: 'rgba(255, 255, 255, 0.85)', lineHeight: 1.65 }}>
              Compliance answers are directly connected to relevant regulatory sources, Gazette notifications, and statutory sections. Zero hallucinated advice.
            </p>
          </div>

          {/* Column 03 */}
          <div>
            <span
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(3rem, 5vw, 4.5rem)',
                color: 'var(--color-beige)',
                lineHeight: 1,
                display: 'block',
                marginBottom: '1.5rem',
                fontWeight: 400
              }}
            >
              03
            </span>
            <h3
              style={{
                fontSize: '1.75rem',
                color: '#FFFFFF',
                marginBottom: '1rem',
                letterSpacing: '-0.01em'
              }}
            >
              AUDITABLE
            </h3>
            <p style={{ fontSize: '1.125rem', color: 'rgba(255, 255, 255, 0.85)', lineHeight: 1.65 }}>
              Important actions can be traced, timestamped, and reviewed. Deliver verifiable proof of due diligence to auditors, boards, and banking partners.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 860px) {
          .why-grid {
            grid-template-columns: 1fr !important;
            gap: 3rem !important;
          }
        }
      `}</style>
    </section>
  );
};
