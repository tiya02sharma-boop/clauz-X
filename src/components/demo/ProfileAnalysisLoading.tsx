import React, { useState, useEffect } from 'react';
import { ArrowRight, CheckCircle2, ShieldCheck } from 'lucide-react';
import type { BusinessProfile } from '../../types';

interface ProfileAnalysisLoadingProps {
  profile: BusinessProfile;
  onComplete: () => void;
}

export const ProfileAnalysisLoading: React.FC<ProfileAnalysisLoadingProps> = ({
  profile,
  onComplete
}) => {
  const [stage, setStage] = useState<number>(0);
  const [isReady, setIsReady] = useState(false);

  const statutoryChecks = [
    'Evaluating GST threshold against turnover bracket...',
    'Checking EPF & ESI labor applicability for headcount...',
    'Mapping Companies Act 2013 secretarial mandates...',
    'Verifying MSMED Act Section 15 & MSME-1 requirements...',
    'Synthesizing calendar dates & personalized compliance view...'
  ];

  useEffect(() => {
    const timer1 = setTimeout(() => setStage(1), 700);
    const timer2 = setTimeout(() => setStage(2), 1400);
    const timer3 = setTimeout(() => setStage(3), 2100);
    const timer4 = setTimeout(() => setStage(4), 2800);
    const timer5 = setTimeout(() => {
      setStage(5);
      setIsReady(true);
    }, 3400);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
    };
  }, []);

  return (
    <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '3rem 1.5rem' }}>
      <div
        style={{
          maxWidth: '580px',
          width: '100%',
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '3rem 2.5rem',
          textAlign: 'center',
          boxShadow: 'var(--shadow-card)',
          position: 'relative'
        }}
      >
        {!isReady ? (
          <div>
            {/* Animated Radar Pulse */}
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--color-brick-light)', border: '2px solid var(--color-brick)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem', position: 'relative', animation: 'pulseSubtle 1.5s infinite ease-in-out' }}>
              <ShieldCheck size={36} className="text-brick" />
            </div>

            <h3 style={{ fontSize: '1.75rem', color: 'var(--color-black)', letterSpacing: '-0.01em', marginBottom: '0.5rem' }}>
              Understanding your business...
            </h3>
            <p style={{ fontSize: '0.9375rem', color: 'var(--color-muted)', marginBottom: '2.5rem' }}>
              Mapping statutory acts and due dates for <strong style={{ color: 'var(--color-black)' }}>{profile.businessName}</strong>.
            </p>

            {/* Check status list */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', textAlign: 'left', backgroundColor: 'var(--color-bg)', padding: '1.25rem', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
              {statutoryChecks.map((check, idx) => {
                const isPassed = stage > idx;
                const isCurrent = stage === idx;
                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      fontSize: '0.8125rem',
                      color: isPassed ? 'var(--color-black)' : isCurrent ? 'var(--color-brick)' : 'var(--color-muted)',
                      fontWeight: isPassed || isCurrent ? 600 : 400,
                      opacity: isPassed || isCurrent ? 1 : 0.45,
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {isPassed ? (
                      <CheckCircle2 size={16} className="text-brick" />
                    ) : (
                      <span style={{ width: '16px', height: '16px', borderRadius: '50%', border: '1.5px solid currentColor', display: 'inline-block' }} />
                    )}
                    <span>{check}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div style={{ animation: 'fadeIn 0.35s ease-out' }}>
            <div style={{ width: '70px', height: '70px', borderRadius: '50%', backgroundColor: 'var(--color-brick)', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <CheckCircle2 size={36} />
            </div>

            <div className="eyebrow" style={{ justifyContent: 'center', marginBottom: '0.5rem' }}>
              ANALYSIS COMPLETE
            </div>

            <h3 style={{ fontSize: '2rem', color: 'var(--color-black)', letterSpacing: '-0.02em', marginBottom: '0.75rem' }}>
              Your compliance profile is ready.
            </h3>

            <p style={{ fontSize: '0.9375rem', color: 'var(--color-muted)', marginBottom: '2rem' }}>
              We've synthesized all applicable Central and State statutory mandates for your entity.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2.5rem' }}>
              <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2.25rem', color: 'var(--color-brick)', lineHeight: 1 }}>Mapped</div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-black)', marginTop: '0.35rem' }}>
                  Statutory Obligations
                </div>
              </div>

              <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2.25rem', color: 'var(--color-black)', lineHeight: 1 }}>Active</div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-black)', marginTop: '0.35rem' }}>
                  Compliance Calendar
                </div>
              </div>
            </div>

            <button
              onClick={onComplete}
              className="btn btn-brick"
              style={{ width: '100%', padding: '1rem', fontSize: '1rem' }}
            >
              View My Compliance Dashboard <ArrowRight size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
