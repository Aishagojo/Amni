export type CaseStatus = 'Open' | 'In progress' | 'Resolved';
export type SupportCase = { id: string; title: string; category: string; priority: string; status: CaseStatus; owner: string; description: string };
export const initialCases: SupportCase[] = [
  { id: 'AMN-1042', title: 'API connection timing out', category: 'Networking', priority: 'High', status: 'In progress', owner: 'Alex Morgan', description: 'The application cannot reach the API endpoint. Check DNS resolution, the destination port, and upstream connectivity.' },
  { id: 'AMN-1041', title: 'Renew the staging TLS certificate', category: 'Security', priority: 'Medium', status: 'Open', owner: 'Sam Wilson', description: 'Review certificate expiry and the staging HTTPS configuration before rotating the certificate.' },
  { id: 'AMN-1040', title: 'Investigate container restart loop', category: 'Linux & Docker', priority: 'High', status: 'In progress', owner: 'Jamie Chen', description: 'Inspect container logs, the health check, and memory limits to identify the cause of repeated restarts.' },
  { id: 'AMN-1039', title: 'Update the DNS troubleshooting guide', category: 'Knowledge base', priority: 'Low', status: 'Resolved', owner: 'Alex Morgan', description: 'The guide now includes DNS lookup commands, cache checks, and common resolution errors.' },
];
export const guides = [
  { title: 'Start with the right DNS checks', category: 'Networking', time: '4 min read', body: 'Confirm the hostname and expected IP address. Use dig or nslookup to inspect the DNS response. Compare the configured resolver with a known resolver, then review record types and TTL values. Record the results in your case before changing configuration.' },
  { title: 'Find the story in your container logs', category: 'Linux & Docker', time: '6 min read', body: 'List containers with docker ps -a. Inspect recent output using docker logs --tail 100 <container>. Check the exit code and restart count with docker inspect. Compare errors with recent deployments and inspect health-check output before restarting the service.' },
  { title: 'Troubleshoot an HTTPS connection', category: 'Security', time: '5 min read', body: 'Confirm the hostname and system clock. Inspect the certificate chain and expiry using openssl s_client. Check that port 443 is reachable and the reverse proxy serves the correct certificate. Do not disable certificate verification to resolve a production connection error.' },
];
