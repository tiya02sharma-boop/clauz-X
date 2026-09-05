import type { BusinessProfile, Obligation, ComplianceCalendarItem } from '../types';

export const defaultProfile: BusinessProfile = {
  businessName: 'Acme Technologies Pvt Ltd',
  entityType: 'Private Limited',
  state: 'Maharashtra',
  sector: 'Information Technology & Software Services',
  turnover: '₹5 Cr - ₹15 Cr',
  headcount: '25-50 Employees',
  investmentPlantMachinery: 20000000,
  isFactory: false,
  msmeClassification: 'Small',
  gstRegistered: true,
  gstFilingScheme: 'monthly',
  gstin: '27AABCU9603R1ZM',
  pan: 'AABCU9603R',
  cin: 'U72900MH2021PTC368491',
  udyamNumber: 'UDYAM-MH-01-0084920',
  whatsappNumber: '+919896603656'
};

export const sampleObligations: Obligation[] = [
  {
    id: 'obl-1',
    code: 'GSTR-3B',
    title: 'Monthly Summary Return & Tax Payment',
    act: 'Central Goods and Services Tax Act, 2017',
    section: 'Section 39(1) read with Rule 61(5)',
    category: 'Tax & GST',
    frequency: 'Monthly',
    nextDueDate: 'September 20, 2026',
    daysRemaining: 3,
    status: 'Urgent',
    applicabilityReason: 'Mandatory for all regular taxpayers having aggregate turnover above threshold.',
    penaltyRisk: '₹50/day late fee (₹20 for NIL return) + 18% p.a. interest on unpaid tax.',
    sourceUrl: 'https://cbic-gst.gov.in'
  },
  {
    id: 'obl-2',
    code: 'ESI Monthly',
    title: 'ESI Contribution Payment & Filing',
    act: 'Employees\' State Insurance Act, 1948',
    section: 'Section 39 & 40 read with Regulation 31',
    category: 'Labor & Social Security',
    frequency: 'Monthly',
    nextDueDate: 'September 15, 2026',
    daysRemaining: 8,
    status: 'Upcoming',
    applicabilityReason: 'Applicable to non-seasonal factories/establishments employing 10+ persons with wages up to ₹21,000/mo.',
    penaltyRisk: 'Damages from 5% to 25% under Sec 85B + Prosecution under Sec 85.',
    sourceUrl: 'https://esic.gov.in'
  },
  {
    id: 'obl-3',
    code: 'EPF Monthly',
    title: 'PF Contribution & ECR Electronic Challan Return',
    act: 'Employees\' Provident Funds and Miscellaneous Provisions Act, 1952',
    section: 'Section 6 & Scheme Paragraph 38',
    category: 'Labor & Social Security',
    frequency: 'Monthly',
    nextDueDate: 'September 15, 2026',
    daysRemaining: 8,
    status: 'Upcoming',
    applicabilityReason: 'Mandatory for commercial establishments employing 20 or more staff.',
    penaltyRisk: 'Damages up to 25% p.a. + penal interest under Section 7Q (12% p.a.).',
    sourceUrl: 'https://epfindia.gov.in'
  },
  {
    id: 'obl-4',
    code: 'TDS (Challan 281)',
    title: 'Monthly TDS / TCS Deposit',
    act: 'Income Tax Act, 1961',
    section: 'Section 192 - 195 read with Rule 30',
    category: 'Tax & GST',
    frequency: 'Monthly',
    nextDueDate: 'October 7, 2026',
    daysRemaining: 14,
    status: 'Upcoming',
    applicabilityReason: 'Deduction of tax at source on salaries, contractor payments, and professional fees.',
    penaltyRisk: '1.5% interest per month on delayed payment under Section 201(1A).',
    sourceUrl: 'https://incometax.gov.in'
  },
  {
    id: 'obl-5',
    code: 'MSME-1 Form',
    title: 'Half-Yearly Return of Outstanding Payments to MSME Vendors',
    act: 'Companies Act, 2013',
    section: 'Section 405 read with MCA Order dated 22.01.2019',
    category: 'MSME Specific',
    frequency: 'Half-Yearly',
    nextDueDate: 'October 31, 2026',
    daysRemaining: 21,
    status: 'Upcoming',
    applicabilityReason: 'Mandatory for all specified companies with dues to Micro/Small enterprises exceeding 45 days.',
    penaltyRisk: 'Company fine up to ₹20,000 + ₹1,000/day ongoing penalty; Director liability.',
    sourceUrl: 'https://mca.gov.in'
  },
  {
    id: 'obl-6',
    code: 'DIR-3 KYC',
    title: 'Annual Director KYC Verification (Web / e-Form)',
    act: 'Companies Act, 2013',
    section: 'Rule 12A of Companies (Appointment and Qualification of Directors) Rules, 2014',
    category: 'Corporate & ROC',
    frequency: 'Annual',
    nextDueDate: 'September 30, 2026',
    daysRemaining: 18,
    status: 'Upcoming',
    applicabilityReason: 'Mandatory for every individual who holds a DIN as on 31st March of the financial year.',
    penaltyRisk: 'DIN deactivation + ₹5,000 fee for belated filing.',
    sourceUrl: 'https://mca.gov.in'
  },
  {
    id: 'obl-7',
    code: 'AOC-4 & MGT-7',
    title: 'Annual Financial Statements & Annual Return Filing with ROC',
    act: 'Companies Act, 2013',
    section: 'Section 137 & Section 92',
    category: 'Corporate & ROC',
    frequency: 'Annual',
    nextDueDate: 'November 29, 2026',
    daysRemaining: 45,
    status: 'Upcoming',
    applicabilityReason: 'Mandatory annual filing for all registered Private Limited and Public Companies.',
    penaltyRisk: '₹100 per day additional fee for each day of delay.',
    sourceUrl: 'https://mca.gov.in'
  },
  {
    id: 'obl-8',
    code: 'GSTR-1',
    title: 'Monthly Statement of Outward Supplies',
    act: 'Central Goods and Services Tax Act, 2017',
    section: 'Section 37 read with Rule 59',
    category: 'Tax & GST',
    frequency: 'Monthly',
    nextDueDate: 'September 11, 2026',
    daysRemaining: 1,
    status: 'Urgent',
    applicabilityReason: 'Regular GST taxpayer supplying goods or services without QRMP option.',
    penaltyRisk: 'Late fee ₹50/day + blocking of E-Way Bill generation if consecutive filings missed.',
    sourceUrl: 'https://cbic-gst.gov.in'
  },
  {
    id: 'obl-9',
    code: 'Advance Tax Q2',
    title: 'Second Installment of Advance Tax (45%)',
    act: 'Income Tax Act, 1961',
    section: 'Section 208, 209 & 211',
    category: 'Tax & GST',
    frequency: 'Quarterly',
    nextDueDate: 'September 15, 2026',
    daysRemaining: 8,
    status: 'Upcoming',
    applicabilityReason: 'Assessees whose estimated tax liability for the year exceeds ₹10,000.',
    penaltyRisk: 'Interest at 1% per month under Section 234C for deferment of installment.',
    sourceUrl: 'https://incometax.gov.in'
  },
  {
    id: 'obl-10',
    code: 'PT Monthly Return',
    title: 'State Professional Tax Return & Remittance',
    act: 'Maharashtra State Tax on Professions, Trades, Callings and Employments Act, 1975',
    section: 'Section 6 read with Rule 11',
    category: 'Labor & Social Security',
    frequency: 'Monthly',
    nextDueDate: 'September 30, 2026',
    daysRemaining: 18,
    status: 'Upcoming',
    applicabilityReason: 'Employers in Maharashtra registered under PTRC with monthly liability > ₹50,000.',
    penaltyRisk: '1.25% interest per month + penalty up to 10% of tax amount.',
    sourceUrl: 'https://mahagst.gov.in'
  },
  {
    id: 'obl-11',
    code: 'Form 24Q (Q2)',
    title: 'Quarterly TDS Return for Salary Deductions',
    act: 'Income Tax Act, 1961',
    section: 'Section 200(3) read with Rule 31A',
    category: 'Tax & GST',
    frequency: 'Quarterly',
    nextDueDate: 'October 31, 2026',
    daysRemaining: 28,
    status: 'Upcoming',
    applicabilityReason: 'All corporate deductors paying taxable salaries to employees.',
    penaltyRisk: '₹200 per day under Section 234E until return is filed.',
    sourceUrl: 'https://incometax.gov.in'
  },
  {
    id: 'obl-12',
    code: 'Board Meeting Min.',
    title: 'Quarterly Board Meeting & Minutes Documentation',
    act: 'Companies Act, 2013',
    section: 'Section 173 & Secretarial Standard-1 (SS-1)',
    category: 'Corporate & ROC',
    frequency: 'Quarterly',
    nextDueDate: 'September 30, 2026',
    daysRemaining: 18,
    status: 'Upcoming',
    applicabilityReason: 'Every Private Limited company must hold at least 1 meeting every quarter (max gap 120 days).',
    penaltyRisk: 'Penalty of ₹25,000 on company and ₹5,000 on officer in default.',
    sourceUrl: 'https://mca.gov.in'
  },
  {
    id: 'obl-factories-act',
    code: 'Factories Act Reg.',
    title: 'Factories Act Registration & Licensing',
    act: 'Factories Act, 1948',
    section: 'Section 6 read with State Factory Rules [PLACEHOLDER: Legal verification required]',
    category: 'Labor & Social Security',
    frequency: 'Annual',
    nextDueDate: 'December 31, 2026',
    daysRemaining: 117,
    status: 'Upcoming',
    applicabilityReason: 'Applies because your business operates as a factory under the Factories Act, not a commercial establishment.',
    penaltyRisk: 'Imprisonment up to 2 years or fine up to ₹1,00,000 under Section 92 [PLACEHOLDER: Legal verification required].',
    sourceUrl: 'https://labour.gov.in'
  },
  {
    id: 'obl-shops-act',
    code: 'Shops & Est. Reg.',
    title: 'Shops & Commercial Establishments Registration',
    act: 'State Shops and Commercial Establishments Act',
    section: 'State Shops & Establishments Registration Provisions [PLACEHOLDER: Legal verification required]',
    category: 'Labor & Social Security',
    frequency: 'Annual',
    nextDueDate: 'December 31, 2026',
    daysRemaining: 117,
    status: 'Upcoming',
    applicabilityReason: 'Applies because your business operates as a commercial establishment under the Shops and Establishments Act, not a factory.',
    penaltyRisk: 'Monetary penalty up to ₹1,00,000 per state schedule [PLACEHOLDER: Legal verification required].',
    sourceUrl: 'https://labour.gov.in'
  }
];

