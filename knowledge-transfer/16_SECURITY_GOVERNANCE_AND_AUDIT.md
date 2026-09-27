# 16 Security, Governance, and Audit

## 1. Security Architecture
- **No Hardcoded Credentials**: Loaded via `.env` / environment variables.
- **SQL Parameterization & Allowlist**: All queries use parameterized parameters and SQL command allowlisting.
- **PII Masking**: Automatic regex masking of sensitive data in logs.
- **Approval Gates**: High-risk runbooks require manual approval.
