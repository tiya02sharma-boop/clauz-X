import React, { useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  ChevronRight,
  Eye,
  FileText,
  LayoutDashboard,
  Search,
  ShieldCheck,
  Upload,
  X,
  Sparkles,
  ShieldAlert,
  Copy,
  Check,
  Info,
  Scale,
  Download,
  Send,
  MessageCircle,
} from 'lucide-react';

type Status = 'compliant' | 'needs_review' | 'missing_high_risk';

type CheckItem = {
  check_id: string;
  title: string;
  required?: boolean;
  status: Status;
  reason: string;
  explanation?: string;
  risk_assessment?: string;
  suggested_amendment?: string;
  evidence?: string | null;
  matched_terms?: string[];
};

type Contract = {
  id: string;
  filename: string;
  uploaded: string;
  pages: number;
  checks: CheckItem[];
  score: number;
  risk: string;
  aiEnhanced?: boolean;
  aiModel?: string;
  executiveSummary?: string;
  keyRisks?: string[];
  negotiationRecommendations?: string[];
};

const apiBase = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5001';

const statusLabel: Record<Status, string> = {
  compliant: 'Compliant',
  needs_review: 'Needs review',
  missing_high_risk: 'Missing / High risk',
};

const statusStyle: Record<Status, React.CSSProperties> = {
  compliant: { color: '#087443', background: '#e8f8f0', border: '1px solid #c0e8d5' },
  needs_review: { color: '#9a5b00', background: '#fff5d9', border: '1px solid #ffe0a3' },
  missing_high_risk: { color: '#bb2431', background: '#fff0f1', border: '1px solid #ffd0d5' },
};

