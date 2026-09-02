import React from 'react';
import { Filter, CalendarClock, HelpCircle } from 'lucide-react';

export const ProblemSection: React.FC = () => {
  return (
    <section className="bg-beige section-padding" style={{ position: 'relative' }}>
      <div className="container">
        {/* Header */}
        <div style={{ maxWidth: '680px', marginBottom: '4rem' }}>
          <div className="eyebrow eyebrow-dark" style={{ color: 'var(--color-brick)' }}>
            THE COMPLIANCE FRICTION
          </div>
          <h2
            style={{
              fontSize: 'clamp(2.25rem, 4vw, 3.5rem)',
              lineHeight: 1.1,
              color: 'var(--color-black)',
              letterSpacing: '-0.02em',
              marginBottom: '1rem'
            }}
          >
            Too many rules.<br />
            Too little clarity.
          </h2>
          <p style={{ color: '#3D3830', fontSize: '1.125rem' }}>
            Growing businesses spend countless hours sifting through statutory circulars, risking missed deadlines, and dealing with fragmented advisory.
          </p>
        </div>

        {/* 3 Large Editorial Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2rem'
          }}
          className="problem-cards-grid"
        >
          {/* Card 01 */}
          <div
            style={{
              backgroundColor: '#FAF5ED',
              border: '1px solid rgba(0, 0, 0, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '2.5rem 2rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              minHeight: '340px',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease'
            }}
            className="hover-lift"
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                <span className="card-num" style={{ marginBottom: 0 }}>01</span>
                <div style={{ width: '44px', height: '44px', borderRadius: '50%', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                  <Filter size={20} />
                </div>
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--color-black)', letterSpacing: '-0.01em' }}>
                WHAT APPLIES?
              </h3>
              <p style={{ color: 'var(--color-muted)', fontSize: '0.9375rem', lineHeight: 1.65 }}>
                Not every compliance requirement applies to every business. The challenge is identifying the ones that actually matter based on headcount, state, turnover, and structure.
              </p>
            </div>
            <div style={{ paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)', fontSize: '0.8125rem', fontFamily: 'var(--font-mono)', color: 'var(--color-brick)' }}>
              → Threshold ambiguity
            </div>
          </div>

          {/* Card 02 */}
          <div
            style={{
              backgroundColor: '#FAF5ED',
              border: '1px solid rgba(0, 0, 0, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '2.5rem 2rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              minHeight: '340px',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease'
            }}
            className="hover-lift"
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                <span className="card-num" style={{ marginBottom: 0 }}>02</span>
                <div style={{ width: '44px', height: '44px', borderRadius: '50%', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                  <CalendarClock size={20} />
                </div>
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--color-black)', letterSpacing: '-0.01em' }}>
                WHAT'S DUE?
              </h3>
              <p style={{ color: 'var(--color-muted)', fontSize: '0.9375rem', lineHeight: 1.65 }}>
                Multiple filing cycles across different ministries make it easy to lose track of upcoming deadlines, resulting in preventable daily late fees and compliance friction.
              </p>
            </div>
            <div style={{ paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)', fontSize: '0.8125rem', fontFamily: 'var(--font-mono)', color: 'var(--color-brick)' }}>
              → Fragmented calendars
            </div>
          </div>

          {/* Card 03 */}
          <div
            style={{
              backgroundColor: '#FAF5ED',
              border: '1px solid rgba(0, 0, 0, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '2.5rem 2rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              minHeight: '340px',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease'
            }}
            className="hover-lift"
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                <span className="card-num" style={{ marginBottom: 0 }}>03</span>
                <div style={{ width: '44px', height: '44px', borderRadius: '50%', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                  <HelpCircle size={20} />
                </div>
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--color-black)', letterSpacing: '-0.01em' }}>
                WHAT NOW?
              </h3>
              <p style={{ color: 'var(--color-muted)', fontSize: '0.9375rem', lineHeight: 1.65 }}>
                When a question comes up, finding a reliable and relevant answer grounded in actual Acts and Notifications takes time, leaving founders uncertain of their next step.
              </p>
            </div>
            <div style={{ paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)', fontSize: '0.8125rem', fontFamily: 'var(--font-mono)', color: 'var(--color-brick)' }}>
              → Ungrounded advisory
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .hover-lift:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
          border-color: rgba(0, 0, 0, 0.35) !important;
        }
        @media (max-width: 900px) {
          .problem-cards-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};
