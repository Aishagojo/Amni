export type CaseStatus = 'Open' | 'In progress' | 'Resolved';
export type SupportCase = { id: string; title: string; category: string; priority: string; status: CaseStatus; owner: string; description: string };
export const initialCases: SupportCase[] = [
  { id: 'AMN-1042', title: 'API connection timing out', category: 'Networking', priority: 'High', status: 'In progress', owner: 'Alex Morgan', description: 'The application cannot reach the API endpoint. Check DNS resolution, the destination port, and upstream connectivity.' },
  { id: 'AMN-1041', title: 'Renew the staging TLS certificate', category: 'Security', priority: 'Medium', status: 'Open', owner: 'Sam Wilson', description: 'Review certificate expiry and the staging HTTPS configuration before rotating the certificate.' },
  { id: 'AMN-1040', title: 'Investigate container restart loop', category: 'Linux & Docker', priority: 'High', status: 'In progress', owner: 'Jamie Chen', description: 'Inspect container logs, the health check, and memory limits to identify the cause of repeated restarts.' },
  { id: 'AMN-1039', title: 'Update the DNS troubleshooting guide', category: 'Knowledge base', priority: 'Low', status: 'Resolved', owner: 'Alex Morgan', description: 'The guide now includes DNS lookup commands, cache checks, and common resolution errors.' },
];
