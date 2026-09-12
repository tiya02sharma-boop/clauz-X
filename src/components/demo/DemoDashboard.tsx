import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Calendar,
  MessageSquare,
  FileText,
  AlertTriangle,
  ArrowRight,
  Send,
  RefreshCw
} from 'lucide-react';
import { ContractDashboard } from '../ContractDashboard';
import type { BusinessProfile } from '../../types';
import {
  samplePredefinedQuestions
} from '../../data/mockComplianceData';

interface DemoDashboardProps {
  profile: BusinessProfile;
  onEditProfile: () => void;
  onBackToLanding: () => void;
}

type TabKey = 'overview' | 'obligations' | 'calendar' | 'verify' | 'ask';

type LiveObligation = {
  id: string;
  code: string;
  title: string;
  act: string;
  section: string;
  category: string;
  frequency: string;
  nextDueDate: string;
  daysRemaining: number;
  status: string;
  applicabilityReason: string;
  penaltyRisk: string;
  sourceUrl?: string;
};

const apiBase = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5001';

const parseNumericValue = (value: unknown): number | null => {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value !== 'string') return null;
  const cleaned = value.trim();
  if (!cleaned) return null;
  
  // Range like "20 - 49 Employees" or "50 - 100"
  const rangeMatch = cleaned.match(/(\d+)\s*[-–]\s*(\d+)/);
  if (rangeMatch) {
    return parseInt(rangeMatch[1], 10);
  }
  // "100+ Employees"
  const plusMatch = cleaned.match(/(\d+)\s*\+/);
  if (plusMatch) {
    return parseInt(plusMatch[1], 10);
  }
  // Crore
  const crMatch = cleaned.match(/([\d.]+)\s*(?:Cr|Crore)/i);
  if (crMatch) {
    return parseFloat(crMatch[1]) * 10000000;
  }
  // Lakh
  const lakhMatch = cleaned.match(/([\d.]+)\s*(?:Lakh|Lac)/i);
  if (lakhMatch) {
    return parseFloat(lakhMatch[1]) * 100000;
  }
  // First number
  const numMatch = cleaned.match(/\d+/);
  if (numMatch) {
    return parseInt(numMatch[0], 10);
  }
  return null;
};

const deriveCategory = (rule: any): 'Tax & GST' | 'Labor & Social Security' | 'Corporate & ROC' | 'MSME Specific' => {
  const text = `${rule.obligation_name || rule.name || ''} ${rule.description || ''} ${rule.source_title || ''} ${rule.source_citation || ''} ${rule.rule_id || rule.obligation_id || ''}`.toLowerCase();
  if (text.includes('gst') || text.includes('tds') || text.includes('tax') || text.includes('income tax')) {
    return 'Tax & GST';
  }
  if (text.includes('epf') || text.includes('esi') || text.includes('provident') || text.includes('employee') || text.includes('labor') || text.includes('labour')) {
    return 'Labor & Social Security';
  }
  if (text.includes('company') || text.includes('roc') || text.includes('mca') || text.includes('director') || text.includes('annual return') || text.includes('private limited')) {
    return 'Corporate & ROC';
  }
  return 'MSME Specific';
};

const computeClientMsmeClassification = (
  investment: number | string | undefined | null,
  turnover: string | number | undefined | null
): 'Micro' | 'Small' | 'Medium' | 'Not MSME' => {
  const inv = typeof investment === 'number' ? investment : parseNumericValue(investment);
  const to = typeof turnover === 'number' ? turnover : parseNumericValue(turnover);
  if (inv === null || to === null) return 'Not MSME';
  if (inv <= 25000000 && to <= 100000000) return 'Micro';
  if (inv <= 250000000 && to <= 1000000000) return 'Small';
  if (inv <= 1250000000 && to <= 5000000000) return 'Medium';
  return 'Not MSME';
};

