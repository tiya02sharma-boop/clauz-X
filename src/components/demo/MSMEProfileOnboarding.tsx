import React, { useState } from 'react';
import { ArrowRight, ArrowLeft, Building2, Users, FileCheck, CheckCircle2 } from 'lucide-react';
import type { BusinessProfile } from '../../types';

interface MSMEProfileOnboardingProps {
  initialProfile: BusinessProfile;
  onSubmit: (profile: BusinessProfile) => void;
  onCancel: () => void;
}

export const MSMEProfileOnboarding: React.FC<MSMEProfileOnboardingProps> = ({
  initialProfile,
  onSubmit,
  onCancel
}) => {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [profile, setProfile] = useState<BusinessProfile>(() => ({
    ...initialProfile,
    whatsappNumber: initialProfile.whatsappNumber || '+91 98966 03656'
  }));

  const indianStates = [
    'Maharashtra', 'Karnataka', 'Delhi (NCT)', 'Gujarat', 'Tamil Nadu',
    'Telangana', 'Uttar Pradesh', 'Haryana', 'West Bengal', 'Rajasthan',
    'Kerala', 'Madhya Pradesh', 'Andhra Pradesh', 'Punjab'
  ];

  const sectors = [
    'Information Technology & Software Services',
    'Manufacturing & Industrial Engineering',
    'Retail, E-Commerce & Wholesale Trading',
    'Healthcare, Pharma & Biotech',
    'Professional, Legal & Financial Consulting',
    'Logistics, Warehousing & Supply Chain',
    'Hospitality, Food & Beverages',
    'Construction & Real Estate Development'
  ];

  const turnoverBrackets = [
    'Up to ₹40 Lakhs (Exempt threshold)',
    '₹40 Lakhs - ₹1.5 Crore',
    '₹1.5 Crore - ₹5 Crore (Micro Enterprise)',
    '₹5 Crore - ₹15 Crore (Small Enterprise)',
    '₹15 Crore - ₹50 Crore (Medium Enterprise)',
    'Above ₹50 Crore'
  ];

  const headcountBrackets = [
    '1 - 9 Employees (Below ESI/EPF threshold)',
    '10 - 19 Employees (ESI mandatory, PF optional)',
    '20 - 49 Employees (EPF & ESI mandatory)',
    '50 - 100 Employees (Full labor compliance)',
    '100+ Employees (Industrial Standing Orders)'
  ];

  const handleContinue = () => {
    if (step < 4) {
      setStep((step + 1) as 1 | 2 | 3 | 4);
    } else {
      onSubmit(profile);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep((step - 1) as 1 | 2 | 3 | 4);
    } else {
      onCancel();
    }
  };

  return (
    <div style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '3rem 1rem' }}>
      <div className="container" style={{ maxWidth: '780px' }}>
        
        {/* Onboarding Header */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <div className="eyebrow" style={{ justifyContent: 'center' }}>
            APPLICABILITY ONBOARDING
          </div>
          <h2
            style={{
              fontSize: 'clamp(2rem, 3.5vw, 2.75rem)',
              lineHeight: 1.15,
              color: 'var(--color-black)',
              letterSpacing: '-0.02em',
              marginBottom: '0.75rem'
            }}
          >
            Let's understand your business.
          </h2>
          <p style={{ fontSize: '1rem', color: 'var(--color-muted)' }}>
            Your business profile helps us identify which compliance obligations may apply.
          </p>
        </div>

        {/* Progress Stepper */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '0.75rem',
            marginBottom: '2.5rem'
          }}
        >
          {[
            { num: '01', title: 'Business', icon: Building2 },
            { num: '02', title: 'Size & Scale', icon: Users },
            { num: '03', title: 'Registrations', icon: FileCheck },
            { num: '04', title: 'Review', icon: CheckCircle2 }
          ].map((s, idx) => {
            const stepNum = (idx + 1) as 1 | 2 | 3 | 4;
            const isActive = step === stepNum;
            const isCompleted = step > stepNum;
            return (
              <div
                key={idx}
                onClick={() => setStep(stepNum)}
                style={{
                  padding: '0.85rem 1rem',
                  backgroundColor: isActive ? 'var(--color-card-bg)' : isCompleted ? 'rgba(158, 23, 25, 0.05)' : 'var(--color-bg)',
                  border: isActive ? '1px solid var(--color-brick)' : isCompleted ? '1px solid rgba(158, 23, 25, 0.2)' : '1px solid var(--color-border)',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, color: isActive || isCompleted ? 'var(--color-brick)' : 'var(--color-muted)' }}>
                    {s.num}
                  </span>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: isActive ? 'var(--color-black)' : 'var(--color-muted)' }}>
                    {s.title}
                  </span>
                </div>
                <div style={{ height: '3px', backgroundColor: isActive ? 'var(--color-brick)' : isCompleted ? 'var(--color-brick)' : 'transparent', borderRadius: '2px' }} />
              </div>
            );
          })}
        </div>

        {/* Form Container */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '2.5rem',
            boxShadow: 'var(--shadow-card)'
          }}
        >
          {/* STEP 1: BUSINESS */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'fadeIn 0.25s ease-out' }}>
              <div>
                <label style={labelStyle}>Business Name</label>
                <input
                  type="text"
                  value={profile.businessName}
                  onChange={(e) => setProfile({ ...profile, businessName: e.target.value })}
                  placeholder="e.g. Acme Technologies Pvt Ltd"
                  style={inputStyle}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }} className="form-two-col">
                <div>
                  <label style={labelStyle}>GST Filing Scheme</label>
                  <select value={profile.gstFilingScheme || 'unknown'} onChange={(e) => setProfile({ ...profile, gstFilingScheme: e.target.value as BusinessProfile['gstFilingScheme'] })} style={inputStyle} disabled={!profile.gstRegistered}>
                    <option value="unknown">Not known</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly / QRMP</option>
                    <option value="composition">Composition</option>
                  </select>
                </div>
                <div>
                  <label style={labelStyle}>Most Recent AGM Date</label>
                  <input type="date" value={profile.agmDate || ''} onChange={(e) => setProfile({ ...profile, agmDate: e.target.value || undefined })} style={inputStyle} />
                </div>
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', margin: '-0.75rem 0 0' }}>
                These fields are used only to calculate approved rule formulas. Leave a value blank if unknown; Clauz X will not guess a due date.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }} className="form-two-col">
                <div>
                  <label style={labelStyle}>Entity Type</label>
                  <select
                    value={profile.entityType}
                    onChange={(e) => setProfile({ ...profile, entityType: e.target.value as any })}
                    style={inputStyle}
                  >
                    <option value="Private Limited">Private Limited Company</option>
                    <option value="LLP">Limited Liability Partnership (LLP)</option>
                    <option value="Partnership">Registered Partnership Firm</option>
                    <option value="Sole Proprietorship">Sole Proprietorship</option>
                    <option value="Public Limited">Public Limited Company</option>
                  </select>
                </div>

                <div>
                  <label style={labelStyle}>Registered State / UT</label>
                  <select
                    value={profile.state}
                    onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                    style={inputStyle}
                  >
                    {indianStates.map((st, i) => (
                      <option key={i} value={st}>{st}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label style={labelStyle}>Industry Sector</label>
                <select
                  value={profile.sector}
                  onChange={(e) => setProfile({ ...profile, sector: e.target.value })}
                  style={inputStyle}
                >
                  {sectors.map((sec, i) => (
                    <option key={i} value={sec}>{sec}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* STEP 2: SIZE & SCALE */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'fadeIn 0.25s ease-out' }}>
              <div>
                <label style={labelStyle}>Annual Turnover Bracket (FY 2025-26)</label>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginBottom: '0.6rem' }}>
                  Used to evaluate GST audit thresholds, QRMP scheme applicability, and MSMED classification.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {turnoverBrackets.map((tb, idx) => (
                    <label
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.85rem',
                        padding: '0.85rem 1rem',
                        backgroundColor: profile.turnover === tb ? 'var(--color-brick-light)' : 'var(--color-bg)',
                        border: profile.turnover === tb ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        fontWeight: profile.turnover === tb ? 600 : 400
                      }}
                    >
                      <input
                        type="radio"
                        name="turnover"
                        checked={profile.turnover === tb}
                        onChange={() => setProfile({ ...profile, turnover: tb })}
                        style={{ accentColor: 'var(--color-brick)' }}
                      />
                      <span>{tb}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label style={labelStyle}>Total Workforce / Employee Headcount</label>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginBottom: '0.6rem' }}>
                  Evaluates mandatory ESI (10+ staff) and EPF (20+ staff) registrations.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {headcountBrackets.map((hb, idx) => (
                    <label
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.85rem',
                        padding: '0.85rem 1rem',
                        backgroundColor: profile.headcount === hb ? 'var(--color-brick-light)' : 'var(--color-bg)',
                        border: profile.headcount === hb ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        fontWeight: profile.headcount === hb ? 600 : 400
                      }}
                    >
                      <input
                        type="radio"
                        name="headcount"
                        checked={profile.headcount === hb}
                        onChange={() => setProfile({ ...profile, headcount: hb })}
                        style={{ accentColor: 'var(--color-brick)' }}
                      />
                      <span>{hb}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: REGISTRATIONS */}
          {step === 3 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'fadeIn 0.25s ease-out' }}>
              <div>
                <label style={labelStyle}>Is the business GST Registered?</label>
                <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                  <button
                    type="button"
                    onClick={() => setProfile({ ...profile, gstRegistered: true })}
                    style={{
                      flex: 1,
                      padding: '0.85rem',
                      backgroundColor: profile.gstRegistered ? 'var(--color-brick-light)' : 'var(--color-bg)',
                      border: profile.gstRegistered ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 600,
                      color: profile.gstRegistered ? 'var(--color-brick)' : 'var(--color-black)'
                    }}
                  >
                    ✓ Yes, Registered
                  </button>
                  <button
                    type="button"
                    onClick={() => setProfile({ ...profile, gstRegistered: false })}
                    style={{
                      flex: 1,
                      padding: '0.85rem',
                      backgroundColor: !profile.gstRegistered ? 'var(--color-brick-light)' : 'var(--color-bg)',
                      border: !profile.gstRegistered ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 600,
                      color: !profile.gstRegistered ? 'var(--color-brick)' : 'var(--color-black)'
                    }}
                  >
                    ✕ No / Exempt
                  </button>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }} className="form-two-col">
                <div>
                  <label style={labelStyle}>Permanent Account Number (PAN)</label>
                  <input
                    type="text"
                    value={profile.pan || ''}
                    onChange={(e) => setProfile({ ...profile, pan: e.target.value })}
                    placeholder="e.g. AABCU9603R"
                    style={inputStyle}
                  />
                </div>

                <div>
                  <label style={labelStyle}>GSTIN (if available)</label>
                  <input
                    type="text"
                    value={profile.gstin || ''}
                    onChange={(e) => setProfile({ ...profile, gstin: e.target.value })}
                    placeholder="e.g. 27AABCU9603R1ZM"
                    style={inputStyle}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }} className="form-two-col">
                <div>
                  <label style={labelStyle}>CIN / Registration Number</label>
                  <input
                    type="text"
                    value={profile.cin || ''}
                    onChange={(e) => setProfile({ ...profile, cin: e.target.value })}
                    placeholder="e.g. U72900MH2021PTC368491"
                    style={inputStyle}
                  />
                </div>

                <div>
                  <label style={labelStyle}>Udyam Registration Number</label>
                  <input
                    type="text"
                    value={profile.udyamNumber || ''}
                    onChange={(e) => setProfile({ ...profile, udyamNumber: e.target.value })}
                    placeholder="e.g. UDYAM-MH-01-0084920"
                    style={inputStyle}
                  />
                </div>
              </div>

              <div>
                <label style={labelStyle}>WhatsApp Number for Deadline Reminders</label>
                <input
                  type="text"
                  value={profile.whatsappNumber || ''}
                  onChange={(e) => setProfile({ ...profile, whatsappNumber: e.target.value })}
                  placeholder="+91 98966 03656"
                  style={inputStyle}
                />
                <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginTop: '0.35rem', display: 'block' }}>
                  Statutory reminders will be sent to this WhatsApp number 7, 3, and 1 days before compliance due dates.
                </span>
              </div>
            </div>
          )}

          {/* STEP 4: REVIEW */}
          {step === 4 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'fadeIn 0.25s ease-out' }}>
              <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-brick)', fontWeight: 700 }}>
                  CONFIRM BUSINESS PROFILE PARAMETERS
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', fontSize: '0.875rem' }} className="form-two-col">
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>Business Name</div>
                  <div style={reviewValueStyle}>{profile.businessName}</div>
                </div>
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>Entity Type</div>
                  <div style={reviewValueStyle}>{profile.entityType}</div>
                </div>
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>State & Sector</div>
                  <div style={reviewValueStyle}>{profile.state} • {profile.sector}</div>
                </div>
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>Turnover & Workforce</div>
                  <div style={reviewValueStyle}>{profile.turnover} • {profile.headcount}</div>
                </div>
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>GSTIN / PAN</div>
                  <div style={reviewValueStyle}>{profile.gstin || 'Not Provided'} • {profile.pan || 'Not Provided'}</div>
                </div>
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>CIN / Udyam</div>
                  <div style={reviewValueStyle}>{profile.cin || 'N/A'} • {profile.udyamNumber || 'N/A'}</div>
                </div>
                <div style={reviewItemStyle}>
                  <div style={reviewLabelStyle}>WhatsApp Reminders</div>
                  <div style={reviewValueStyle}>{profile.whatsappNumber || '+91 98966 03656'}</div>
                </div>
              </div>
            </div>
          )}

          {/* Footer Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)' }}>
            <button
              type="button"
              onClick={handleBack}
              className="btn btn-secondary"
              style={{ fontSize: '0.875rem', padding: '0.75rem 1.25rem' }}
            >
              <ArrowLeft size={16} /> Back
            </button>

            <button
              type="button"
              onClick={handleContinue}
              className="btn btn-brick"
              style={{ fontSize: '0.9375rem', padding: '0.75rem 1.75rem' }}
            >
              {step === 4 ? 'Create My Profile' : 'Continue'} <ArrowRight size={16} />
            </button>
          </div>
        </div>

      </div>

      <style>{`
        @media (max-width: 600px) {
          .form-two-col {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8125rem',
  fontWeight: 600,
  color: 'var(--color-black)',
  marginBottom: '0.35rem'
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.75rem 1rem',
  backgroundColor: '#FFFFFF',
  border: '1px solid var(--color-border)',
  borderRadius: '4px',
  fontSize: '0.875rem',
  outline: 'none',
  color: 'var(--color-black)',
  fontFamily: 'var(--font-sans)'
};

const reviewItemStyle: React.CSSProperties = {
  padding: '0.85rem 1rem',
  backgroundColor: '#FAF5ED',
  border: '1px solid var(--color-border)',
  borderRadius: '4px'
};

const reviewLabelStyle: React.CSSProperties = {
  fontSize: '0.6875rem',
  color: 'var(--color-muted)',
  fontFamily: 'var(--font-mono)',
  marginBottom: '0.2rem'
};

const reviewValueStyle: React.CSSProperties = {
  fontWeight: 600,
  color: 'var(--color-black)'
};