const seedContracts: Contract[] = [
  {
    id: 'sample-1',
    filename: 'sample_indian_vendor_agreement.pdf',
    uploaded: 'Today',
    pages: 4,
    score: 64,
    risk: 'medium',
    aiEnhanced: true,
    aiModel: 'gemini-3.5-flash',
    executiveSummary:
      'This agreement is a commercial Master Services Agreement between an Indian corporate client and a technology vendor. While basic payment and confidentiality terms are incorporated, the contract lacks mandatory Indian data protection safeguards under the DPDP Act 2023 and exposes the business to uncapped indemnities.',
    keyRisks: [
      'Missing statutory data fiduciary/processor covenants under India’s DPDP Act 2023.',
      'Uncapped indemnification for operational breaches with broad third-party claim exposure.',
      'Ambiguity in GST invoice timelines and separate Income Tax TDS deduction obligations.',
      'Court dispute jurisdiction in a single forum without arbitration under the Arbitration & Conciliation Act 1996.',
    ],
    negotiationRecommendations: [
      'Incorporate a 12-month trailing fee liability cap with standard gross negligence exclusions.',
      'Add a dedicated DPDP 2023 compliance clause with 72-hour breach reporting and deletion upon termination.',
      'Include a mutual 30-day written notice and cure period before unilateral termination.',
      'Add institutional arbitration seated in Mumbai/Bengaluru under Indian law.',
    ],
    checks: [
      {
        check_id: 'party_authority',
        title: 'Parties and signing authority',
        required: true,
        status: 'compliant',
        reason: 'Corporate identities and signing authority signals found.',
        explanation: 'The contract defines both corporate parties along with corporate identification references and authorized signatory blocks.',
        risk_assessment: 'Ensuring signatories hold valid corporate authority mitigates ultra vires challenges under the Companies Act, 2013.',
        suggested_amendment: 'Retain current clause; ensure certified Board Resolution or Power of Attorney is collected on signing.',
        evidence: 'IN WITNESS WHEREOF, the duly authorized representatives of the Parties have executed this Agreement.',
      },
      {
        check_id: 'scope_payment_gst',
        title: 'Scope, payment and GST/TDS',
        required: true,
        status: 'needs_review',
        reason: 'Payment milestones and GST terms found, but TDS mechanism needs clarification.',
        explanation: 'Defines invoicing within 30 days plus applicable GST (rate not specified in the reviewed clause), but omits section references for TDS deduction and credit certificate delivery.',
        risk_assessment: 'Improper TDS handling can result in tax credit mismatches and interest liabilities under Section 194C/194J of the Income Tax Act.',
        suggested_amendment: 'All payments shall be subject to tax deduction at source (TDS) as per the Income Tax Act, 1961, against timely provision of TDS certificates.',
        evidence: 'Client shall pay monthly fees within thirty (30) days of receipt of invoice plus applicable Goods and Services Tax (GST).',
      },
      {
        check_id: 'data_protection_india',
        title: 'India data protection and security',
        required: true,
        status: 'missing_high_risk',
        reason: 'No matching DPDP-aligned data protection clause found.',
        explanation: 'The contract does not designate data fiduciary or data processor obligations, nor does it establish breach response timelines.',
        risk_assessment: 'Processing personal data without mandated DPDP Act 2023 covenants can attract penalties up to INR 250 crores under Section 33.',
        suggested_amendment: 'Service Provider shall process personal data solely to perform services under this Agreement, maintain ISO/IEC 27001 compliant security safeguards, report breaches within 72 hours, and delete all personal data upon contract expiry.',
      },
      {
        check_id: 'indemnity',
        title: 'Indemnity',
        required: true,
        status: 'needs_review',
        reason: 'Indemnity exists but is one-sided in favor of the client.',
        explanation: 'Vendor indemnifies the client for breaches and third-party claims, but the client provides no reciprocal indemnity for materials or IP supplied.',
        risk_assessment: 'Unilateral indemnity exposes the vendor to open-ended legal fees and third-party claims without defense control under Section 124 of Indian Contract Act.',
        suggested_amendment: 'Each Party shall mutually indemnify and defend the other against direct third-party claims arising from gross negligence or infringement of intellectual property.',
        evidence: 'Vendor agrees to indemnify and hold harmless the Client against all claims, losses, and legal costs arising from breach.',
      },
      {
        check_id: 'liability_cap',
        title: 'Limitation of liability',
        required: true,
        status: 'compliant',
        reason: 'Monetary cap and consequential damages exclusion found.',
        explanation: 'Total aggregate liability is capped at fees paid over the previous 12 months, and special/consequential damages are expressly disclaimed.',
        risk_assessment: 'Protects both parties against speculative remote damages under Section 73 of the Indian Contract Act, 1872.',
        suggested_amendment: 'Clause is well balanced and standard for Indian commercial agreements.',
        evidence: 'Neither party shall be liable for indirect or consequential damages. Total liability shall not exceed fees paid in the preceding 12 months.',
      },
      {
        check_id: 'termination',
        title: 'Termination',
        required: true,
        status: 'compliant',
        reason: 'Notice period and breach cure process found.',
        explanation: 'Either party may terminate for convenience with 30 days notice or immediately for uncured material breach following written notice.',
        risk_assessment: 'Standard cure mechanism ensures adequate operational transition time.',
        suggested_amendment: 'Maintain clause; verify that post-termination data return is explicitly linked.',
        evidence: 'Either party may terminate this agreement upon thirty (30) days prior written notice, or upon material breach uncured within 30 days.',
      },
      {
        check_id: 'governing_law',
        title: 'Indian governing law and disputes',
        required: true,
        status: 'compliant',
        reason: 'Indian law and Mumbai court jurisdiction specified.',
        explanation: 'Governed by the laws of India with exclusive jurisdiction in the courts of Mumbai.',
        risk_assessment: 'Clear Indian dispute seat avoids cross-border jurisdictional friction.',
        suggested_amendment: 'Consider adding a fast-track arbitration clause under the Arbitration and Conciliation Act 1996 before municipal court litigation.',
        evidence: 'This Agreement shall be governed by the laws of India, and courts in Mumbai shall have exclusive jurisdiction.',
      },
      {
        check_id: 'confidentiality',
        title: 'Confidentiality',
        required: true,
        status: 'compliant',
        reason: 'Confidentiality and 3-year survival term found.',
        explanation: 'Binds recipient party to secrecy during term and for 3 years post-termination, with standard trade secret exclusions.',
        risk_assessment: 'Sufficient under common law breach of confidence and Indian trade practice.',
        suggested_amendment: 'Standard terms; clarify that proprietary customer lists remain protected indefinitely.',
        evidence: 'Each party shall hold confidential information in strict trust for a period of three (3) years from termination.',
      },
    ],
  },
];