export const DemoDashboard: React.FC<DemoDashboardProps> = ({
  profile,
  onEditProfile,
  onBackToLanding
}) => {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [obligations, setObligations] = useState<LiveObligation[]>([]);
  const [rulesState, setRulesState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [msmeClassification, setMsmeClassification] = useState<string>(() =>
    profile.msmeClassification || computeClientMsmeClassification(profile.investmentPlantMachinery, profile.turnover)
  );
  
  // Ask Clauz X State
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'assistant'; text: string; sources?: Array<{title: string; citation: string; source_url?: string}> }>>([
    {
      sender: 'assistant',
      text: `Hello! I am your regulatory compliance assistant for ${profile.businessName}. You can ask any question regarding GST deadlines, ESI/PF thresholds, MCA filings, or MSME vendor dues.`,
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    const payload = {
      business_name: profile.businessName,
      turnover: parseNumericValue(profile.turnover),
      headcount: parseNumericValue(profile.headcount),
      investment_plant_machinery: typeof profile.investmentPlantMachinery === 'number'
        ? profile.investmentPlantMachinery
        : parseNumericValue(profile.investmentPlantMachinery),
      is_factory: typeof profile.isFactory === 'boolean' ? profile.isFactory : false,
      sector: profile.sector,
      state: profile.state,
      entity_type: profile.entityType ? profile.entityType.toLowerCase().replace(/\s+/g, '_') : null,
      gst_registered: profile.gstRegistered,
      gst_filing_scheme: profile.gstFilingScheme || 'unknown',
      agm_date: profile.agmDate || null,
      whatsapp_number: profile.whatsappNumber || '+919896603656'
    };

    fetch(`${apiBase}/api/compliance/businesses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal
    })
      .then(async response => {
        if (!response.ok) {
          const fallbackResp = await fetch(`${apiBase}/api/applicability/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal
          });
          if (!fallbackResp.ok) throw new Error('API request failed');
          return fallbackResp.json();
        }
        return response.json();
      })
      .then(data => {
        const retProf = data.profile || data.business;
        if (retProf?.msme_classification) {
          setMsmeClassification(retProf.msme_classification);
        }
        const rawList = data.obligations || data.applicable_obligations || [];
        const mapped = rawList.map((rule: any): LiveObligation => {
          const cat = deriveCategory(rule);
          const nextDue = rule.next_due || rule.due_day_rule || 'Schedule not specified';
          let daysRemaining = 0;
          let isOverdue = false;
          if (rule.next_due) {
            const today = new Date();
            const todayUtc = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
            const dueParts = rule.next_due.split('-');
            const dueUtc = Date.UTC(parseInt(dueParts[0]), parseInt(dueParts[1]) - 1, parseInt(dueParts[2]));
            const diffDays = Math.ceil((dueUtc - todayUtc) / (1000 * 60 * 60 * 24));
            daysRemaining = diffDays;
            if (diffDays < 0) {
              isOverdue = true;
            }
          }
          const isUrgent = !isOverdue && daysRemaining >= 0 && daysRemaining <= 7;
          return {
            id: rule.obligation_id || rule.rule_id || Math.random().toString(),
            code: rule.name || rule.obligation_name || rule.obligation_id || rule.rule_id,
            title: rule.description || rule.name || rule.obligation_name || 'Approved compliance obligation',
            act: rule.source_citation || rule.source_title || 'Approved regulatory source',
            section: rule.source_citation || 'Statutory mandate',
            category: cat,
            frequency: rule.recurrence ? rule.recurrence.charAt(0).toUpperCase() + rule.recurrence.slice(1) : 'Monthly',
            nextDueDate: nextDue,
            daysRemaining: daysRemaining,
            status: isOverdue ? 'Overdue' : (isUrgent ? 'Urgent' : (daysRemaining > 7 ? 'Upcoming' : 'Compliant')),
            applicabilityReason: rule.reason || 'Matches your entity type and registration parameters.',
            penaltyRisk: rule.penalty_formula || 'Statutory late fee & interest apply.',
            sourceUrl: rule.source_url
          };
        });
        setObligations(mapped);
        setRulesState('ready');
      })
      .catch(error => {
        if (error.name !== 'AbortError') {
          console.error('Fetch error:', error);
          setRulesState('error');
        }
      });
    return () => controller.abort();
  }, [profile]);

  // Filter obligations by selected category
  const filteredObligations = selectedCategory === 'All'
    ? obligations
    : obligations.filter(o => o.category === selectedCategory);

  // Dynamic metrics derived from live obligations
  const totalObligations = obligations.length;
  const overdueList = obligations.filter(o => o.daysRemaining < 0 || o.status === 'Overdue');
  const urgentList = obligations.filter(o => o.status === 'Urgent');
  const overdueCount = overdueList.length;
  const urgentCount = urgentList.length;
  const actionNeededCount = overdueCount + urgentCount;

  const goodStandingCount = Math.max(0, totalObligations - overdueCount);
  const complianceHealth = totalObligations > 0
    ? Math.round((goodStandingCount / totalObligations) * 100)
    : 100;

  const currentDate = new Date();
  const currentMonthYear = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
  const currentMonthName = currentDate.toLocaleString('en-IN', { month: 'long' });
  const dueThisMonthList = obligations.filter(o => o.nextDueDate && o.nextDueDate.startsWith(currentMonthYear));
  const dueThisMonthCount = dueThisMonthList.length;

  const primaryActionItem = overdueList[0] || urgentList[0];

  // Closest deadlines first for priority view
  const sortedUpcoming = [...obligations].sort((a, b) => a.daysRemaining - b.daysRemaining).slice(0, 4);

  // Forward schedule calendar title
  const nextMonthDate = new Date();
  nextMonthDate.setMonth(nextMonthDate.getMonth() + 1);
  const nextMonthName = nextMonthDate.toLocaleString('en-IN', { month: 'long', year: 'numeric' });
  const calendarScheduleTitle = `${currentMonthName} - ${nextMonthName} Statutory Schedule`;
  const scheduledDatesCount = obligations.filter(o => o.nextDueDate && o.nextDueDate !== 'Schedule not specified' && !o.nextDueDate.includes('Needs manual')).length;

  const handleAskQuestion = async (qText: string) => {
    if (!qText.trim() || isAsking) return;
    setMessages(prev => [...prev, { sender: 'user', text: qText }]);
    setInputQuestion('');
    setIsAsking(true);
    try {
      const response = await fetch(`${apiBase}/api/ask`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: qText }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.error?.message || 'The assistant is unavailable right now.');
      setMessages(prev => [...prev, { sender: 'assistant', text: data.answer, sources: data.sources }]);
    } catch (error) {
      setMessages(prev => [...prev, { sender: 'assistant', text: error instanceof Error ? error.message : 'The assistant is unavailable right now.' }]);
    } finally { setIsAsking(false); }
  };

  return (
    <div style={{ backgroundColor: 'var(--color-bg)', minHeight: '100vh', paddingBottom: '6rem' }}>
      
      {/* Top Demo Bar */}
      <div style={{ backgroundColor: 'var(--color-black)', color: '#FFFFFF', padding: '0.65rem 0', fontSize: '0.8125rem' }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ padding: '0.15rem 0.5rem', backgroundColor: 'var(--color-brick)', borderRadius: '3px', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '0.6875rem' }}>
              DEMO MODE
            </span>
            <span>Simulating active compliance cockpit for <strong>{profile.businessName}</strong></span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <button
              onClick={onEditProfile}
              style={{ background: 'none', border: 'none', color: 'var(--color-beige)', cursor: 'pointer', fontSize: '0.8125rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
            >
              <RefreshCw size={12} /> Edit Profile Parameters
            </button>
            <button
              onClick={onBackToLanding}
              style={{ background: 'none', border: 'none', color: '#FFFFFF', cursor: 'pointer', fontSize: '0.8125rem', textDecoration: 'underline' }}
            >
              Exit Demo
            </button>
          </div>
        </div>
      </div>

      <div className="container" style={{ paddingTop: '2.5rem' }}>
        
        {/* Dashboard Title Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: '0.4rem' }}>
              COMPLIANCE COCKPIT
            </div>
            <h1 style={{ fontSize: 'clamp(2rem, 3.5vw, 2.75rem)', color: 'var(--color-black)', letterSpacing: '-0.02em', marginBottom: '0.35rem' }}>
              Good morning, {profile.businessName}.
            </h1>
            <p style={{ fontSize: '1rem', color: 'var(--color-muted)', marginBottom: '0.75rem' }}>
              Here's your real-time compliance overview tailored for a <strong style={{ color: 'var(--color-black)' }}>{profile.entityType}</strong> in <strong style={{ color: 'var(--color-black)' }}>{profile.state}</strong>.
            </p>

            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '0.25rem 0.65rem', backgroundColor: 'var(--color-brick-light)', border: '1px solid var(--color-brick)', borderRadius: '4px', color: 'var(--color-brick)', fontWeight: 700 }}>
                MSME Classification: {msmeClassification} {msmeClassification !== 'Not MSME' ? 'Enterprise' : ''}
              </span>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '0.25rem 0.65rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', color: 'var(--color-black)', fontWeight: 500 }}>
                Regime: {profile.isFactory ? 'Factory (Factories Act 1948)' : 'Commercial Establishment (Shops & Est. Act)'}
              </span>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '0.25rem 0.65rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', color: 'var(--color-muted)' }}>
                Turnover: {profile.turnover}
              </span>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '0.25rem 0.65rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', color: 'var(--color-muted)' }}>
                Investment: ₹{Number(profile.investmentPlantMachinery || 0).toLocaleString('en-IN')}
              </span>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '0.25rem 0.65rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', color: 'var(--color-muted)' }}>
                Workforce: {profile.headcount}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={() => setActiveTab('ask')}
              className="btn btn-brick"
              style={{ fontSize: '0.875rem', padding: '0.65rem 1.25rem' }}
            >
              <MessageSquare size={16} /> Ask Clauz X
            </button>
          </div>
        </div>

        {/* Dashboard Navigation Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--color-border)', marginBottom: '2.5rem', overflowX: 'auto', paddingBottom: '2px' }}>
          {[
            { key: 'overview', label: 'Overview', icon: ShieldCheck },
            { key: 'obligations', label: `Applicable Obligations (${obligations.length})`, icon: FileText },
            { key: 'calendar', label: 'Compliance Calendar', icon: Calendar },
            { key: 'verify', label: 'Contract Health Report', icon: ShieldCheck },
            { key: 'ask', label: 'Ask Clauz X (AI)', icon: MessageSquare }
          ].map(t => {
            const IconC = t.icon;
            const isSel = activeTab === t.key;
            return (
              <button
                key={t.key}
                onClick={() => setActiveTab(t.key as TabKey)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.75rem 1.25rem',
                  backgroundColor: isSel ? '#FFFFFF' : 'transparent',
                  border: isSel ? '1px solid var(--color-border)' : '1px solid transparent',
                  borderBottom: isSel ? '1px solid #FFFFFF' : '1px solid transparent',
                  borderRadius: '4px 4px 0 0',
                  color: isSel ? 'var(--color-brick)' : 'var(--color-muted)',
                  fontWeight: isSel ? 700 : 500,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  marginBottom: '-1px',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease'
                }}
              >
                <IconC size={16} />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>

        {/* =========================================================
            TAB 1: OVERVIEW
           ========================================================= */}
        {activeTab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', animation: 'fadeIn 0.25s ease-out' }}>
            
            {/* Top Stat Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem' }} className="dash-metrics-grid">
              
              {/* Compliance Health */}
              <div style={{ padding: '1.75rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-subtle)' }}>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)', textTransform: 'uppercase' }}>Compliance Health</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2.5rem', color: complianceHealth >= 80 ? 'var(--color-brick)' : 'var(--color-brick)', margin: '0.35rem 0' }}>
                  {rulesState === 'loading' ? '…' : `${complianceHealth}%`}
                </div>
                <div style={{ fontSize: '0.8125rem', color: complianceHealth >= 80 ? 'green' : 'var(--color-brick)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span>●</span> {rulesState === 'loading' ? 'Evaluating obligations…' : `${goodStandingCount} of ${totalObligations} in good standing`}
                </div>
              </div>

              {/* Applicable */}
              <div style={{ padding: '1.75rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-subtle)' }}>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)', textTransform: 'uppercase' }}>Applicable Obligations</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2.5rem', color: 'var(--color-black)', margin: '0.35rem 0' }}>{rulesState === 'loading' ? '…' : totalObligations}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)' }}>
                  {rulesState === 'loading' ? 'Matching rules…' : `${new Set(obligations.map(o => o.category)).size} statutory categories matched`}
                </div>
              </div>

              {/* Due this Month */}
              <div style={{ padding: '1.75rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-subtle)' }}>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)', textTransform: 'uppercase' }}>Due This Month</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2.5rem', color: 'var(--color-black)', margin: '0.35rem 0' }}>{rulesState === 'loading' ? '…' : dueThisMonthCount}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)' }}>
                  {currentMonthName} statutory filings
                </div>
              </div>

              {/* Overdue / Action Needed */}
              <div style={{ padding: '1.75rem', backgroundColor: actionNeededCount > 0 ? 'var(--color-brick-light)' : 'var(--color-bg)', border: actionNeededCount > 0 ? '1px solid var(--color-border-brick)' : '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: actionNeededCount > 0 ? 'var(--color-brick)' : 'var(--color-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Action Needed / Overdue</div>
                <div style={{ fontFamily: 'var(--font-serif)', fontSize: '2.5rem', color: actionNeededCount > 0 ? 'var(--color-brick)' : 'var(--color-black)', margin: '0.35rem 0' }}>
                  {rulesState === 'loading' ? '…' : actionNeededCount}
                </div>
                <div style={{ fontSize: '0.8125rem', color: actionNeededCount > 0 ? 'var(--color-brick)' : 'green', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  {rulesState === 'loading' ? (
                    'Checking deadlines…'
                  ) : primaryActionItem ? (
                    <>
                      <AlertTriangle size={14} /> {primaryActionItem.code}: {primaryActionItem.status === 'Overdue' ? `${Math.abs(primaryActionItem.daysRemaining)}d overdue` : `Due in ${primaryActionItem.daysRemaining}d`}
                    </>
                  ) : (
                    <>✓ All deadlines on schedule</>
                  )}
                </div>
              </div>

            </div>

            {/* Upcoming Priority Obligations */}
            <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '2rem', boxShadow: 'var(--shadow-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--color-border)' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--color-black)', letterSpacing: '-0.01em' }}>Upcoming Statutory Deadlines</h3>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)' }}>Priority items needing attention over the next 30 days</p>
                </div>
                <button
                  onClick={() => setActiveTab('obligations')}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.8125rem', padding: '0.45rem 0.85rem' }}
                >
                  View All {obligations.length} Obligations →
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {sortedUpcoming.map((obl) => (
                  <div
                    key={obl.id}
                    style={{
                      padding: '1.25rem 1.5rem',
                      backgroundColor: obl.status === 'Urgent' || obl.status === 'Overdue' ? 'var(--color-brick-light)' : 'var(--color-bg)',
                      border: obl.status === 'Urgent' || obl.status === 'Overdue' ? '1px solid var(--color-border-brick)' : '1px solid var(--color-border)',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '1rem'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
                        <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--color-black)' }}>{obl.code}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>• {obl.act}</span>
                        <span style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', padding: '0.15rem 0.4rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '2px' }}>
                          {obl.category}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--color-black)', fontWeight: 500 }}>{obl.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginTop: '0.25rem' }}>
                        Section: {obl.section}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.875rem', fontWeight: 700, color: obl.status === 'Urgent' || obl.status === 'Overdue' ? 'var(--color-brick)' : 'var(--color-black)' }}>
                          {obl.nextDueDate}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: obl.status === 'Urgent' || obl.status === 'Overdue' ? 'var(--color-brick)' : 'var(--color-muted)', fontWeight: 600 }}>
                          {obl.daysRemaining < 0
                            ? `${Math.abs(obl.daysRemaining)} days overdue`
                            : obl.daysRemaining === 0
                            ? 'Due today'
                            : `Due in ${obl.daysRemaining} days`}
                        </div>
                      </div>

                      <button
                        onClick={() => {
                          setActiveTab('ask');
                          handleAskQuestion(`When is my next ${obl.code} filing due and what is the penalty?`);
                        }}
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.5rem 0.85rem' }}
                      >
                        Ask Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {rulesState !== 'ready' && (
                <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem', marginTop: '1rem' }}>
                  {rulesState === 'loading' ? 'Checking approved regulatory rules…' : 'The applicability service is unavailable. No mock obligations are shown.'}
                </p>
              )}
              {rulesState === 'ready' && obligations.length === 0 && (
                <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem', marginTop: '1rem' }}>
                  No approved rules currently match this profile. Add source-backed rules through the review queue; AI candidates do not appear here until approved.
                </p>
              )}
            </div>

            {/* Quick Actions Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }} className="dash-quick-actions">
              <div
                onClick={() => setActiveTab('obligations')}
                style={{ padding: '1.5rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', cursor: 'pointer' }}
                className="hover-card"
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                    <FileText size={18} />
                  </div>
                  <h4 style={{ fontSize: '1.125rem', color: 'var(--color-black)' }}>View All Obligations</h4>
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', margin: 0 }}>
                  Inspect approved, source-backed obligations and the deterministic reasons they apply.
                </p>
              </div>

              <div
                onClick={() => setActiveTab('calendar')}
                style={{ padding: '1.5rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', cursor: 'pointer' }}
                className="hover-card"
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                    <Calendar size={18} />
                  </div>
                  <h4 style={{ fontSize: '1.125rem', color: 'var(--color-black)' }}>Compliance Calendar</h4>
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', margin: 0 }}>
                  Examine the monthly filing roadmap with exact due dates and statutory circulars.
                </p>
              </div>

              <div
                onClick={() => setActiveTab('ask')}
                style={{ padding: '1.5rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px', cursor: 'pointer' }}
                className="hover-card"
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '4px', backgroundColor: 'var(--color-beige-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-black)' }}>
                    <MessageSquare size={18} />
                  </div>
                  <h4 style={{ fontSize: '1.125rem', color: 'var(--color-black)' }}>Ask Clauz X</h4>
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', margin: 0 }}>
                  Get instant compliance guidance grounded in statutory acts and circulars.
                </p>
              </div>
            </div>

          </div>
        )}

        {/* =========================================================
            TAB 2: OBLIGATIONS DIRECTORY
           ========================================================= */}
        {activeTab === 'obligations' && (
          <div style={{ animation: 'fadeIn 0.25s ease-out' }}>
            {/* Category Filter Bar */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              {['All', 'Tax & GST', 'Labor & Social Security', 'Corporate & ROC', 'MSME Specific'].map((cat, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    padding: '0.45rem 0.95rem',
                    fontSize: '0.8125rem',
                    fontFamily: 'var(--font-sans)',
                    borderRadius: '20px',
                    border: selectedCategory === cat ? '1px solid var(--color-brick)' : '1px solid var(--color-border)',
                    backgroundColor: selectedCategory === cat ? 'var(--color-brick)' : '#FFFFFF',
                    color: selectedCategory === cat ? '#FFFFFF' : 'var(--color-black)',
                    cursor: 'pointer',
                    fontWeight: selectedCategory === cat ? 600 : 400
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Obligations Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }} className="dash-two-col">
              {filteredObligations.map((obl) => (
                <div
                  key={obl.id}
                  style={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1.75rem',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: 'var(--shadow-subtle)'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <div>
                        <span style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', padding: '0.2rem 0.5rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '3px' }}>
                          {obl.category}
                        </span>
                        <h4 style={{ fontSize: '1.25rem', color: 'var(--color-black)', margin: '0.5rem 0 0.2rem' }}>
                          {obl.code} — {obl.title}
                        </h4>
                      </div>
                      <span
                        style={{
                          fontSize: '0.6875rem',
                          fontFamily: 'var(--font-mono)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '3px',
                          fontWeight: 600,
                          backgroundColor: obl.status === 'Urgent' ? 'var(--color-brick-light)' : 'var(--color-bg)',
                          color: obl.status === 'Urgent' ? 'var(--color-brick)' : 'var(--color-black)'
                        }}
                      >
                        {obl.status}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginBottom: '0.85rem' }}>
                      <strong>Act:</strong> {obl.act} <br />
                      <strong>Section / Rule:</strong> {obl.section}
                    </div>

                    <div style={{ padding: '0.85rem', backgroundColor: 'var(--color-bg)', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '0.75rem', marginBottom: '1rem' }}>
                      <div style={{ fontWeight: 600, color: 'var(--color-black)', marginBottom: '0.2rem' }}>Why it applies to your profile:</div>
                      <div style={{ color: 'var(--color-muted)' }}>{obl.applicabilityReason}</div>
                    </div>

                    <div style={{ fontSize: '0.75rem', color: 'var(--color-brick)', marginBottom: '1rem' }}>
                      <strong>Penalty Risk:</strong> {obl.penaltyRisk}
                    </div>
                  </div>

                  <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontSize: '0.8125rem' }}>
                      Next Due: <strong>{obl.nextDueDate}</strong>
                    </div>
                    <button
                      onClick={() => {
                        setActiveTab('ask');
                        handleAskQuestion(`Explain how to file ${obl.code} and avoid penalties`);
                      }}
                      style={{ background: 'none', border: 'none', color: 'var(--color-brick)', fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                    >
                      Ask Guidance <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            {rulesState === 'ready' && filteredObligations.length === 0 && (
              <p style={{ color: 'var(--color-muted)', marginTop: '1rem' }}>No approved obligations match this profile and filter.</p>
            )}
          </div>
        )}

        {/* =========================================================
            TAB 3: CALENDAR
           ========================================================= */}
        {activeTab === 'calendar' && (
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '2.5rem', animation: 'fadeIn 0.25s ease-out' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--color-border)' }}>
              <div>
                <h3 style={{ fontSize: '1.35rem', color: 'var(--color-black)', letterSpacing: '-0.01em' }}>{calendarScheduleTitle}</h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>Forward-looking statutory timeline calculated for {profile.businessName}</p>
              </div>
              <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', padding: '0.3rem 0.65rem', backgroundColor: 'var(--color-bg)', border: '1px solid var(--color-border)', borderRadius: '3px' }}>
                {scheduledDatesCount} STATUTORY DATES
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {obligations.map((obl) => {
                let monthLabel = 'DUE';
                let dayLabel = obl.nextDueDate;
                if (obl.nextDueDate && obl.nextDueDate.includes('-')) {
                  const parts = obl.nextDueDate.split('-');
                  if (parts.length === 3) {
                    const parsedDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                    if (!isNaN(parsedDate.getTime())) {
                      monthLabel = parsedDate.toLocaleString('en-IN', { month: 'short' }).toUpperCase();
                      dayLabel = String(parsedDate.getDate());
                    }
                  }
                }
                const item = { id: obl.id, month: monthLabel, day: dayLabel, obligationCode: obl.code, category: obl.category, title: obl.title, status: obl.status };
                return (
                <div
                  key={item.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1.25rem 1.5rem',
                    backgroundColor: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '4px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ textAlign: 'center', minWidth: '45px', padding: '0.4rem', backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: '4px' }}>
                      <div style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', color: 'var(--color-brick)', textTransform: 'uppercase', fontWeight: 700 }}>{item.month}</div>
                      <div style={{ fontFamily: 'var(--font-serif)', fontSize: '0.9rem', lineHeight: 1.2, color: 'var(--color-black)' }}>{item.day}</div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.9375rem', color: 'var(--color-black)' }}>{item.obligationCode}</span>
                        <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)' }}>• {item.category}</span>
                      </div>
                      <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginTop: '0.2rem' }}>{item.title}</div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                    <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', fontWeight: 600, color: item.status === 'Due Soon' ? 'var(--color-brick)' : 'var(--color-black)' }}>
                      {item.status}
                    </span>
                    <button
                      onClick={() => {
                        setActiveTab('ask');
                        handleAskQuestion(`What are the steps to complete ${item.obligationCode} before ${item.month} ${item.day}?`);
                      }}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.75rem', padding: '0.4rem 0.75rem' }}
                    >
                      Verify
                    </button>
                  </div>
                </div>
              )})}
            </div>
            {rulesState === 'ready' && obligations.length === 0 && <p style={{ color: 'var(--color-muted)', marginTop: '1rem' }}>No approved rule schedules are available for this profile.</p>}
          </div>
        )}

        {/* =========================================================
            TAB 4: CONTRACT HEALTH REPORT & AI AUDIT
           ========================================================= */}
        {activeTab === 'verify' && (
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1.5rem', boxShadow: 'var(--shadow-card)', animation: 'fadeIn 0.25s ease-out' }}>
            <ContractDashboard embedded={true} />
          </div>
        )}

        {/* =========================================================
            TAB 5: ASK CLAUZ X (INTERACTIVE AI COPILOT)
           ========================================================= */}
        {activeTab === 'ask' && (
          <div
            style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '2rem',
              boxShadow: 'var(--shadow-card)',
              animation: 'fadeIn 0.25s ease-out'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--color-border)' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', color: 'var(--color-black)' }}>Ask Clauz X — Grounded Regulatory Assistant</h3>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-muted)' }}>Answers backed by relevant Acts, notifications, and circulars for {profile.businessName}</p>
              </div>
              <span style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', color: 'green', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                ● Connected to Indian Legal Vault
              </span>
            </div>

            {/* Quick Prompt Suggestions */}
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)', marginBottom: '0.5rem' }}>
                CLICK TO RUN VERIFIED STATUTORY QUERY:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {samplePredefinedQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAskQuestion(q)}
                    style={{
                      padding: '0.4rem 0.75rem',
                      fontSize: '0.75rem',
                      fontFamily: 'var(--font-sans)',
                      backgroundColor: 'var(--color-bg)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      color: 'var(--color-black)',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    💬 {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Chat Messages Stream */}
            <div
              style={{
                height: '380px',
                overflowY: 'auto',
                border: '1px solid var(--color-border)',
                borderRadius: '4px',
                padding: '1.25rem',
                backgroundColor: 'var(--color-bg)',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem',
                marginBottom: '1.25rem'
              }}
            >
              {messages.map((m, i) => (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: m.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div
                    style={{
                      maxWidth: '82%',
                      padding: '1rem 1.25rem',
                      backgroundColor: m.sender === 'user' ? 'var(--color-black)' : '#FFFFFF',
                      color: m.sender === 'user' ? '#FFFFFF' : 'var(--color-black)',
                      border: m.sender === 'user' ? 'none' : '1px solid var(--color-border)',
                      borderRadius: m.sender === 'user' ? '8px 8px 0 8px' : '0 8px 8px 8px',
                      fontSize: '0.875rem',
                      lineHeight: 1.6
                    }}
                  >
                    {m.text}

                    {Boolean(m.sources?.length) && (
                      <div style={{ marginTop: '0.85rem', paddingTop: '0.75rem', borderTop: '1px solid var(--color-border)', fontSize: '0.75rem' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', color: 'var(--color-brick)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.2rem' }}>
                          STATUTORY GROUNDING
                        </div>
                        {m.sources?.map((source, sourceIndex) => (
                          <div key={`${source.title}-${sourceIndex}`} style={{ marginTop: sourceIndex ? '0.65rem' : 0 }}>
                            <div style={{ fontWeight: 600, color: 'var(--color-black)' }}>{source.title}</div>
                            <div style={{ color: 'var(--color-muted)' }}>{source.citation}</div>
                            {source.source_url && <a href={source.source_url} target="_blank" rel="noreferrer" style={{ color: 'var(--color-brick)' }}>Open source ↗</a>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isAsking && <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)' }}>Searching reviewed legal sources…</div>}
            </div>

            {/* Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleAskQuestion(inputQuestion);
              }}
              style={{ display: 'flex', gap: '0.75rem' }}
            >
              <input
                type="text"
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                placeholder="Ask any question regarding your obligations, tax filings, or threshold limits..."
                style={{
                  flex: 1,
                  padding: '0.85rem 1.25rem',
                  backgroundColor: '#FFFFFF',
                  border: '1px solid var(--color-border)',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  outline: 'none',
                  color: 'var(--color-black)'
                }}
              />
              <button
                type="submit"
                className="btn btn-brick"
                disabled={isAsking}
                style={{ padding: '0.85rem 1.5rem', fontSize: '0.875rem' }}
              >
                {isAsking ? 'Checking sources…' : 'Ask'} <Send size={14} />
              </button>
            </form>
          </div>
        )}

      </div>

      <style>{`
        .hover-card:hover {
          border-color: var(--color-brick) !important;
          transform: translateY(-2px);
          transition: all 0.2s ease;
        }
        @media (max-width: 900px) {
          .dash-metrics-grid {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          .dash-quick-actions {
            grid-template-columns: 1fr !important;
          }
          .dash-two-col {
            grid-template-columns: 1fr !important;
          }
          .dash-docs-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};
