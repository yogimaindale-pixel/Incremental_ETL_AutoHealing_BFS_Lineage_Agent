# Security, Governance & Audit Controls

## Security Controls
1. **No Credentials in Code or Config**: Passwords/tokens loaded via `.env` file or environment variables.
2. **PII Masking**: Emails, credit card numbers, and SSNs masked automatically in logs.
3. **Parameterized SQL & Allowlisting**: All queries parameterized; SQL commands validated against allowlist (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `CREATE`, `ALTER`, `DROP`).
4. **Human Approval Gates**: High-risk actions require explicit human sign-off in test/prod.
