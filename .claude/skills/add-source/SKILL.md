# Skill: add-source

Add a new data source connector to the PHX ingest service.

## For a new filesystem folder

1. Create the mount directory on the host:
   ```bash
   mkdir -p /mnt/customer-shares/<department>
   ```

2. Add the bind mount to `docker/compose.yaml` under `phx-ingest.volumes`:
   ```yaml
   - /mnt/customer-shares/<department>:/customer_data/<department>:ro
   ```

3. Add the source to `config/customer-template/sources.yaml`:
   ```yaml
   - id: "<unique-id>"
     type: filesystem
     enabled: true
     path: /customer_data/<department>
     department: <department>
     access_tags:
       - <tag1>
       - <tag2>
     doc_type: <doc_type>
     include_patterns: ["**/*.txt", "**/*.pdf", "**/*.docx"]
     exclude_patterns: ["**/.DS_Store"]
   ```

4. Restart ingest: `docker compose restart phx-ingest`

5. Trigger sync: `docker compose exec phx-ingest python -m app.main --once`

## For a new database connector type (e.g., MySQL)

1. Create `services/ingest/app/connectors/mysql_connector.py`
2. Subclass `BaseConnector` from `connectors/base.py`
3. Implement `scan()` and `get_source_type()`
4. Register in `services/ingest/app/pipeline.py` CONNECTOR_MAP
5. Add `source_type: mysql` to sources.yaml schema
6. Write unit tests in `services/ingest/tests/test_mysql.py`
7. Update `docs/customer-onboarding.md`

## Security Checklist for New Connectors

- [ ] Uses read-only credentials
- [ ] Only reads allowlisted tables/views (no arbitrary user-controlled SQL)
- [ ] No hardcoded credentials
- [ ] Credentials come from source_config (from sources.yaml env-var interpolation)
- [ ] Connection errors are caught and logged, not raised to users
