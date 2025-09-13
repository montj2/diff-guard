# Security Policy

We take supply-chain and dependency security seriously. This project is early-stage; responsible disclosure helps everyone.

## Supported Versions
The `master` branch is the only actively supported line. Create issues or PRs against `master`.

## Reporting a Vulnerability
Email: security (at) example.com (replace with actual contact) or open a PRIVATE security advisory in GitHub (Security > Advisories) if available.

Please include:
- A clear description of the issue
- Steps to reproduce (minimal proof-of-concept preferred)
- Potential impact (confidentiality, integrity, availability)
- Suggested mitigation (if known)

Do not publicly disclose details until maintainers acknowledge and provide a remediation path or release.

## Response Targets (Best Effort)
- Acknowledge report: 3 business days
- Initial assessment: 7 business days
- Fix or mitigation plan: 14 business days (complex issues may take longer)

## Scope
Reports relevant to:
- Remote code execution, injection, sandbox escapes
- Authentication or authorization bypass in future features
- Data tampering or integrity failures in analysis pipeline
- Vulnerabilities in diff parsing leading to unsafe execution

Out of scope (unless escalation path to a real issue):
- Typos, minor logging gaps
- Denial of service via unrealistic resource exhaustion (unless trivial)
- Dependency advisory already tracked upstream

## Coordinated Disclosure
We prefer coordinated disclosure. After a fix is released you may publish details. Credit will be given unless you request anonymity.

## Hardening Recommendations (Roadmap)
- Deterministic parsing & sandboxing of package contents
- Memory/resource limits on diff/analysis steps
- Input validation on all external payloads
- Structured logging + audit trail

Thank you for helping improve the security of DiffGuard.
