import React from 'react';

export const TrustProblemSection: React.FC = () => {
  return (
    <section className="hairline-top hairline-bottom" style={{ backgroundColor: 'var(--color-bg)', padding: '5.5rem 0' }}>
      <div className="container">
        {/* Eyebrow & Core Message */}
        <div style={{ maxWidth: '840px', marginBottom: '4rem' }}>
          <div className="eyebrow">
            FOR INDIAN MSMES
          </div>
          
          <h2
            style={{
              fontSize: 'clamp(2rem, 3.8vw, 3.25rem)',
              lineHeight: 1.15,
              marginBottom: '1.5rem',
              color: 'var(--color-black)',
              letterSpacing: '-0.02em'
            }}
          >
            Compliance is not just about knowing the rules.<br />
            <span style={{ color: 'var(--color-brick)' }}>It's about knowing which rules apply to you.</span>
          </h2>

          <p style={{ fontSize: '1.1875rem', lineHeight: 1.7, color: 'var(--color-muted)' }}>
            Multiple regulations, changing requirements and recurring deadlines can make compliance difficult for businesses without dedicated compliance teams.
          </p>
        </div>

        {/* 3 Metric Points */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2.5rem',
            paddingTop: '2.5rem',
            borderTop: '1px solid var(--color-border)'
          }}
          className="metric-grid"
        >
          {/* Stat 1 */}
          <div>
            <div
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                color: 'var(--color-black)',
                lineHeight: 1,
                marginBottom: '0.6rem'
              }}
            >
              6.3+ <span style={{ fontSize: '1.75rem', fontFamily: 'var(--font-sans)', fontWeight: 600, color: 'var(--color-brick)' }}>CRORE</span>
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.35rem' }}>
              Indian MSMEs
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', lineHeight: 1.5 }}>
              Operating across manufacturing, services, trade, and software without in-house legal departments.
            </p>
          </div>

          {/* Stat 2 */}
          <div>
            <div
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                color: 'var(--color-black)',
                lineHeight: 1,
                marginBottom: '0.6rem'
              }}
            >
              MULTIPLE
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.35rem' }}>
              Recurring obligations
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', lineHeight: 1.5 }}>
              Spanning GST, PF, ESI, TDS, Companies Act, and MSMED Act filings every month and quarter.
            </p>
          </div>

          {/* Stat 3 */}
          <div>
            <div
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                color: 'var(--color-brick)',
                lineHeight: 1,
                marginBottom: '0.6rem'
              }}
            >
              ONE
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.35rem' }}>
              Personalized compliance view
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', lineHeight: 1.5 }}>
              Clauz X filters the noise and shows only the exact statutory mandates relevant to your entity.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 800px) {
          .metric-grid {
            grid-template-columns: 1fr !important;
            gap: 2rem !important;
          }
        }
      `}</style>
    </section>
  );
};