export const sampleCalendarItems: ComplianceCalendarItem[] = [
  {
    id: 'cal-1',
    date: '2026-09-11',
    day: 11,
    month: 'Sep',
    obligationCode: 'GSTR-1',
    title: 'Outward Supplies Return (Monthly)',
    category: 'Tax & GST',
    status: 'Due Soon'
  },
  {
    id: 'cal-2',
    date: '2026-09-15',
    day: 15,
    month: 'Sep',
    obligationCode: 'EPF & ESI',
    title: 'Monthly Social Security Contribution & ECR',
    category: 'Labor',
    status: 'Upcoming'
  },
  {
    id: 'cal-3',
    date: '2026-09-15',
    day: 15,
    month: 'Sep',
    obligationCode: 'Advance Tax',
    title: 'Advance Tax Q2 (Cumulative 45%)',
    category: 'Direct Tax',
    status: 'Upcoming'
  },
  {
    id: 'cal-4',
    date: '2026-09-20',
    day: 20,
    month: 'Sep',
    obligationCode: 'GSTR-3B',
    title: 'Monthly Summary GST Return & Payment',
    category: 'Tax & GST',
    status: 'Due Soon'
  },
  {
    id: 'cal-5',
    date: '2026-09-30',
    day: 30,
    month: 'Sep',
    obligationCode: 'DIR-3 KYC',
    title: 'Director KYC Annual Verification (MCA)',
    category: 'Corporate',
    status: 'Upcoming'
  },
  {
    id: 'cal-6',
    date: '2026-10-07',
    day: 7,
    month: 'Oct',
    obligationCode: 'TDS Challan 281',
    title: 'TDS Deposit for September Deductions',
    category: 'Direct Tax',
    status: 'Upcoming'
  },
  {
    id: 'cal-7',
    date: '2026-10-31',
    day: 31,
    month: 'Oct',
    obligationCode: 'MSME-1 Form',
    title: 'Half-Yearly Outstanding Dues Return to MSMEs',
    category: 'MSME Specific',
    status: 'Upcoming'
  }
];

