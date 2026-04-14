# Skill: build-release

Build a customer-ready offline release bundle.

## Steps

1. Run the full test suite and confirm all pass (see run-tests skill)

2. Set the version:
   ```bash
   export VERSION=v1.0.0
   ```

3. Run the release builder:
   ```bash
   bash scripts/build-release.sh
   ```

4. Verify the bundle:
   ```bash
   ls -lh release-bundle/images/
   ls release-bundle/
   ```

5. Deliver `phx-${VERSION}.tar.gz` to the customer.

## Customer Installation from Bundle

```bash
tar -xzf phx-v1.0.0.tar.gz
cd release-bundle
cp .env.example .env
# Edit .env with real credentials
bash scripts/install-offline.sh
```

## Checklist Before Release

- [ ] All tests pass
- [ ] Version tag set
- [ ] `.env.example` has current variable list
- [ ] `docs/` are up to date
- [ ] No real secrets in any committed file
- [ ] Compose files validated: `docker compose config`
