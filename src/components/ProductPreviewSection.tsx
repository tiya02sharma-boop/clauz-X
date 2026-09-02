import { ArrowRight, CheckCircle, AlertTriangle, Calendar, Sparkles } from 'lucide-react';

interface ProductPreviewSectionProps {
  onGetStarted: () => void;
}

export const ProductPreviewSection: React.FC<ProductPreviewSectionProps> = ({ onGetStarted }) => {
  return (
    <section id="product-preview" className="section-padding hairline-top" style={{ backgroundColor: 'var(--color-bg)', overflow: 'hidden' }}>
      <div className="container">
        {/* Header */}
        <div style={{ textAlign: 'center', maxWidth: '720px', margin: '0 auto 4rem' }}>
          <div className="eyebrow" style={{ justifyContent: 'center' }}>
            PRODUCT INTERFACE
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
            See compliance at a glance.
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-muted)' }}>
            A unified, uncluttered view of all your company's statutory filings, health ratings, and upcoming deadlines.
          </p>
        </div>

        {/* Generously Spaced Browser Mockup */}
        <div style={{ maxWidth: '1060px', margin: '0 auto', position: 'relative' }}>
          
          {/* Browser Frame */}
          <div
            style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.12)',
              overflow: 'hidden'
            }}
          >
            {/* Browser Header Bar */}
            <div
              style={{
                backgroundColor: '#FAF5ED',
                padding: '0.85rem 1.5rem',
                borderBottom: '1px solid var(--color-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#E25C5C', display: 'inline-block' }} />
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#E5A93C', display: 'inline-block' }} />
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#5CB85C', display: 'inline-block' }} />
              </div>

              <div
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid var(--color-border)',
                  borderRadius: '20px',
                  padding: '0.25rem 1.5rem',
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--color-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <span>🔒</span>
                <span>app.claux-x.in/dashboard/acme-technologies</span>
              </div>

              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', color: 'var(--color-brick)', fontWeight: 600 }}>
                LIVE PREVIEW
              </span>
            </div>

            {/* Dashboard Content Mockup */}
            <div style={{ padding: '2.5rem', backgroundColor: '#FFFFFF' }}>
              
              {/* Dashboard Top Row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem', flexWrap: 'wrap', gap: '1.5rem' }}>
                <div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.75rem', color: 'var(--color-black)', marginBottom: '0.25rem' }}>
                    Good morning, Acme Technologies.
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
                    Here is your real-time statutory compliance health & filing roadmap.
                  </div>
                </div>

                <button
                  onClick={onGetStarted}
                  className="btn btn-brick"
                  style={{ fontSize: '0.875rem', padding: '0.65rem 1.25rem' }}
                >
                  <Sparkles size={14} /> Open Interactive Demo
                </button>
              </div>

              {/* 5 Key Metric Cards */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(5, 1fr)',
                  gap: '1rem',
                  marginBottom: '2.5rem'
                }}
                className="preview-metrics-grid"
              >
                {/* Metric 1: Health */}
                <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>Compliance Health</div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', color: 'var(--color-brick)', margin: '0.25rem 0' }}>82%</div>
                  <div style={{ fontSize: '0.75rem', color: 'green', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <CheckCircle size={12} /> Above Peer Avg
                  </div>
                </div>

                {/* Metric 2: Applicable */}
                <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>Applicable</div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', color: 'var(--color-black)', margin: '0.25rem 0' }}>12</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>Statutory Mandates</div>
                </div>

                {/* Metric 3: Due this month */}
                <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>Due This Month</div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', color: 'var(--color-black)', margin: '0.25rem 0' }}>4</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>Sept Filings</div>
                </div>

                {/* Metric 4: Upcoming */}
                <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>Upcoming</div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', color: 'var(--color-black)', margin: '0.25rem 0' }}>7</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>Q3 Obligations</div>
                </div>

                {/* Metric 5: Overdue */}
                <div style={{ padding: '1.25rem', backgroundColor: 'var(--color-brick-light)', border: '1px solid var(--color-border-brick)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-brick)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>Overdue</div>
                  <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', color: 'var(--color-brick)', margin: '0.25rem 0' }}>1</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-brick)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <AlertTriangle size={12} /> Action Needed
                  </div>
                </div>
              </div>

              {/* Upcoming Obligations Section */}
              <div style={{ border: '1px solid var(--color-border)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ padding: '1rem 1.5rem', backgroundColor: 'var(--color-bg)', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-black)' }}>
                    PRIORITY STATUTORY TIMELINE
                  </span>
                  <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)' }}>
                    Auto-synced with GSTN & MCA Portal
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  {[
                    { code: 'GSTR-3B', title: 'Monthly Summary GST Return & Payment', due: 'Due in 3 days', status: 'Urgent', statusBg: 'var(--color-brick-light)', statusColor: 'var(--color-brick)', act: 'Central GST Act, 2017' },
                    { code: 'ESI Monthly', title: 'ESI Contribution Payment & Filing', due: 'Due in 8 days', status: 'Upcoming', statusBg: 'var(--color-bg)', statusColor: 'var(--color-black)', act: 'ESI Act, 1948' },
                    { code: 'MSME-1 Form', title: 'Half-Yearly Dues Return to Micro/Small Vendors', due: 'Due in 21 days', status: 'Scheduled', statusBg: 'var(--color-bg)', statusColor: 'var(--color-muted)', act: 'Companies Act, 2013' }
                  ].map((row, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '1.25rem 1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        borderBottom: idx !== 2 ? '1px solid var(--color-border)' : 'none',
                        backgroundColor: idx === 0 ? '#FCFAF6' : '#FFFFFF'
                      }}
                      className="preview-row"
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '4px', backgroundColor: 'var(--color-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-brick)', fontWeight: 700, fontSize: '0.875rem' }}>
                          <Calendar size={18} />
                        </div>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.9375rem', color: 'var(--color-black)' }}>{row.code}</span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>• {row.act}</span>
                          </div>
                          <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginTop: '0.2rem' }}>{row.title}</div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-black)' }}>{row.due}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>Auto-reminder Active</div>
                        </div>
                        <span
                          style={{
                            fontSize: '0.75rem',
                            fontFamily: 'var(--font-mono)',
                            padding: '0.3rem 0.6rem',
                            backgroundColor: row.statusBg,
                            color: row.statusColor,
                            borderRadius: '3px',
                            fontWeight: 600,
                            minWidth: '75px',
                            textAlign: 'center'
                          }}
                        >
                          {row.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>

          {/* Bottom Interactive Invitation Banner */}
          <div style={{ textAlign: 'center', marginTop: '2.5rem' }}>
            <button
              onClick={onGetStarted}
              className="btn btn-secondary"
              style={{ padding: '0.85rem 2rem', fontSize: '0.9375rem' }}
            >
              Test with your own business profile <ArrowRight size={16} />
            </button>
          </div>

        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .preview-metrics-grid {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          .preview-row {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 1rem !important;
          }
        }
      `}</style>
    </section>
  );
};
