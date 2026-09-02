import React from 'react';
import { UserCheck, Calculator, Building } from 'lucide-react';

export const WhoIsItForSection: React.FC = () => {
  const audiences = [
    {
      title: 'MSME OWNERS',
      icon: UserCheck,
      description: 'Understand what needs to be done without navigating compliance complexity alone.',
      points: [
        'Eliminate fear of sudden statutory notices & penalties',
        'Know exact deadlines without wading through legal jargon',
        'Focus on growing core revenue and operations'
      ]
    },
    {
      title: 'ACCOUNTANTS & CAs',
      icon: Calculator,
      description: 'Manage obligations, deadlines and documentation across client businesses with structured clarity.',
      points: [
        'Single unified forward-looking calendar for multi-entity clients',
        'Auto-drafted Form MSME-1 and routine secretarial resolutions',
        'Speed up month-end reconciliation and client communication'
      ]
    },
    {
      title: 'COMPLIANCE TEAMS',
      icon: Building,
      description: 'Keep compliance activity organized, auditable and completely traceable across growing teams.',
      points: [
        'Centralized repository with timestamped audit trail',
        'Instant legal source verification for internal queries',
        'Proactive WhatsApp and email escalation schedules'
      ]
    }
  ];

  return (
    <section className="section-padding hairline-top" style={{ backgroundColor: 'var(--color-bg)' }}>
      <div className="container">
        {/* Header */}
        <div style={{ maxWidth: '640px', marginBottom: '4.5rem' }}>
          <div className="eyebrow">
            BUILT FOR INDIAN ENTERPRISES
          </div>
          <h2
            style={{
              fontSize: 'clamp(2.25rem, 4.2vw, 3.5rem)',
              lineHeight: 1.1,
              color: 'var(--color-black)',
              letterSpacing: '-0.02em',
              marginBottom: '1rem'
            }}
          >
            Made for the people<br />
            <span className="text-brick">keeping businesses moving.</span>
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-muted)' }}>
            Whether you are a solo founder or managing finance across five operating entities, Clauz X simplifies your statutory workflow.
          </p>
        </div>

        {/* 3 Audience Blocks */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2rem'
          }}
          className="audience-grid"
        >
          {audiences.map((aud, index) => {
            const IconComp = aud.icon;
            return (
              <div
                key={index}
                style={{
                  backgroundColor: 'var(--color-card-bg)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '2.5rem 2rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  transition: 'all 0.3s ease'
                }}
                className="audience-card"
              >
                <div>
                  <div style={{ width: '48px', height: '48px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', color: 'var(--color-brick)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.75rem' }}>
                    <IconComp size={24} />
                  </div>

                  <h3 style={{ fontSize: '1.35rem', color: 'var(--color-black)', letterSpacing: '-0.01em', marginBottom: '1rem' }}>
                    {aud.title}
                  </h3>

                  <p style={{ fontSize: '0.9375rem', color: 'var(--color-muted)', lineHeight: 1.65, marginBottom: '2rem' }}>
                    {aud.description}
                  </p>
                </div>

                <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {aud.points.map((pt, pIdx) => (
                    <div key={pIdx} style={{ fontSize: '0.8125rem', color: 'var(--color-black)', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--color-brick)', fontWeight: 700 }}>•</span>
                      <span>{pt}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        .audience-card:hover {
          transform: translateY(-3px);
          box-shadow: var(--shadow-card);
          border-color: rgba(0, 0, 0, 0.25);
        }
        @media (max-width: 900px) {
          .audience-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};
