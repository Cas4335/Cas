# Skill: security-check

Run a security audit checklist on the PHX codebase.

## Automated Checks

```bash
# Check for hardcoded secrets (common patterns)
grep -rn "password\s*=\s*['\"]" services/ --include="*.py" | grep -v "test\|example\|placeholder\|hash"

# Check for outbound HTTP to external URLs
grep -rn "https\?://\(api\.\|cloud\.\|openai\.\|anthropic\.\)" services/ --include="*.py"

# Check for any 'shell=True' subprocess calls
grep -rn "shell=True" services/ --include="*.py"

# Check for SQL string formatting (injection risk)
grep -rn "execute.*%s\|execute.*format\|execute.*f\"" services/ --include="*.py" | grep -v "test"
```

## Manual Review Checklist

### Authentication
- [ ] JWT tokens have expiry (exp claim set)
- [ ] Passwords are bcrypt-hashed
- [ ] Login endpoint doesn't reveal whether email exists
- [ ] Inactive users are rejected

### Authorization
- [ ] `get_allowed_tags()` is called before every Qdrant retrieval
- [ ] allowed_tags comes from DB role lookup, not user input
- [ ] Chat endpoint applies filter on every request
- [ ] Admin endpoints require admin role check

### Source Connectors
- [ ] File mounts are `:ro` in compose.yaml
- [ ] DB connectors set `read_only=True` or equivalent
- [ ] No user input reaches SQL queries
- [ ] allowlisted tables only (no `SELECT *` on arbitrary tables)

### Secrets
- [ ] No secrets in any Python/TypeScript file
- [ ] No secrets in compose.yaml (all from env vars)
- [ ] .env is in .gitignore
- [ ] .env.example has placeholder values only

### Network
- [ ] No outbound calls to cloud APIs in runtime code
- [ ] Qdrant/Postgres/Ollama ports bound to 127.0.0.1 (not 0.0.0.0)
- [ ] UI port (3000) is the only publicly exposed port

### Audit
- [ ] Every chat request writes an audit log
- [ ] Audit log includes user_id, roles, allowed_tags, chunk_ids
- [ ] Audit logs are accessible only to admin role
