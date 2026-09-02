import React from 'react';
import { ArrowRight, Shield } from 'lucide-react';

interface FinalCTASectionProps {
  onGetStarted: () => void;
}

export const FinalCTASection: React.FC<FinalCTASectionProps> = ({ onGetStarted }) => {
  return (
    <section className="bg-black section-padding" style={{ position: 'relative', overflow: 'hidden' }}>
      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ maxWidth: '820px', margin: '0 auto', textAlign: 'center' }}>
          
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.14em',
              color: 'var(--color-beige)',
              marginBottom: '1.5rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: 'rgba(233, 201, 149, 0.1)',
              padding: '0.35rem 0.85rem',
              borderRadius: '999px',
              border: '1px solid rgba(233, 201, 149, 0.2)'
            }}
          >
            <Shield size={14} className="text-beige" />
            GET STARTED IN MINUTES
          </div>

          <h2
            style={{
              fontSize: 'clamp(2.5rem, 5.5vw, 4.5rem)',
              lineHeight: 1.08,
              color: 'var(--color-bg)',
              letterSpacing: '-0.02em',
              marginBottom: '1.5rem'
            }}
          >
            Know what applies.<br />
            <span style={{ color: 'var(--color-beige)' }}>Stay ahead of what's due.</span>
          </h2>

          <p
            style={{
              fontSize: '1.1875rem',
              color: '#A39E96',
              lineHeight: 1.7,
              maxWidth: '620px',
              margin: '0 auto 2.5rem'
            }}
          >
            Start with your business profile and see how Clauz X can organize your compliance journey with zero legal complexity.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <button
              onClick={onGetStarted}
              className="btn btn-brick"
              style={{
                padding: '1.1rem 2.75rem',
                fontSize: '1.0625rem',
                backgroundColor: 'var(--color-brick)'
              }}
            >
              Get Started <ArrowRight size={18} />
            </button>

            <span style={{ fontSize: '0.875rem', color: '#827D75', fontFamily: 'var(--font-mono)' }}>
              Built specifically for Indian MSMEs. No credit card required.
            </span>
          </div>

        </div>
      </div>
    </section>
  );
};
