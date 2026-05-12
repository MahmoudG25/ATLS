# Backup & Recovery Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-08 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Infrastructure & Backend Team |
| **Applicability** | All ATLS Production Data & Media |

## 1. Backup Philosophy
In ATLS, data is the farm's digital lifeblood. We follow the **3-2-1 Rule**:
- **3** copies of data (Primary + 2 Backups).
- **2** different storage media (Object Storage + Local Snapshot).
- **1** copy off-site (Different geographic region).

## 2. Backup Types
- **Automated Snapshots**: Infrastructure-level backups (AWS RDS/S3).
- **Point-in-Time Recovery (PITR)**: Transaction logs for database state restoration.
- **Manual Exports**: Domain-specific backups (e.g., Seasonal financial records).

## 3. Full vs Incremental
- **Full**: Weekly complete database and media inventory snapshots.
- **Incremental**: Daily changes (WAL logs for DB, new files for Storage).
- **Transaction Logs**: Continuously streamed to backup storage every 5 minutes.

## 4. Database Backups
- **Frequency**: Daily snapshots + Continuous PITR.
- **Cross-Region**: Snapshots must be automatically replicated to a secondary region (e.g., from `us-east-1` to `eu-west-1`).
- **Integrity**: Checksum validation for every snapshot.

## 5. Media Backups
- **Versioning**: Enable S3 Bucket Versioning for immediate recovery from accidental deletions.
- **Replication**: Use Cross-Region Replication (CRR) for all operational media buckets.
- **Immutability**: Enable "Object Lock" for legal/audit documents.

## 6. Encryption Rules
- **At Rest**: All backups must be encrypted using `AES-256`.
- **Key Management**: Use AWS KMS or Cloud KMS with multi-factor authentication (MFA) for decryption keys.
- **FORBIDDEN**: Storing unencrypted backups in any environment.

## 7. Restore Workflows
- **Non-Destructive**: Restores must always be to a *new* instance or database. Overwriting production data is strictly forbidden.
- **Verification**: Every restore must be validated against a "Data Integrity Checklist" before being promoted to production.

## 8. Disaster Recovery (DR)
- **RTO (Recovery Time Objective)**: < 4 hours for core operational services.
- **RPO (Recovery Point Objective)**: < 15 minutes (max 15 mins of data loss).
- **Failover**: Automated DNS failover to the secondary region cluster.

## 9. Multi-Tenant Recovery
- **Granularity**: Ability to restore a single tenant's data from a shared backup (using schema-level or filtered data extraction).
- **Safety**: Restoring Tenant A must never expose or affect Tenant B's data.

## 10. Backup Validation
- **Dry Runs**: Monthly automated restore tests to a staging environment to verify backup viability.
- **Alerting**: Failure to validate a backup triggers a `CRITICAL` alert to the on-call engineer.

## 11. Retention Rules
- **Daily**: 7 days.
- **Weekly**: 4 weeks.
- **Monthly**: 12 months.
- **Yearly**: 10 years (for regulatory/agricultural audit compliance).

## 12. Deletion Safeguards
- **Termination Protection**: Enabled for all production DB instances.
- **Soft Delete**: All backups must remain in a "Trash" or "Pending Deletion" state for 72 hours before permanent removal.

## 13. Admin Confirmation Flows
- **Multi-Sig**: Deleting or modifying a backup policy requires approval from two authorized administrators.
- **MFA**: Mandatory for any manual backup deletion.

## 14. Audit Logging
- Every backup creation, modification, and deletion is recorded in the immutable audit log.
- Every restore attempt (success or failure) is logged with the `user_id` of the requesting admin.

## 15. Async Backup Processing
- Large media backups and database exports must be handled by dedicated infrastructure, not the application server.
- Use Celery to monitor the status of cloud-native backup tasks.

## 16. Monitoring & Alerts
- Monitor backup age, size, and success/failure status.
- Alerting thresholds:
    - Backup failed: Immediate.
    - Restore test failed: Immediate.
    - Backup size decrease > 20% (possible data loss): Immediate.

## 17. Performance Constraints
- Backup operations must not increase application latency by more than 5%.
- Restore operations should utilize high-speed internal cloud networks.

## 18. AI Safety Rules
- **Unencrypted**: AI agents MUST NOT create or move backups to unencrypted storage.
- **Silent Deletion**: FORBID "Silent Deletion" of backups; every deletion must produce an audit trail and alert.
- **Overwrite**: FORBID logic that overwrites existing production data during a restore; always restore to a new target.
- **Testing**: FORBID declaring a backup system "Production Ready" without a documented restore test.
- **Single Point**: FORBID storing backups in the same geographic region/account as the primary data.

## 19. Forbidden Backup Anti-Patterns
- **The Local Backup**: Storing database dumps on the same disk as the database.
- **Ignoring Media**: Backing up the DB but forgetting to backup the billions of photos in S3.
- **Manual Backups**: Relying on an engineer to run a script manually every day.

## 20. Agricultural Disaster Scenarios
- **Ransomware**: A farm manager's account is compromised and data is encrypted. System uses PITR to roll back the database to 10 minutes before the infection.
- **Region Failure**: AWS `us-east-1` goes down. The ATLS DR policy triggers failover to `us-west-2` using replicated snapshots.

## 21. Enforcement Checklist
- [ ] 3-2-1 Rule implemented.
- [ ] Cross-region replication active for DB and S3.
- [ ] PITR active with < 15 min RPO.
- [ ] Monthly restore dry-runs scheduled.
- [ ] Encryption at rest verified for all snapshots.
- [ ] Multi-sig deletion flow active.
- [ ] Audit logging for all backup actions.
- [ ] Restore-to-new-instance policy enforced.
- [ ] Soft-delete on backups enabled.
