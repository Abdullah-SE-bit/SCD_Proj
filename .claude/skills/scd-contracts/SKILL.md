---
name: scd-contracts
description: SCD project rules for api-contracts, backend-engineering, database-management. Use when adding or changing an endpoint, schema, table or migration.
---

# scd-contracts

**Purpose:** project-specific rules for api-contracts, backend-engineering, database-management. Generic skills may help, but never override these.
**Use when:** adding or changing an endpoint, schema, table or migration.
**Read first:** contracts/, docs/architecture/APIContracts.md, DataArchitecture.md.
**Requirements:** IFC-002, API-*, SCH-*, DBS-*.

## Workflow
1. Change the contract and both examples first
2. Layer code as routes, services, repositories
3. Add a forward-only migration with a fresh-database test
4. Validate every input and output
5. Cache keys follow AMB-11

**Tools:** jsonschema, pytest.
**Restrictions:** no field without a requirement or written justification. No secrets in files or messages.
**Verify:** `python harness/verification/scd.py check contract-tests`.
**Outputs:** contract PR, tests.
**On failure:** consumer breaks: version the change and send CONTRACT_UPDATED.
**Complete when:** contract and service tests pass.
