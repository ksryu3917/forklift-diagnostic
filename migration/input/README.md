# V20 migration inputs

Data only, recovered from local historical candidate
`9035a4ae103a1f699a48ba1a63386a63f5290485`.
No legacy Java is imported by the V20 migration.

Run `python tools/migrate_v20.py` then `python tools/validate_migration_parity.py`.
Parity confirms source records, nodes, branches and variant entry points were
preserved. It does not certify the OEM evidence or field completeness.
Missing contracts remain `OEM_VERIFY` and block procedural execution.