export const samplePredefinedQuestions = [
  "When is my next GST filing due?",
  "Do I need to file MSME-1 Form this half-year?",
  "Is ESI registration mandatory for our current headcount?",
  "What is the penalty for delayed DIR-3 KYC filing?",
  "What are the quarterly Board meeting requirements for a Pvt Ltd?"
];

export const mockChatAnswers: Record<string, {
  answer: string;
  source: {
    act: string;
    section: string;
    rule: string;
    circularNo?: string;
    summary: string;
  };
}> = {
  "When is my next GST filing due?": {
    answer: "Your next applicable GST filing is GSTR-1 due on September 11, 2026, followed by GSTR-3B due on September 20, 2026 for the preceding tax period. Because your turnover exceeds ₹5 Crore and you are on monthly filing frequency, both returns must be completed within these statutory windows.",
    source: {
      act: "Central Goods and Services Tax Act, 2017",
      section: "Section 37(1) & Section 39(1)",
      rule: "Rule 59 & Rule 61(5) of CGST Rules 2017",
      circularNo: "CBIC Notification No. 13/2020-Central Tax",
      summary: "Prescribes monthly deadlines for outward supplies (11th) and consolidated returns (20th) for regular registered taxable entities."
    }
  },
  "Do I need to file MSME-1 Form this half-year?": {
    answer: "Yes, if your company has any outstanding payments due to registered Micro or Small enterprises for more than 45 days as of September 30, 2026, you are required to submit Form MSME-1 to the Registrar of Companies (ROC) within 30 days (by October 31, 2026).",
    source: {
      act: "Companies Act, 2013 read with MSMED Act, 2006",
      section: "Section 405(1) & Section 15 of MSMED Act",
      rule: "Specified Companies (Furnishing of information about payment to micro and small enterprise suppliers) Order, 2019",
      circularNo: "MCA Gazette Order S.O. 368(E)",
      summary: "Requires half-yearly reporting of delayed MSME vendor payments along with reasons for delay."
    }
  },
  "Is ESI registration mandatory for our current headcount?": {
    answer: "Yes. With a declared headcount of 25-50 employees in Maharashtra, your establishment comfortably exceeds the 10-person threshold mandated under the ESI Act. All employees whose monthly gross wages do not exceed ₹21,000 (or ₹25,000 for employees with disabilities) must be covered.",
    source: {
      act: "Employees' State Insurance Act, 1948",
      section: "Section 1(5) & Section 2(9)",
      rule: "Rule 50 of ESI (Central) Rules, 1950",
      circularNo: "ESIC Coverage Notification No. P-11/14/19/2016-Bft.II",
      summary: "Mandatory coverage for all commercial establishments with 10+ employees where monthly wages are within statutory wage ceiling."
    }
  },
  "What is the penalty for delayed DIR-3 KYC filing?": {
    answer: "If a director fails to file DIR-3 KYC by September 30, the Director Identification Number (DIN) will be marked as 'Deactivated due to non-filing of DIR-3 KYC'. Reactivation requires filing the form along with a mandatory late fee of ₹5,000 per DIN.",
    source: {
      act: "Companies Act, 2013",
      section: "Section 152 read with Rule 12A",
      rule: "Companies (Appointment and Qualification of Directors) Rules, 2014",
      circularNo: "MCA Notification F. No. 1/22/2013-CL-V",
      summary: "Specifies annual mandatory verification of director KYC details and ₹5,000 penalty for filing after due date."
    }
  },
  "What are the quarterly Board meeting requirements for a Pvt Ltd?": {
    answer: "A Private Limited company must hold at least one Board Meeting in every calendar quarter, ensuring that the maximum interval between two consecutive Board Meetings does not exceed 120 days. Minimum quorum is 2 directors or 1/3rd of total strength (whichever is higher).",
    source: {
      act: "Companies Act, 2013",
      section: "Section 173(1) & Section 174",
      rule: "Secretarial Standard on Meetings of the Board of Directors (SS-1)",
      circularNo: "ICSI SS-1 Mandated under Sec 118(10)",
      summary: "Mandates minimum 4 board meetings per year with compliant notice periods, quorum, and recorded minutes."
    }
  }
};


export const sampleAuditTrail = [
  {
    id: 'aud-1',
    time: '10:42 AM',
    date: 'Today',
    title: 'Obligation assessment completed',
    description: '12 active obligations mapped based on updated turnover & headcount parameters.',
    badge: 'System Audit'
  },
  {
    id: 'aud-2',
    time: '09:00 AM',
    date: 'Today',
    title: 'Automated reminder dispatched',
    description: 'WhatsApp & Email alert sent for GSTR-1 filing (T-2 days countdown).',
    badge: 'Notification'
  },
  {
    id: 'aud-3',
    time: '04:15 PM',
    date: 'Yesterday',
    title: 'Auto-drafted MSME-1 generated',
    description: 'Pre-filled MCA e-form draft created using verified master data.',
    badge: 'Document'
  },
  {
    id: 'aud-4',
    time: '11:30 AM',
    date: '3 days ago',
    title: 'Compliance score recalibrated',
    description: 'Health rating updated to 82% following successful EPF challan reconciliation.',
    badge: 'Health Check'
  }
];
