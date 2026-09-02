export interface BusinessProfile {
  businessName: string;
  entityType: 'Private Limited' | 'LLP' | 'Partnership' | 'Sole Proprietorship' | 'Public Limited';
  state: string;
  sector: string;
  turnover: string;
  headcount: string;
  gstRegistered: boolean;
  gstFilingScheme?: 'monthly' | 'quarterly' | 'composition' | 'unknown';
  agmDate?: string;
  gstin?: string;
  pan?: string;
  cin?: string;
  udyamNumber?: string;
  whatsappNumber?: string;
}

export interface Obligation {
  id: string;
  code: string;
  title: string;
  act: string;
  section: string;
  category: 'Tax & GST' | 'Labor & Social Security' | 'Corporate & ROC' | 'MSME Specific' | 'Financial & Banking';
  frequency: 'Monthly' | 'Quarterly' | 'Half-Yearly' | 'Annual' | 'Event-Based';
  nextDueDate: string;
  daysRemaining: number;
  status: 'Urgent' | 'Upcoming' | 'Overdue' | 'Compliant';
  applicabilityReason: string;
  penaltyRisk: string;
  sourceUrl?: string;
}

export interface ComplianceCalendarItem {
  id: string;
  date: string;
  day: number;
  month: string;
  obligationCode: string;
  title: string;
  category: string;
  status: 'Due Soon' | 'Upcoming' | 'Completed' | 'Overdue';
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  source?: {
    act: string;
    section: string;
    rule: string;
    circularNo?: string;
    summary: string;
  };
}
