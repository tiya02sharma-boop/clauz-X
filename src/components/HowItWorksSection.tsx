import React, { useState } from 'react';
import { Building2, CheckSquare, Bell, FileCheck } from 'lucide-react';

export const HowItWorksSection: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      num: '01',
      title: 'Tell us about your business',
      description: 'Share your turnover, headcount, sector, state and entity type in under 2 minutes.',
      icon: Building2,
      detail: 'Calculates applicable exemptions & specific threshold triggers instantly.'
    },
    {
      num: '02',
      title: 'Know what applies',
      description: 'Clauz X identifies the exact statutory obligations relevant to your business profile.',
      icon: CheckSquare,
      detail: 'No generic lists. Filtered by Central Acts, State Labor Laws, and MCA mandates.'
    },
    {
      num: '03',
      title: 'Stay ahead',
      description: 'See upcoming deadlines and receive proactive reminders well before due dates.',
      icon: Bell,
      detail: 'T-7, T-3, and T-1 multi-channel alerts over WhatsApp and email.'
    },
    {
      num: '04',
      title: 'Take action',
      description: 'Ask compliance questions, verify statutory rules and track all deadlines.',
      icon: FileCheck,
      detail: 'Grounded AI regulatory assistant with verifiable legal source citations.'
    }
  ];

  return (
    <section id="how-it-works" className="section-padding hairline-top hairline-bottom" style={{ backgroundColor: 'var(--color-bg)' }}>
      <div className="container">
        {/* Header */}
        <div style={{ maxWidth: '640px', marginBottom: '4rem' }}>
          <div className="eyebrow">
            STEP-BY-STEP WORKFLOW
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
            From business profile<br />
            <span className="text-brick">to compliance clarity.</span>
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-muted)' }}>
            A streamlined 4-step journey engineered to remove legal friction for busy founders and operators.
          </p>
        </div>

        {/* 4-Step Horizontal Layout */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '1.5rem'
          }}
          className="steps-grid"
        >
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            const isSelected = activeStep === index;
            return (
              <div
                key={index}
                onClick={() => setActiveStep(index)}
                style={{
                  backgroundColor: isSelected ? '#FAF5ED' : 'var(--color-card-bg)',
                  border: isSelected ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '2.25rem 1.75rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  minHeight: '380px',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                  boxShadow: isSelected ? '0 12px 30px rgba(158, 23, 25, 0.12)' : 'none',
                  transform: isSelected ? 'translateY(-4px)' : 'none'
                }}
                className="step-card"
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.75rem' }}>
                    <span
                      style={{
                        fontFamily: 'var(--font-serif)',
                        fontSize: '2.25rem',
                        color: isSelected ? 'var(--color-brick)' : 'var(--color-black)',
                        fontWeight: 400
                      }}
                    >
                      {step.num}
                    </span>
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        backgroundColor: isSelected ? 'var(--color-brick-light)' : 'var(--color-bg)',
                        color: isSelected ? 'var(--color-brick)' : 'var(--color-black)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <IconComponent size={20} />
                    </div>
                  </div>

                  <h3
                    style={{
                      fontSize: '1.35rem',
                      lineHeight: 1.25,
                      marginBottom: '0.85rem',
                      color: 'var(--color-black)',
                      letterSpacing: '-0.01em'
                    }}
                  >
                    {step.title}
                  </h3>

                  <p style={{ fontSize: '0.9375rem', color: 'var(--color-muted)', lineHeight: 1.6 }}>
                    {step.description}
                  </p>
                </div>

                <div
                  style={{
                    paddingTop: '1.5rem',
                    borderTop: '1px solid var(--color-border)',
                    fontSize: '0.8125rem',
                    color: isSelected ? 'var(--color-brick)' : 'var(--color-muted)',
                    fontFamily: 'var(--font-mono)'
                  }}
                >
                  ✓ {step.detail}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        .step-card:hover {
          border-color: var(--color-brick) !important;
        }
        @media (max-width: 990px) {
          .steps-grid {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }
        @media (max-width: 600px) {
          .steps-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};