function fromApi(filename: string, data: any): Contract {
  return {
    id: crypto.randomUUID(),
    filename,
    uploaded: 'Just now',
    pages: data.pages || 1,
    score: data.health_score ?? 0,
    risk: data.overall_risk ?? 'high',
    aiEnhanced: data.ai_enhanced ?? false,
    aiModel: data.ai_model,
    executiveSummary: data.executive_summary,
    keyRisks: data.key_risks ?? [],
    negotiationRecommendations: data.negotiation_recommendations ?? [],
    checks: data.results ?? [],
  };
}

function fallback(filename: string): Contract {
  const checks: CheckItem[] = [
    {
      check_id: 'confidentiality',
      title: 'Confidentiality',
      status: 'needs_review',
      reason: 'Backend offline. Start backend on port 5001 for automated analysis.',
      explanation: 'Backend was unreachable during analysis.',
      risk_assessment: 'Unable to evaluate without active backend.',
      suggested_amendment: 'Please re-run analysis once backend is reachable.',
    },
    {
      check_id: 'termination',
      title: 'Termination',
      status: 'needs_review',
      reason: 'Backend offline. Start backend on port 5001 for automated analysis.',
      explanation: 'Backend was unreachable during analysis.',
      risk_assessment: 'Unable to evaluate without active backend.',
      suggested_amendment: 'Please re-run analysis once backend is reachable.',
    },
    {
      check_id: 'indemnity',
      title: 'Indemnity',
      status: 'needs_review',
      reason: 'Backend offline. Start backend on port 5001 for automated analysis.',
      explanation: 'Backend was unreachable during analysis.',
      risk_assessment: 'Unable to evaluate without active backend.',
      suggested_amendment: 'Please re-run analysis once backend is reachable.',
    },
  ];
  return {
    id: crypto.randomUUID(),
    filename,
    uploaded: 'Just now',
    pages: 0,
    score: 0,
    risk: 'needs backend',
    aiEnhanced: false,
    checks,
  };
}

interface ContractDashboardProps {
  embedded?: boolean;
}

