import React from 'react';
import { ArrowDown, Check, Building, FileSpreadsheet, BellRing, Sparkles } from 'lucide-react';

export const SolutionSection: React.FC = () => {
  return (
    <section className="bg-offwhite section-padding" style={{ position: 'relative' }}>
      <div className="container">
        {/* Header */}
        <div style={{ textAlign: 'center', maxWidth: '760px', margin: '0 auto 4.5rem' }}>
          <div className="eyebrow" style={{ justifyContent: 'center' }}>
            MEET CLAUZ X
          </div>
          <h2
            style={{
              fontSize: 'clamp(2.25rem, 4.5vw, 3.75rem)',
              lineHeight: 1.1,
              marginBottom: '1.25rem',
              color: 'var(--color-black)',
              letterSpacing: '-0.02em'
            }}
          >
            Your compliance,<br />
            <span className="text-brick">organized around your business.</span>
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-muted)', maxWidth: '600px', margin: '0 auto' }}>
            Clauz X starts with your business profile and builds a personalized compliance view around it — eliminating generic checklists.
          </p>
        </div>

        {/* Large Visual Flow Architecture: Vertical & Horizontal Editorial Stages */}
        <div style={{ maxWidth: '880px', margin: '0 auto' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {/* Stage 1: YOUR BUSINESS */}
            <div
              style={{
                backgroundColor: 'var(--color-card-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.75rem 2.25rem',
                display: 'grid',
                gridTemplateColumns: '180px 1fr auto',
                alignItems: 'center',
                gap: '2rem',
                transition: 'all 0.3s ease'
              }}
              className="flow-row"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Building size={16} />
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', fontWeight: 600, letterSpacing: '0.05em' }}>
                  01 / INPUT
                </span>
              </div>
              <div>
                <h4 style={{ fontSize: '1.25rem', color: 'var(--color-black)', marginBottom: '0.2rem' }}>YOUR BUSINESS</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', margin: 0 }}>
                  Indian entity structure, registered location, turnover tier, and headcount metrics.
                </p>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.75rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '3px' }}>
                RAW DATA
              </span>
            </div>

            {/* Connecting Arrow */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.5rem 0' }}>
              <ArrowDown size={20} style={{ color: 'var(--color-brick)' }} />
            </div>

            {/* Stage 2: PROFILE */}
            <div
              style={{
                backgroundColor: 'var(--color-card-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.75rem 2.25rem',
                display: 'grid',
                gridTemplateColumns: '180px 1fr auto',
                alignItems: 'center',
                gap: '2rem'
              }}
              className="flow-row"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FileSpreadsheet size={16} />
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', fontWeight: 600, letterSpacing: '0.05em' }}>
                  02 / STRUCTURE
                </span>
              </div>
              <div>
                <h4 style={{ fontSize: '1.25rem', color: 'var(--color-black)', marginBottom: '0.2rem' }}>PROFILE</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', margin: 0 }}>
                  Categorized metadata engine applying statutory threshold filters across Indian laws.
                </p>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.75rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '3px' }}>
                RULE-EVALUATED
              </span>
            </div>

            {/* Connecting Arrow */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.5rem 0' }}>
              <ArrowDown size={20} style={{ color: 'var(--color-brick)' }} />
            </div>

            {/* Stage 3: APPLICABLE OBLIGATIONS (BRICK RED HIGHLIGHT) */}
            <div
              style={{
                backgroundColor: 'var(--color-brick)',
                color: '#FFFFFF',
                borderRadius: 'var(--radius-sm)',
                padding: '2rem 2.25rem',
                display: 'grid',
                gridTemplateColumns: '180px 1fr auto',
                alignItems: 'center',
                gap: '2rem',
                boxShadow: '0 12px 30px rgba(158, 23, 25, 0.25)',
                border: '1px solid var(--color-brick-dark)'
              }}
              className="flow-row"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '4px', backgroundColor: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF' }}>
                  <Check size={18} />
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', fontWeight: 700, letterSpacing: '0.05em', color: '#FFFFFF' }}>
                  03 / CORE FILTER
                </span>
              </div>
              <div>
                <h4 style={{ fontSize: '1.35rem', color: '#FFFFFF', marginBottom: '0.25rem', letterSpacing: '-0.01em' }}>
                  APPLICABLE OBLIGATIONS
                </h4>
                <p style={{ fontSize: '0.9375rem', color: 'rgba(255,255,255,0.9)', margin: 0 }}>
                  Exact statutory requirements extracted: GST, EPF, ESI, MSME-1, TDS, and MCA filings tailored specifically to your parameters.
                </p>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.35rem 0.85rem', backgroundColor: '#FFFFFF', color: 'var(--color-brick)', borderRadius: '3px', fontWeight: 700 }}>
                ACTIVE ENGINE
              </span>
            </div>

            {/* Connecting Arrow */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.5rem 0' }}>
              <ArrowDown size={20} style={{ color: 'var(--color-brick)' }} />
            </div>

            {/* Stage 4: DEADLINES */}
            <div
              style={{
                backgroundColor: 'var(--color-card-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.75rem 2.25rem',
                display: 'grid',
                gridTemplateColumns: '180px 1fr auto',
                alignItems: 'center',
                gap: '2rem'
              }}
              className="flow-row"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <BellRing size={16} />
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', fontWeight: 600, letterSpacing: '0.05em' }}>
                  04 / SCHEDULE
                </span>
              </div>
              <div>
                <h4 style={{ fontSize: '1.25rem', color: 'var(--color-black)', marginBottom: '0.2rem' }}>DEADLINES</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', margin: 0 }}>
                  A forward-looking calendar with concrete statutory dates and multi-channel proactive alerts.
                </p>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.75rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '3px' }}>
                TIME-LOCKED
              </span>
            </div>

            {/* Connecting Arrow */}
            <div style={{ display: 'flex', justifyContent: 'center', margin: '-0.5rem 0' }}>
              <ArrowDown size={20} style={{ color: 'var(--color-black)' }} />
            </div>

            {/* Stage 5: ACTION */}
            <div
              style={{
                backgroundColor: 'var(--color-beige)',
                border: '1px solid var(--color-beige-dark)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.75rem 2.25rem',
                display: 'grid',
                gridTemplateColumns: '180px 1fr auto',
                alignItems: 'center',
                gap: '2rem'
              }}
              className="flow-row"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '4px', backgroundColor: 'rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={16} />
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--color-black)' }}>
                  05 / RESOLUTION
                </span>
              </div>
              <div>
                <h4 style={{ fontSize: '1.25rem', color: 'var(--color-black)', marginBottom: '0.2rem' }}>ACTION</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-black)', margin: 0 }}>
                  Ask plain-language questions with regulatory sources, auto-draft forms, and maintain audit-proof records.
                </p>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.75rem', backgroundColor: '#FFFFFF', border: '1px solid rgba(0,0,0,0.15)', borderRadius: '3px', fontWeight: 600 }}>
                CONFIRMED
              </span>
            </div>

          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .flow-row {
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
          }
        }
      `}</style>
    </section>
  );
};
