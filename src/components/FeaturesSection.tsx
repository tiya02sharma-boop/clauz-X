import React, { useState } from 'react';
import {
  Calendar,
  MessageSquare,
  History,
  Send,
  ExternalLink,
  Smartphone,
  Mail,
  Check
} from 'lucide-react';
import { samplePredefinedQuestions, mockChatAnswers } from '../data/mockComplianceData';

export const FeaturesSection: React.FC = () => {
  // State for interactive Ask Clauz X mockup in Feature 04
  const [selectedQuestion, setSelectedQuestion] = useState(samplePredefinedQuestions[0]);
  const [activeCalendarMonth] = useState('September 2026');
  const [showCitationDetails, setShowCitationDetails] = useState(false);

  const activeChatData = mockChatAnswers[selectedQuestion] || mockChatAnswers["When is my next GST filing due?"];

  return (
    <section id="features" className="section-padding bg-offwhite" style={{ position: 'relative' }}>
      <div className="container">
        {/* Header */}
        <div style={{ maxWidth: '680px', marginBottom: '5rem' }}>
          <div className="eyebrow">
            COMPREHENSIVE CAPABILITIES
          </div>
          <h2
            style={{
              fontSize: 'clamp(2.5rem, 4.5vw, 3.75rem)',
              lineHeight: 1.1,
              color: 'var(--color-black)',
              letterSpacing: '-0.02em',
              marginBottom: '1rem'
            }}
          >
            Everything you need.<br />
            <span className="text-brick">Nothing you don't.</span>
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-muted)' }}>
            Six purpose-built engines designed specifically around Indian statutory realities for small and growing enterprises.
          </p>
        </div>

        {/* 6 Feature Showcase Modules */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5rem' }}>

          {/* ==========================================================
              FEATURE 01: PERSONALIZED OBLIGATION MAPPING
             ========================================================== */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '4rem',
              alignItems: 'center',
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '3.5rem',
              boxShadow: 'var(--shadow-card)'
            }}
            className="feature-row"
          >
            <div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.6rem', backgroundColor: 'var(--color-brick-light)', color: 'var(--color-brick)', borderRadius: '3px', fontWeight: 600 }}>
                Rule-based applicability
              </span>
              <h3 style={{ fontSize: '2.25rem', color: 'var(--color-black)', margin: '1.25rem 0 1rem', letterSpacing: '-0.02em' }}>
                Personalized Obligation Mapping
              </h3>
              <p style={{ fontSize: '1.0625rem', color: 'var(--color-muted)', lineHeight: 1.7, marginBottom: '2rem' }}>
                Identify compliance obligations based on your business attributes such as turnover, headcount, sector, state and entity type. We automatically filter out non-applicable statutes so you only see what matters.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.9375rem', color: 'var(--color-black)' }}>
                  <div style={{ width: '22px', height: '22px', borderRadius: '50%', backgroundColor: 'var(--color-brick)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Check size={14} />
                  </div>
                  <span>Real-time evaluation against 40+ statutory thresholds</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.9375rem', color: 'var(--color-black)' }}>
                  <div style={{ width: '22px', height: '22px', borderRadius: '50%', backgroundColor: 'var(--color-brick)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Check size={14} />
                  </div>
                  <span>Automatic state-specific rules for Maharashtra, Karnataka, Delhi, etc.</span>
                </div>
              </div>
            </div>

            {/* Visual: Business Profile -> Rules -> Applicable Obligations */}
            <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '2rem', boxShadow: '0 4px 16px rgba(0,0,0,0.03)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--color-border)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', textTransform: 'uppercase', color: 'var(--color-muted)' }}>MAPPING PIPELINE</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', color: 'var(--color-brick)', fontWeight: 600 }}>THRESHOLD EVALUATED</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)', marginBottom: '0.25rem' }}>STEP 1: BUSINESS ATTRIBUTES</div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-black)' }}>Pvt Ltd • Headcount: 28 • Turnover: ₹8.4 Cr</div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-brick)', fontWeight: 600 }}>↓ Applied via 12 statutory filter rules</div>
                </div>

                <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-brick)', color: '#FFFFFF', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', opacity: 0.85, marginBottom: '0.4rem' }}>STEP 2: APPLICABLE OBLIGATIONS</div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, marginBottom: '0.5rem' }}>12 Active Mandates Confirmed</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    <span style={{ fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: '2px' }}>GST Section 39</span>
                    <span style={{ fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: '2px' }}>ESI Act (10+ Staff)</span>
                    <span style={{ fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: '2px' }}>EPF Act (20+ Staff)</span>
                    <span style={{ fontSize: '0.6875rem', padding: '0.2rem 0.5rem', backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: '2px' }}>MSME-1 Form</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ==========================================================
              FEATURE 02: COMPLIANCE CALENDAR
             ========================================================== */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1.1fr',
              gap: '4rem',
              alignItems: 'center',
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '3.5rem',
              boxShadow: 'var(--shadow-card)'
            }}
            className="feature-row"
          >
            <div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.6rem', backgroundColor: 'var(--color-brick-light)', color: 'var(--color-brick)', borderRadius: '3px', fontWeight: 600 }}>
                Forward-looking timeline
              </span>
              <h3 style={{ fontSize: '2.25rem', color: 'var(--color-black)', margin: '1.25rem 0 1rem', letterSpacing: '-0.02em' }}>
                Compliance Calendar
              </h3>
              <p style={{ fontSize: '1.0625rem', color: 'var(--color-muted)', lineHeight: 1.7, marginBottom: '2rem' }}>
                Turn applicable obligations into a forward-looking schedule with concrete due dates. Never juggle separate government portals or static spreadsheets again.
              </p>

              <div style={{ display: 'flex', gap: '1.5rem', borderTop: '1px solid var(--color-border)', paddingTop: '1.5rem' }}>
                <div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', color: 'var(--color-brick)', lineHeight: 1 }}>04</div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginTop: '0.25rem' }}>Due This Month</div>
                </div>
                <div style={{ width: '1px', height: '40px', backgroundColor: 'var(--color-border)' }} />
                <div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', color: 'var(--color-black)', lineHeight: 1 }}>07</div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginTop: '0.25rem' }}>Upcoming Q3 Filings</div>
                </div>
              </div>
            </div>

            {/* Visual: Clean monthly calendar highlighting GSTR-3B, ESI, TDS, MSME-1 */}
            <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1.75rem', boxShadow: '0 4px 16px rgba(0,0,0,0.03)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Calendar size={18} className="text-brick" />
                  <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--color-black)' }}>{activeCalendarMonth}</span>
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', backgroundColor: 'var(--color-bg)', padding: '0.25rem 0.5rem', borderRadius: '3px', border: '1px solid var(--color-border)' }}>
                  STATUTORY SCHEDULE
                </span>
              </div>

              {/* Highlighted Calendar Rows */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {[
                  { day: '11', code: 'GSTR-1', name: 'Monthly Outward Supplies', status: 'Due in 1 day', statusColor: 'var(--color-brick)' },
                  { day: '15', code: 'EPF & ESI', name: 'Challan & Social Security', status: 'Due in 5 days', statusColor: '#C05621' },
                  { day: '20', code: 'GSTR-3B', name: 'Monthly Summary GST Return', status: 'Due in 10 days', statusColor: 'var(--color-black)' },
                  { day: '30', code: 'DIR-3 KYC', name: 'Annual Director Verification', status: 'Due in 20 days', statusColor: 'var(--color-muted)' },
                  { day: '31', code: 'MSME-1', name: 'Outstanding Vendor Dues Return', status: 'Due in 31 days', statusColor: 'var(--color-muted)' }
                ].map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.85rem 1rem',
                      backgroundColor: idx === 0 ? 'var(--color-brick-light)' : 'var(--color-bg)',
                      border: idx === 0 ? '1px solid var(--color-border-brick)' : '1px solid var(--color-border)',
                      borderRadius: '4px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span style={{ fontFamily: 'var(--font-serif)', fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-brick)', minWidth: '24px' }}>
                        {item.day}
                      </span>
                      <div>
                        <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>{item.code}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>{item.name}</div>
                      </div>
                    </div>
                    <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', fontWeight: 600, color: item.statusColor }}>
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ==========================================================
              FEATURE 03: PROACTIVE REMINDERS
             ========================================================== */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '4rem',
              alignItems: 'center',
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '3.5rem',
              boxShadow: 'var(--shadow-card)'
            }}
            className="feature-row"
          >
            <div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.6rem', backgroundColor: 'var(--color-brick-light)', color: 'var(--color-brick)', borderRadius: '3px', fontWeight: 600 }}>
                Multi-channel notifications
              </span>
              <h3 style={{ fontSize: '2.25rem', color: 'var(--color-black)', margin: '1.25rem 0 1rem', letterSpacing: '-0.02em' }}>
                Proactive Reminders
              </h3>
              <p style={{ fontSize: '1.0625rem', color: 'var(--color-muted)', lineHeight: 1.7, marginBottom: '2rem' }}>
                Get reminders before deadlines instead of discovering an obligation after it is missed. Alerts trigger at critical milestones with pre-drafted summaries.
              </p>

              <div style={{ display: 'flex', gap: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.6rem 1rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <Smartphone size={18} className="text-brick" />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>WhatsApp Alerts</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.6rem 1rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <Mail size={18} className="text-brick" />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Email Digests</span>
                </div>
              </div>
            </div>

            {/* Visual: T-7 -> T-3 -> T-1 -> DUE cascade */}
            <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '2rem', boxShadow: '0 4px 16px rgba(0,0,0,0.03)' }}>
              <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', color: 'var(--color-muted)', marginBottom: '1.5rem', letterSpacing: '0.08em' }}>
                ALERT CADENCE ENGINE
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {[
                  { label: 'T - 7 DAYS', title: 'Advance Notice & Document Checklist', desc: 'Summary of required invoices and data inputs sent to finance team.', badge: 'Email' },
                  { label: 'T - 3 DAYS', title: 'Challan Verification & Calculation', desc: 'Alert to verify gross tax liabilities and initiate bank transfer.', badge: 'WhatsApp' },
                  { label: 'T - 1 DAY', title: 'Final Portal Submission Reminder', desc: 'Urgent notification with pre-filled acknowledgment form link.', badge: 'Priority Push' },
                  { label: 'DUE DATE', title: 'Statutory Filing Completion', desc: 'Filing confirmed; timestamped audit log saved to secure vault.', badge: 'Audit Confirmed', isFinal: true }
                ].map((step, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '1.25rem',
                      padding: '1rem',
                      backgroundColor: step.isFinal ? 'var(--color-brick)' : 'var(--color-bg)',
                      color: step.isFinal ? '#FFFFFF' : 'var(--color-black)',
                      borderRadius: '4px',
                      border: step.isFinal ? 'none' : '1px solid var(--color-border)'
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.8125rem',
                        fontWeight: 700,
                        color: step.isFinal ? '#FFFFFF' : 'var(--color-brick)',
                        minWidth: '85px'
                      }}
                    >
                      {step.label}
                    </span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '0.2rem' }}>{step.title}</div>
                      <div style={{ fontSize: '0.75rem', opacity: 0.85, lineHeight: 1.4 }}>{step.desc}</div>
                    </div>
                    <span
                      style={{
                        fontSize: '0.6875rem',
                        fontFamily: 'var(--font-mono)',
                        padding: '0.2rem 0.5rem',
                        backgroundColor: step.isFinal ? 'rgba(255,255,255,0.2)' : '#FFFFFF',
                        border: '1px solid rgba(0,0,0,0.1)',
                        borderRadius: '3px',
                        color: step.isFinal ? '#FFFFFF' : 'var(--color-black)'
                      }}
                    >
                      {step.badge}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ==========================================================
              FEATURE 04: ASK CLAUZ X (CONVERSATIONAL MOCKUP)
             ========================================================== */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1.25fr',
              gap: '4rem',
              alignItems: 'center',
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '3.5rem',
              boxShadow: 'var(--shadow-card)'
            }}
            className="feature-row"
          >
            <div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.6rem', backgroundColor: 'var(--color-brick-light)', color: 'var(--color-brick)', borderRadius: '3px', fontWeight: 600 }}>
                Grounded Legal AI
              </span>
              <h3 style={{ fontSize: '2.25rem', color: 'var(--color-black)', margin: '1.25rem 0 1rem', letterSpacing: '-0.02em' }}>
                Ask Clauz X
              </h3>
              <p style={{ fontSize: '1.0625rem', color: 'var(--color-muted)', lineHeight: 1.7, marginBottom: '1.5rem' }}>
                Ask compliance questions in plain language with answers grounded in relevant regulatory sources, circulars, and sections.
              </p>

              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.75rem' }}>
                Try interactive questions:
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {samplePredefinedQuestions.slice(0, 3).map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedQuestion(q)}
                    style={{
                      textAlign: 'left',
                      padding: '0.65rem 0.9rem',
                      fontSize: '0.8125rem',
                      fontFamily: 'var(--font-sans)',
                      backgroundColor: selectedQuestion === q ? 'var(--color-brick)' : '#FFFFFF',
                      color: selectedQuestion === q ? '#FFFFFF' : 'var(--color-black)',
                      border: selectedQuestion === q ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      fontWeight: selectedQuestion === q ? 600 : 400
                    }}
                  >
                    💬 "{q}"
                  </button>
                ))}
              </div>
            </div>

            {/* Visual: Sophisticated conversational interface mockup */}
            <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1.75rem', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>

              {/* Chat Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1rem', borderBottom: '1px solid var(--color-border)', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '4px', backgroundColor: 'var(--color-brick)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <MessageSquare size={14} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>Clauz X Regulatory Assistant</div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--color-muted)' }}>Grounded on Central & State Acts</div>
                  </div>
                </div>
                <span style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', color: 'green', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '6px', height: '6px', backgroundColor: 'green', borderRadius: '50%' }} /> Active
                </span>
              </div>

              {/* User Question */}
              <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                <div style={{ backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '6px 6px 0 6px', padding: '0.75rem 1rem', maxWidth: '85%', fontSize: '0.875rem', color: 'var(--color-black)', fontWeight: 500 }}>
                  {selectedQuestion}
                </div>
              </div>

              {/* Assistant Answer with Grounded Source */}
              <div style={{ marginBottom: '1.25rem' }}>
                <div style={{ backgroundColor: '#FAF5ED', border: '1px solid var(--color-border)', borderRadius: '0 6px 6px 6px', padding: '1.1rem 1.25rem' }}>
                  <p style={{ fontSize: '0.875rem', color: 'var(--color-black)', lineHeight: 1.6, marginBottom: '1rem' }}>
                    {activeChatData.answer}
                  </p>

                  {/* Grounded Citation Box */}
                  <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border-brick)', borderRadius: '4px', padding: '0.85rem 1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--color-brick)', textTransform: 'uppercase' }}>
                        STATUTORY SOURCE
                      </span>
                      <button
                        onClick={() => setShowCitationDetails(!showCitationDetails)}
                        style={{ background: 'none', border: 'none', color: 'var(--color-brick)', fontSize: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem', cursor: 'pointer' }}
                      >
                        VIEW SOURCE <ExternalLink size={12} />
                      </button>
                    </div>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-black)' }}>
                      {activeChatData.source.act}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>
                      {activeChatData.source.section} • {activeChatData.source.rule}
                    </div>

                    {showCitationDetails && (
                      <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px dashed var(--color-border)', fontSize: '0.75rem', color: 'var(--color-muted)', lineHeight: 1.5 }}>
                        <strong>Official Provision Summary:</strong> {activeChatData.source.summary}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Simulated input bar */}
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px', padding: '0.5rem 0.75rem' }}>
                <input
                  type="text"
                  placeholder="Ask any statutory question (e.g. MSME payment terms)..."
                  readOnly
                  value=""
                  style={{ flex: 1, background: 'none', border: 'none', fontSize: '0.8125rem', outline: 'none', color: 'var(--color-black)' }}
                />
                <button style={{ background: 'var(--color-brick)', color: '#fff', border: 'none', width: '28px', height: '28px', borderRadius: '3px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Send size={12} />
                </button>
              </div>

            </div>
          </div>

          {/* ==========================================================
              FEATURE 05: AUDIT TRAIL
             ========================================================== */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '4rem',
              alignItems: 'center',
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '3.5rem',
              boxShadow: 'var(--shadow-card)'
            }}
            className="feature-row"
          >
            <div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', padding: '0.3rem 0.6rem', backgroundColor: 'var(--color-brick-light)', color: 'var(--color-brick)', borderRadius: '3px', fontWeight: 600 }}>
                Traceable Compliance History
              </span>
              <h3 style={{ fontSize: '2.25rem', color: 'var(--color-black)', margin: '1.25rem 0 1rem', letterSpacing: '-0.02em' }}>
                Immutable Audit Trail
              </h3>
              <p style={{ fontSize: '1.0625rem', color: 'var(--color-muted)', lineHeight: 1.7, marginBottom: '2rem' }}>
                Keep a timestamped history of important compliance actions. Demonstrate due diligence and provide verifiable logs to your Chartered Accountant or auditors.
              </p>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', width: 'fit-content' }}>
                <History size={18} className="text-brick" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Zero-alteration audit timestamps</span>
              </div>
            </div>

            {/* Visual: Vertical timeline with timestamps */}
            <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '2rem', boxShadow: '0 4px 16px rgba(0,0,0,0.03)' }}>
              <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', color: 'var(--color-muted)', marginBottom: '1.5rem', letterSpacing: '0.08em' }}>
                TIMELOCKED ACTIVITY LEDGER
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', position: 'relative' }}>
                {[
                  { time: '10:42 AM', title: 'Obligation assessment completed', desc: '12 active obligations mapped based on turnover parameters.', badge: 'System' },
                  { time: '09:00 AM', title: 'Reminder sent', desc: 'GSTR-1 filing alert sent via WhatsApp and finance email.', badge: 'Alert' },
                  { time: 'Yesterday', title: 'Document generated', desc: 'Pre-filled MCA Form MSME-1 generated and validated.', badge: 'Draft' }
                ].map((item, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '1.25rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-brick)', marginTop: '4px' }} />
                      {idx !== 2 && <div style={{ width: '1px', height: '40px', backgroundColor: 'var(--color-border)', marginTop: '4px' }} />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.2rem' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-brick)' }}>{item.time}</span>
                        <span style={{ fontSize: '0.625rem', fontFamily: 'var(--font-mono)', backgroundColor: 'var(--color-bg)', padding: '0.15rem 0.4rem', borderRadius: '2px', border: '1px solid var(--color-border)' }}>{item.badge}</span>
                      </div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>{item.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>

      <style>{`
        @media (max-width: 960px) {
          .feature-row {
            grid-template-columns: 1fr !important;
            gap: 2.5rem !important;
            padding: 2rem !important;
          }
        }
      `}</style>
    </section>
  );
};