export const ContractDashboard: React.FC<ContractDashboardProps> = ({ embedded = false }) => {
  const [contracts, setContracts] = useState<Contract[]>(seedContracts);
  const [selected, setSelected] = useState<Contract | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'missing_high_risk' | 'needs_review' | 'compliant'>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [whatsappModalOpen, setWhatsappModalOpen] = useState(false);
  const [sendingWhatsapp, setSendingWhatsapp] = useState(false);
  const [whatsappPhone, setWhatsappPhone] = useState('+91 8920013753');
  const [whatsappSuccessMsg, setWhatsappSuccessMsg] = useState<string | null>(null);
  const picker = useRef<HTMLInputElement>(null);

  const allChecks = useMemo(() => contracts.flatMap(item => item.checks), [contracts]);
  const clauseTypes = new Set(allChecks.map(item => item.title)).size;

  const copyAmendment = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2200);
  };

  const downloadPdf = async (contract: Contract) => {
    setDownloadingPdf(true);
    setError('');
    try {
      const reportPayload = {
        filename: contract.filename,
        health_score: contract.score,
        overall_risk: contract.risk,
        ai_enhanced: contract.aiEnhanced ?? false,
        ai_model: contract.aiModel || 'Gemini 3.5 Flash',
        executive_summary: contract.executiveSummary || '',
        key_risks: contract.keyRisks || [],
        negotiation_recommendations: contract.negotiationRecommendations || [],
        summary: {
          compliant: contract.checks.filter(c => c.status === 'compliant').length,
          needs_review: contract.checks.filter(c => c.status === 'needs_review').length,
          missing_high_risk: contract.checks.filter(c => c.status === 'missing_high_risk').length,
          total_checks: contract.checks.length,
        },
        results: contract.checks.map(c => ({
          check_id: c.check_id,
          title: c.title,
          required: c.required ?? false,
          status: c.status,
          reason: c.reason,
          explanation: c.explanation || c.reason,
          evidence: c.evidence,
          risk_assessment: c.risk_assessment,
          suggested_amendment: c.suggested_amendment,
        })),
        disclaimer:
          'First-pass automated screening only, not legal advice or contract approval. Have Indian legal counsel approve the playbook and material agreements.',
      };

      const response = await fetch(`${apiBase}/api/contracts/health/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report: reportPayload }),
      });

      if (!response.ok) throw new Error('PDF generation request failed.');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const cleanName = contract.filename.replace(/[^a-zA-Z0-9_\-]/g, '_');
      a.download = `Contract_Health_Report_${cleanName}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not generate PDF report.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const sendWhatsappReport = async (contract: Contract) => {
    if (!whatsappPhone.trim()) {
      setError('Please enter a valid WhatsApp phone number.');
      return;
    }
    setSendingWhatsapp(true);
    setError('');
    setWhatsappSuccessMsg(null);
    try {
      const reportPayload = {
        filename: contract.filename,
        health_score: contract.score,
        overall_risk: contract.risk,
        ai_enhanced: contract.aiEnhanced ?? false,
        ai_model: contract.aiModel || 'Gemini 3.5 Flash',
        executive_summary: contract.executiveSummary || '',
        key_risks: contract.keyRisks || [],
        negotiation_recommendations: contract.negotiationRecommendations || [],
        summary: {
          compliant: contract.checks.filter(c => c.status === 'compliant').length,
          needs_review: contract.checks.filter(c => c.status === 'needs_review').length,
          missing_high_risk: contract.checks.filter(c => c.status === 'missing_high_risk').length,
          total_checks: contract.checks.length,
        },
        results: contract.checks.map(c => ({
          check_id: c.check_id,
          title: c.title,
          required: c.required ?? false,
          status: c.status,
          reason: c.reason,
          explanation: c.explanation || c.reason,
          evidence: c.evidence,
          risk_assessment: c.risk_assessment,
          suggested_amendment: c.suggested_amendment,
        })),
      };

      const response = await fetch(`${apiBase}/api/contracts/health/whatsapp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report: reportPayload, whatsapp_number: whatsappPhone }),
      });

      const resData = await response.json();
      if (!response.ok || !resData.success) {
        throw new Error(resData.error_message || 'WhatsApp report delivery failed.');
      }

      setWhatsappSuccessMsg(`Health Report PDF and executive summary sent to ${whatsappPhone}!`);
      setTimeout(() => {
        setWhatsappModalOpen(false);
      }, 2500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send WhatsApp report.');
    } finally {
      setSendingWhatsapp(false);
    }
  };

  const upload = async (file: File) => {
    if (!/\.(pdf|txt)$/i.test(file.name)) {
      setError('Upload a PDF or TXT contract document.');
      return;
    }
    setUploading(true);
    setError('');
    try {
      let result: any;
      if (/\.txt$/i.test(file.name)) {
        const text = await file.text();
        const response = await fetch(`${apiBase}/api/contracts/health`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename: file.name, contract_text: text, use_ai: true }),
        });
        result = await response.json();
        if (!response.ok) throw new Error(result?.error?.message || 'Could not analyse this contract.');
      } else {
        const form = new FormData();
        form.append('contract', file);
        const response = await fetch(`${apiBase}/api/contracts/health/upload?ai=true`, {
          method: 'POST',
          body: form,
        });
        result = await response.json();
        if (!response.ok) throw new Error(result?.error?.message || 'Could not analyse this contract.');
      }
      const contract = fromApi(file.name, result);
      setContracts(items => [contract, ...items]);
      setSelected(contract);
    } catch (caught) {
      const contract = fallback(file.name);
      setContracts(items => [contract, ...items]);
      setSelected(contract);
      setError(
        caught instanceof Error
          ? `${caught.message} Showing placeholder report; ensure backend is running.`
          : 'Backend unavailable.'
      );
    } finally {
      setUploading(false);
    }
  };

  const filteredChecks = useMemo(() => {
    if (!selected) return [];
    if (filter === 'all') return selected.checks;
    return selected.checks.filter(c => c.status === filter);
  }, [selected, filter]);

  const typeBadges = (contract: Contract) =>
    contract.checks.slice(0, 4).map(check => (
      <span key={check.check_id} className="cg-badge">
        {check.title.replace('India ', '')}
      </span>
    ));

  return (
    <div className="cg-shell" style={embedded ? { minHeight: 'auto', background: 'transparent' } : undefined}>
      {!embedded && (
        <header className="cg-nav">
          <div className="cg-logo">
            <span>
              <ShieldCheck size={16} />
            </span>
            <strong>CLAUZ</strong> <em>X</em>
            <small>CONTRACT HEALTH & AI AUDIT</small>
          </div>
          <nav>
            <button className="active">
              <LayoutDashboard size={14} /> Dashboard
            </button>
            <button onClick={() => picker.current?.click()}>
              <Upload size={14} /> Upload Contract
            </button>
            <button>
              <Search size={14} /> Search
            </button>
          </nav>
        </header>
      )}

      <main className="cg-main" style={embedded ? { padding: '1rem 0 2rem', maxWidth: '100%' } : undefined}>
        <div className="cg-title">
          <div>
            <div className="eyebrow" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={13} style={{ color: 'var(--color-brick)' }} />
              Gemini AI-Powered Contract Review
            </div>
            <h1>Your contract portfolio.</h1>
            <p>
              Screen commercial agreements against 14 standard Indian legal checks with Gemini AI clause explanations,
              risk assessments, and actionable negotiation playbooks.
            </p>
          </div>
          <button className="cg-primary" onClick={() => picker.current?.click()} disabled={uploading}>
            {uploading ? (
              <>
                <Sparkles size={15} className="animate-spin" /> Analysing with Gemini…
              </>
            ) : (
              <>
                <Upload size={15} /> Upload Contract
              </>
            )}
          </button>
          <input
            ref={picker}
            hidden
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            onChange={event => {
              const file = event.target.files?.[0];
              if (file) upload(file);
              event.currentTarget.value = '';
            }}
          />
        </div>

        {error && (
          <div className="cg-error">
            <AlertTriangle size={15} /> {error}
            <button onClick={() => setError('')}>
              <X size={14} />
            </button>
          </div>
        )}

        <section className="cg-stats">
          <Stat icon="▧" title="Contracts" value={contracts.length} color="var(--color-brick-light)" />
          <Stat icon="☷" title="Clauses Extracted" value={allChecks.length} color="var(--color-beige-light)" />
          <Stat icon="◇" title="Clause Types" value={clauseTypes} color="var(--color-brick-light)" />
          <Stat
            icon="▤"
            title="Pages Analysed"
            value={contracts.reduce((sum, item) => sum + item.pages, 0)}
            color="var(--color-beige-light)"
          />
        </section>

        <section className="cg-card">
          <div className="cg-card-head">
            <div>
              <h2>Contract Reviews</h2>
              <p>
                {contracts.length} contract{contracts.length === 1 ? '' : 's'} analysed
              </p>
            </div>
            <button className="cg-upload-small" onClick={() => picker.current?.click()}>
              <Upload size={14} /> Upload New
            </button>
          </div>

          <div className="cg-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Analysis</th>
                  <th>Uploaded</th>
                  <th>Health Score</th>
                  <th>Overall Risk</th>
                  <th>Extracted Clauses</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {contracts.map(contract => (
                  <tr key={contract.id}>
                    <td className="cg-file">
                      <FileText size={14} /> {contract.filename}
                    </td>
                    <td>
                      {contract.aiEnhanced ? (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            background: '#f4ebff',
                            color: '#6927da',
                            padding: '3px 8px',
                            borderRadius: '12px',
                            fontSize: '10px',
                            fontWeight: 700,
                            border: '1px solid #d8b4fe',
                          }}
                        >
                          <Sparkles size={11} /> Gemini 3.5 AI
                        </span>
                      ) : (
                        <span style={{ fontSize: '10px', color: 'var(--color-muted)' }}>Keyword Rule</span>
                      )}
                    </td>
                    <td>{contract.uploaded}</td>
                    <td>
                      <span
                        style={{
                          fontWeight: 700,
                          fontSize: '13px',
                          color:
                            contract.score >= 70 ? '#087443' : contract.score >= 40 ? '#9a5b00' : '#bb2431',
                        }}
                      >
                        {contract.score}%
                      </span>
                    </td>
                    <td>
                      <span
                        style={{
                          textTransform: 'capitalize',
                          fontWeight: 600,
                          fontSize: '11px',
                          color:
                            contract.risk === 'low'
                              ? '#087443'
                              : contract.risk === 'medium'
                              ? '#9a5b00'
                              : '#bb2431',
                        }}
                      >
                        {contract.risk}
                      </span>
                    </td>
                    <td>
                      <div className="cg-types">
                        {typeBadges(contract)}
                        {contract.checks.length > 4 && (
                          <span className="cg-more">+{contract.checks.length - 4}</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <button className="cg-view" onClick={() => setSelected(contract)}>
                        <Eye size={14} /> View
                      </button>
                      <button
                        className="cg-view"
                        onClick={(e) => { e.stopPropagation(); downloadPdf(contract); }}
                        title="Download structured PDF"
                      >
                        <Download size={13} /> PDF
                      </button>
                      <button className="cg-review" onClick={() => setSelected(contract)}>
                        Report <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <p className="cg-note">
          Automated legal screening and AI analysis based on Indian commercial contracting standards. It does not
          constitute legal advice or contract approval.
        </p>
      </main>

      {/* Contract Health Report Drawer/Modal */}
      {selected && (
        <div className="cg-modal-bg" onClick={() => setSelected(null)}>
          <aside
            className="cg-report"
            style={{ width: 'min(780px, 100vw)' }}
            onClick={event => event.stopPropagation()}
          >
            {/* Header */}
            <div className="cg-report-head">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <p style={{ margin: 0 }}>CONTRACT HEALTH REPORT</p>
                  {selected.aiEnhanced && (
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        background: '#f4ebff',
                        color: '#6927da',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '10px',
                        fontWeight: 700,
                        border: '1px solid #d8b4fe',
                      }}
                    >
                      <Sparkles size={11} /> Gemini 3.5 Flash AI
                    </span>
                  )}
                </div>
                <h2>{selected.filename}</h2>
                <div style={{ display: 'flex', gap: '14px', alignItems: 'center', fontSize: '13px' }}>
                  <span>
                    Health score:{' '}
                    <b
                      style={{
                        color:
                          selected.score >= 70 ? '#087443' : selected.score >= 40 ? '#9a5b00' : '#bb2431',
                      }}
                    >
                      {selected.score}%
                    </b>
                  </span>
                  <span>
                    Overall Risk:{' '}
                    <b
                      style={{
                        textTransform: 'capitalize',
                        color:
                          selected.risk === 'low'
                            ? '#087443'
                            : selected.risk === 'medium'
                            ? '#9a5b00'
                            : '#bb2431',
                      }}
                    >
                      {selected.risk}
                    </b>
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  onClick={() => {
                    setWhatsappSuccessMsg(null);
                    setWhatsappModalOpen(true);
                  }}
                  disabled={sendingWhatsapp}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    background: '#25D366',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '7px 12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                  title="Send executive summary and PDF download link via WhatsApp"
                >
                  <MessageCircle size={13} />
                  Send to WhatsApp
                </button>

                <button
                  onClick={() => downloadPdf(selected)}
                  disabled={downloadingPdf}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    background: 'var(--color-brick)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '7px 12px',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  }}
                  title="Download complete structured PDF audit report"
                >
                  <Download size={13} />
                  {downloadingPdf ? 'Generating PDF…' : 'Download PDF Report'}
                </button>
                <button onClick={() => setSelected(null)}>
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Summary counters */}
            <div className="cg-report-summary">
              <span>✅ {selected.checks.filter(item => item.status === 'compliant').length} Compliant</span>
              <span>⚠️ {selected.checks.filter(item => item.status === 'needs_review').length} Needs review</span>
              <span>❌ {selected.checks.filter(item => item.status === 'missing_high_risk').length} Missing / high risk</span>
            </div>

            {/* Executive Summary Card */}
            {selected.executiveSummary && (
              <div
                style={{
                  margin: '18px 0',
                  padding: '16px 18px',
                  background: 'var(--color-bg)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    color: 'var(--color-brick)',
                    fontWeight: 700,
                    marginBottom: '8px',
                  }}
                >
                  <Sparkles size={13} /> Executive Legal Summary
                </div>
                <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6', color: 'var(--color-black)' }}>
                  {selected.executiveSummary}
                </p>
              </div>
            )}

            {/* Key Risks & Red Flags */}
            {selected.keyRisks && selected.keyRisks.length > 0 && (
              <div
                style={{
                  marginBottom: '18px',
                  padding: '16px 18px',
                  background: '#fff8f8',
                  border: '1px solid #ffd0d5',
                  borderRadius: '6px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    color: '#bb2431',
                    fontWeight: 700,
                    marginBottom: '10px',
                  }}
                >
                  <ShieldAlert size={14} /> Key Legal Risks & Red Flags
                </div>
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', lineHeight: '1.55', color: '#5a1018' }}>
                  {selected.keyRisks.map((risk, idx) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Negotiation Recommendations */}
            {selected.negotiationRecommendations && selected.negotiationRecommendations.length > 0 && (
              <div
                style={{
                  marginBottom: '18px',
                  padding: '16px 18px',
                  background: '#f9f8f4',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    color: 'var(--color-brick)',
                    fontWeight: 700,
                    marginBottom: '10px',
                  }}
                >
                  <Scale size={14} /> Actionable Negotiation Recommendations
                </div>
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', lineHeight: '1.55', color: 'var(--color-black)' }}>
                  {selected.negotiationRecommendations.map((rec, idx) => (
                    <li key={idx} style={{ marginBottom: '5px' }}>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Clause Filter Tabs */}
            <div
              style={{
                display: 'flex',
                gap: '8px',
                margin: '18px 0 10px',
                paddingBottom: '8px',
                borderBottom: '1px solid var(--color-border)',
              }}
            >
              {(
                [
                  { id: 'all', label: `All Checks (${selected.checks.length})` },
                  {
                    id: 'missing_high_risk',
                    label: `High Risk (${selected.checks.filter(c => c.status === 'missing_high_risk').length})`,
                  },
                  {
                    id: 'needs_review',
                    label: `Needs Review (${selected.checks.filter(c => c.status === 'needs_review').length})`,
                  },
                  {
                    id: 'compliant',
                    label: `Compliant (${selected.checks.filter(c => c.status === 'compliant').length})`,
                  },
                ] as const
              ).map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setFilter(tab.id)}
                  style={{
                    border: '1px solid',
                    borderColor: filter === tab.id ? 'var(--color-brick)' : 'var(--color-border)',
                    background: filter === tab.id ? 'var(--color-brick-light)' : 'transparent',
                    color: filter === tab.id ? 'var(--color-brick)' : 'var(--color-muted)',
                    fontWeight: filter === tab.id ? 700 : 500,
                    padding: '5px 10px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    cursor: 'pointer',
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Clauses breakdown */}
            <div className="cg-checks">
              {filteredChecks.map(check => (
                <div
                  className="cg-check"
                  key={check.check_id}
                  style={{
                    padding: '16px',
                    marginBottom: '12px',
                    background: 'var(--color-card-bg)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '8px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="cg-status" style={statusStyle[check.status]}>
                        {statusLabel[check.status]}
                      </span>
                      {check.required && (
                        <span
                          style={{
                            fontSize: '10px',
                            fontFamily: 'var(--font-mono)',
                            color: 'var(--color-muted)',
                            textTransform: 'uppercase',
                          }}
                        >
                          Required Core Check
                        </span>
                      )}
                    </div>
                  </div>

                  <h3 style={{ margin: '4px 0 8px', fontSize: '15px' }}>{check.title}</h3>

                  {/* Quoted evidence from the contract if found */}
                  {check.evidence && (
                    <blockquote
                      style={{
                        margin: '8px 0 10px',
                        padding: '8px 12px',
                        background: '#f7f6f2',
                        borderLeft: '3px solid var(--color-brick)',
                        fontSize: '11.5px',
                        fontStyle: 'italic',
                        color: 'var(--color-black)',
                        borderRadius: '0 4px 4px 0',
                      }}
                    >
                      “{check.evidence}”
                    </blockquote>
                  )}

                  {/* Plain-English Explanation */}
                  <div style={{ margin: '10px 0 6px' }}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        fontSize: '11px',
                        fontWeight: 700,
                        color: 'var(--color-black)',
                        marginBottom: '3px',
                      }}
                    >
                      <Info size={13} style={{ color: 'var(--color-brick)' }} />
                      Detailed Explanation:
                    </div>
                    <p style={{ margin: 0, fontSize: '12.5px', lineHeight: '1.5', color: '#333' }}>
                      {check.explanation || check.reason}
                    </p>
                  </div>

                  {/* Risk Assessment under Indian law */}
                  {check.risk_assessment && (
                    <div
                      style={{
                        marginTop: '8px',
                        padding: '8px 10px',
                        background: check.status === 'compliant' ? '#f0fdf4' : '#fff9f0',
                        borderLeft: `3px solid ${
                          check.status === 'compliant'
                            ? '#087443'
                            : check.status === 'needs_review'
                            ? '#9a5b00'
                            : '#bb2431'
                        }`,
                        borderRadius: '0 4px 4px 0',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          color:
                            check.status === 'compliant'
                              ? '#087443'
                              : check.status === 'needs_review'
                              ? '#9a5b00'
                              : '#bb2431',
                          marginBottom: '2px',
                        }}
                      >
                        ⚖️ Indian Legal Risk & Impact:
                      </div>
                      <p style={{ margin: 0, fontSize: '12px', lineHeight: '1.45', color: '#444' }}>
                        {check.risk_assessment}
                      </p>
                    </div>
                  )}

                  {/* Suggested Amendment / Negotiation Language */}
                  {check.suggested_amendment && (
                    <div
                      style={{
                        marginTop: '10px',
                        padding: '10px 12px',
                        background: '#f8f9fa',
                        border: '1px dashed var(--color-border)',
                        borderRadius: '5px',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          marginBottom: '4px',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: 700,
                            color: 'var(--color-brick)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                        >
                          <Scale size={12} /> Suggested Amendment / Negotiation Tip:
                        </span>
                        <button
                          onClick={() => copyAmendment(check.check_id, check.suggested_amendment || '')}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            border: '1px solid var(--color-border)',
                            background: '#fff',
                            borderRadius: '3px',
                            padding: '2px 7px',
                            fontSize: '10px',
                            cursor: 'pointer',
                            color: copiedId === check.check_id ? '#087443' : 'var(--color-black)',
                          }}
                          title="Copy suggested clause"
                        >
                          {copiedId === check.check_id ? (
                            <>
                              <Check size={11} /> Copied!
                            </>
                          ) : (
                            <>
                              <Copy size={11} /> Copy
                            </>
                          )}
                        </button>
                      </div>
                      <p
                        style={{
                          margin: 0,
                          fontSize: '11.5px',
                          lineHeight: '1.45',
                          fontFamily: 'var(--font-mono, monospace)',
                          color: '#222',
                        }}
                      >
                        {check.suggested_amendment}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </aside>
        </div>
      )}

      {/* WhatsApp Delivery Modal */}
      {whatsappModalOpen && selected && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
          onClick={() => !sendingWhatsapp && setWhatsappModalOpen(false)}
        >
          <div
            style={{
              background: '#fff',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '440px',
              padding: '24px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              position: 'relative',
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#E8F5E9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <MessageCircle size={18} color="#25D366" />
                </div>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#111827' }}>
                  Send Report via WhatsApp
                </h3>
              </div>
              <button
                onClick={() => setWhatsappModalOpen(false)}
                disabled={sendingWhatsapp}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6B7280', padding: '4px' }}
              >
                <X size={18} />
              </button>
            </div>

            <p style={{ fontSize: '13px', color: '#4B5563', marginTop: 0, marginBottom: '16px', lineHeight: 1.5 }}>
              Send the <b>Contract Health Audit Summary</b> and instant <b>PDF Download Link</b> for <i>{selected.filename}</i> to WhatsApp.
            </p>

            {whatsappSuccessMsg ? (
              <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '8px', padding: '12px 14px', color: '#065F46', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <Check size={16} />
                {whatsappSuccessMsg}
              </div>
            ) : (
              <>
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>
                    Recipient WhatsApp Number
                  </label>
                  <input
                    type="text"
                    value={whatsappPhone}
                    onChange={e => setWhatsappPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    disabled={sendingWhatsapp}
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: '6px',
                      border: '1px solid #D1D5DB',
                      fontSize: '14px',
                      fontFamily: 'monospace',
                      boxSizing: 'border-box',
                    }}
                  />
                  <span style={{ fontSize: '11px', color: '#6B7280', marginTop: '4px', display: 'block' }}>
                    Include country code (e.g. +91 for India).
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '20px' }}>
                  <button
                    onClick={() => setWhatsappModalOpen(false)}
                    disabled={sendingWhatsapp}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '6px',
                      border: '1px solid #D1D5DB',
                      background: '#fff',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: '#374151',
                      cursor: 'pointer',
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => sendWhatsappReport(selected)}
                    disabled={sendingWhatsapp}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '6px',
                      border: 'none',
                      background: '#25D366',
                      fontSize: '13px',
                      fontWeight: 700,
                      color: '#fff',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    {sendingWhatsapp ? (
                      <>Sending Report…</>
                    ) : (
                      <>
                        <Send size={14} /> Send WhatsApp Report
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const Stat = ({ icon, title, value, color }: { icon: string; title: string; value: number; color: string }) => (
  <div className="cg-stat">
    <span style={{ background: color }}>{icon}</span>
    <div>
      <p>{title}</p>
      <b>{value}</b>
    </div>
  </div>
);
