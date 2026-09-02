import React from 'react';
import { ArrowRight, ArrowDown, Building2, ShieldCheck, Clock, CheckCircle2, FileText } from 'lucide-react';

interface HeroSectionProps {
  onGetStarted: () => void;
  onExplore: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onGetStarted, onExplore }) => {
  return (
    <section style={{ position: 'relative', paddingTop: '3.5rem', paddingBottom: '6rem', overflow: 'hidden' }}>
      {/* Subtle background hairline grid */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            linear-gradient(to right, rgba(0, 0, 0, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 0, 0, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px',
          pointerEvents: 'none',
          zIndex: 0
        }}
      />

      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '4rem', alignItems: 'center' }} className="hero-grid">
          {/* Left Hero Content */}
          <div>
            <div className="eyebrow">
              REGULATORY INTELLIGENCE FOR MSMES
            </div>

            <h1
              style={{
                fontSize: 'clamp(3rem, 6vw, 5.25rem)',
                lineHeight: 1.05,
                marginBottom: '1.75rem',
                color: 'var(--color-black)',
                letterSpacing: '-0.03em'
              }}
            >
              Compliance,<br />
              <span className="text-brick">simplified.</span>
            </h1>

            <p
              style={{
                fontFamily: 'var(--font-serif)',
                fontSize: 'clamp(1.25rem, 2.2vw, 1.625rem)',
                color: 'var(--color-black)',
                lineHeight: 1.3,
                marginBottom: '1.25rem',
                letterSpacing: '-0.01em'
              }}
            >
              Know what applies. <br className="hidden-mobile" />
              Never miss a deadline.
            </p>

            <p
              style={{
                fontSize: '1.0625rem',
                color: 'var(--color-muted)',
                lineHeight: 1.7,
                maxWidth: '540px',
                marginBottom: '2.5rem'
              }}
            >
              Clauz X helps Indian MSMEs understand the compliance obligations that apply to their business,
              stay ahead of deadlines, receive proactive WhatsApp alerts and ask compliance questions — all from one place.
            </p>

            {/* Action Buttons */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
              <button
                onClick={onGetStarted}
                className="btn btn-brick"
                style={{ padding: '0.95rem 2rem', fontSize: '1rem' }}
              >
                Get Started <ArrowRight size={18} />
              </button>
              <button
                onClick={onExplore}
                className="btn btn-secondary"
                style={{ padding: '0.95rem 1.75rem', fontSize: '1rem' }}
              >
                Explore Clauz X <ArrowDown size={16} />
              </button>
            </div>

            {/* Micro-trust indicator */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '2.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--color-muted)' }}>
                <ShieldCheck size={16} className="text-brick" />
                <span>Companies Act & GST Aligned</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--color-muted)' }}>
                <CheckCircle2 size={16} className="text-brick" />
                <span>Zero Dashboard Clutter</span>
              </div>
            </div>
          </div>

          {/* Right Hero Visual: Abstract Editorial Compliance Illustration */}
          <div style={{ position: 'relative' }}>
            <div
              style={{
                backgroundColor: 'var(--color-card-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: '2.5rem 2rem',
                boxShadow: 'var(--shadow-card)',
                position: 'relative'
              }}
            >
              {/* Header tag */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--color-border)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-muted)' }}>
                  COMPLIANCE APPLICABILITY ENGINE
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', color: 'var(--color-brick)', fontWeight: 600 }}>
                  ACTIVE MAPPING
                </span>
              </div>

              {/* Central Visual Architecture Diagram */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', position: 'relative' }}>
                
                {/* Node 1: Business Profile */}
                <div
                  style={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1.1rem 1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.03)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                      <Building2 size={18} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>Business Profile</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>Pvt Ltd • ₹12 Cr Turnover • 35 Staff</div>
                    </div>
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '3px' }}>
                    INPUT
                  </span>
                </div>

                {/* Connecting Vector Down */}
                <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.4rem 0' }}>
                  <div style={{ width: '1px', height: '20px', backgroundColor: 'var(--color-brick)' }} />
                </div>

                {/* Node 2: Applicable Obligations with surrounding labels */}
                <div
                  style={{
                    backgroundColor: 'var(--color-brick)',
                    color: '#FFFFFF',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1.25rem 1.25rem',
                    boxShadow: '0 8px 24px rgba(158, 23, 25, 0.25)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <ShieldCheck size={18} />
                      <span style={{ fontSize: '0.9375rem', fontWeight: 700, letterSpacing: '0.01em' }}>Applicable Obligations</span>
                    </div>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', backgroundColor: 'rgba(255,255,255,0.2)', padding: '0.2rem 0.5rem', borderRadius: '3px' }}>
                      12 IDENTIFIED
                    </span>
                  </div>

                  {/* Connected pill tags */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {['GST (GSTR-3B)', 'PF / ECR', 'ESI Monthly', 'MSME-1 Form', 'TDS Challan 281', 'DIR-3 KYC'].map((tag, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: '0.75rem',
                          padding: '0.25rem 0.6rem',
                          backgroundColor: 'rgba(255, 255, 255, 0.15)',
                          border: '1px solid rgba(255, 255, 255, 0.25)',
                          borderRadius: '3px',
                          fontWeight: 500
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Connecting Vector Down */}
                <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.4rem 0' }}>
                  <div style={{ width: '1px', height: '20px', backgroundColor: 'var(--color-brick)' }} />
                </div>

                {/* Node 3: Deadlines */}
                <div
                  style={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1.1rem 1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.03)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '4px', backgroundColor: 'var(--color-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-brick)' }}>
                      <Clock size={18} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>Upcoming Deadlines</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-brick)', fontWeight: 600 }}>Next: GSTR-3B in 3 days • ESI in 8 days</div>
                    </div>
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: 'var(--color-brick-light)', color: 'var(--color-brick)', border: '1px solid var(--color-border-brick)', borderRadius: '3px', fontWeight: 600 }}>
                    SCHEDULED
                  </span>
                </div>

                {/* Connecting Vector Down */}
                <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.4rem 0' }}>
                  <div style={{ width: '1px', height: '20px', backgroundColor: 'var(--color-black)' }} />
                </div>

                {/* Node 4: Action */}
                <div
                  style={{
                    backgroundColor: 'var(--color-beige)',
                    border: '1px solid var(--color-beige-dark)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1.1rem 1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '4px', backgroundColor: 'rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                      <FileText size={18} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>Immediate Action</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-black)' }}>Auto-draft form • Plain language Q&A • Audit log</div>
                    </div>
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: '#FFFFFF', border: '1px solid rgba(0,0,0,0.15)', borderRadius: '3px', fontWeight: 600 }}>
                    RESOLVED
                  </span>
                </div>

              </div>
            </div>

            {/* Decorative background accent */}
            <div
              style={{
                position: 'absolute',
                top: '-12px',
                right: '-12px',
                width: '100%',
                height: '100%',
                border: '1px dashed var(--color-brick)',
                borderRadius: 'var(--radius-md)',
                zIndex: -1,
                opacity: 0.3
              }}
            />
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 960px) {
          .hero-grid {
            grid-template-columns: 1fr !important;
            gap: 3rem !important;
          }
          .hidden-mobile {
            display: none !important;
          }
        }
      `}</style>
    </section>
  );
};
