# Notification & Alerting Domain

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-DOM-NOT |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Communications & Backend Team |
| **Applicability** | Global System Alerts & User Communications |

## 1. Notification Domain Philosophy
The Notification Domain is the **"Nervous System"** of the ATLS platform. It ensures that the right information reaches the right person at the right time, preventing operational delays and safety incidents.
- **Actionable**: Every notification should have a clear purpose or required action.
- **Relevant**: Only notify users of events that impact their specific roles or responsibilities.
- **Event-Driven**: Notifications are secondary side-effects of domain events, never the primary driver of logic.

## 2. Operational Alerting Principles
- **Signal-to-Noise**: Minimize "notification fatigue" by batching low-priority updates.
- **Persistence**: Critical alerts must remain visible until explicitly acknowledged or resolved.
- **Contextual**: Include deep-links to the relevant operational entity (e.g., specific Harvest report).

## 3. Notification Aggregate Structure
The core aggregate is the `Notification`:
- **Recipient**: `user_id`, `tenant_id`.
- **Content**: `title`, `body`, `payload` (JSON).
- **Template**: `template_id`, `variables` (JSON).
- **Routing**: `preferred_channels` (List), `priority` (Enum).
- **Status**: `sent_at`, `delivered_at`, `read_at`, `failed_at`.
- **Escalation**: `is_critical`, `escalation_level`, `next_escalation_at`.

## 4. Notification Types
1. **ALERT**: Critical issues requiring immediate action (e.g., Frost warning, Security breach).
2. **UPDATE**: Operational status changes (e.g., "Harvest Report Approved").
3. **REMINDER**: Impending deadlines (e.g., "Submit Daily Journal").
4. **SYSTEM**: Technical notifications (e.g., "Subscription Renewed").

## 5. Delivery Channel Strategy
- **In-App**: Default for all notifications.
- **Push**: For mobile-first operational updates.
- **SMS**: Reserved for `CRITICAL` alerts and offline field users.
- **Email**: For long-form reports, invoices, and password resets.

## 6. In-App Notification Rules
- Store in a persistent `NotificationStore`.
- Support real-time updates via WebSockets or SSE.
- Group similar notifications (e.g., "5 new harvest reports ready for review").

## 7. Push Notification Rules
- Use Firebase Cloud Messaging (FCM) or Apple Push Notification service (APNs).
- Payload must be < 4KB.
- Always include an `image_url` for high-context alerts (e.g., evidence thumbnail).

## 8. SMS Notification Rules
- **Provider**: Twilio or similar global gateway.
- **Constraint**: Max 160 characters per segment.
- **Usage**: Emergency only (Frost, Safety, Urgent Payroll).

## 9. Email Notification Rules
- **Provider**: SendGrid, Postmark, or Amazon SES.
- **Templates**: Responsive HTML with plain-text fallback.
- **Branding**: Must include the ATLS logo and the specific Tenant's branding if configured.

## 10. Broadcast Notification Rules
- Used for system-wide announcements or tenant-wide alerts.
- **Rule**: Must be authorized by a `SystemAdmin` or `TenantOwner`.

## 11. Critical Alert Escalation
- If a `CRITICAL` alert is not acknowledged within `X` minutes:
    - **Level 1**: Push + In-App.
    - **Level 2**: SMS.
    - **Level 3**: Automated Voice Call or Alert to Superior.

## 12. Retry & Failure Handling
- **Exponential Backoff**: For temporary delivery failures (e.g., 503 from provider).
- **DLQ (Dead Letter Queue)**: For permanent failures; logged for manual review.

## 13. Notification Priority System
- **URGENT**: Immediate delivery.
- **HIGH**: Deliver within 1 minute.
- **NORMAL**: Deliver within 5 minutes.
- **LOW**: Deliver during the next "Digest" cycle.

## 14. Deduplication Strategy
- Use a `deduplication_key` (e.g., `harvest_id:status_change`) to prevent sending 10 notifications for the same event within a short window.

## 15. Delivery Tracking
- Track `Sent`, `Delivered`, and `Opened` status.
- Use a tracking pixel for emails and a callback for SMS gateways.

## 16. Read/Unread State Rules
- Read state must be synced across all devices for the same user.
- "Mark all as read" must be a single-tap action.

## 17. Offline Delivery Handling
- Notifications are queued on the server and delivered as soon as the mobile device reconnects.
- Store a local cache of the last 50 notifications on the mobile device.

## 18. Mobile Notification Constraints
- Support Android Notification Channels (Alerts vs Updates).
- Ensure high-priority notifications can bypass "Do Not Disturb" if allowed by the user.

## 19. Tenant Isolation Rules
- **Strict Partitioning**: A user in Tenant A must never receive a notification regarding Tenant B.
- **Validation**: Every notification request must verify the `recipient_id` belongs to the `tenant_id`.

## 20. User Preference Management
- Users can toggle specific categories (e.g., "Disable Reminders") and channels (e.g., "SMS only for Emergencies").
- **FORBIDDEN**: Users cannot disable `SECURITY` or `SYSTEM` critical alerts.

## 21. Quiet Hours Strategy
- Support user-defined "Quiet Hours" (e.g., 10 PM - 5 AM).
- **Exception**: `CRITICAL` alerts bypass quiet hours.

## 22. Localization & RTL Support
- All notification text must be localized via i18n keys.
- **RTL**: Layout must mirror correctly for Arabic/Hebrew (Right-aligned text, mirrored icons).

## 23. Notification Templates
- Centralized template library managed in the `apps.notifications` app.
- Templates use Jinja2 or Django Template Language (DTL).

## 24. Dynamic Template Variables
- Variables: `{{ user_name }}`, `{{ farm_name }}`, `{{ entity_id }}`, `{{ action_link }}`.
- **Sanitization**: All variables must be HTML-escaped before rendering.

## 25. Event-Driven Integration
- Subscribe to Domain Events via the `EventSystem`.
- `Event(harvest_failed) -> NotificationHandler -> CreateNotification`.

## 26. Async Delivery Pipelines
- **Architecture**: `Event -> Celery Task (Creation) -> Celery Task (Channel Delivery)`.
- **Concurrency**: Dedicated Celery queues for `notifications-urgent` and `notifications-bulk`.

## 27. Notification Analytics
- Track "Click-Through Rate" (CTR) for operational deep-links to measure user engagement and alerting effectiveness.

## 28. Rate Limiting Rules
- **Per-User**: Max 1 SMS per 15 minutes for the same event.
- **Global**: Thresholds to prevent "Notification Storms" during system restarts.

## 29. Anti-Spam Protections
- Forbid sending > 50 in-app notifications to a single user within 1 hour.
- Automatically downgrade priority if a user is offline for > 24 hours.

## 30. Security Notification Rules
- Mandatory notification for: Password change, New device login, MFA disabled.

## 31. Audit Integration
- Every sent notification is recorded in the `AuditDomain`.
- Record the exact payload and the final delivery status.

## 32. Performance Constraints
- **Creation**: < 50ms.
- **Delivery (Internal)**: < 200ms.
- **Delivery (External)**: < 2 seconds for high-priority items.

## 33. AI Safety Rules
- **Synchronous**: AI agents MUST NOT send notifications synchronously in the request-response cycle.
- **Spam**: FORBID implementing loops that send notifications without a deduplication check.
- **Storms**: FORBID bulk notification sends without rate limiting.
- **Cross-Tenant**: FORBID sending any notification that contains data from multiple tenants.
- **Hardcoding**: FORBID hardcoding notification text; always use localized templates.
- **Blocking**: FORBID any notification failure from blocking the primary operational workflow.

## 34. Forbidden Notification Anti-Patterns
- **Generic Titles**: "System Update" (Use "Harvest #123 Approved").
- **Missing Action**: Notifications with no link to fix the problem.
- **Email Everything**: Sending emails for every minor status change.

## 35. Real Agricultural Notification Scenarios
- **Frost Warning**: Sensors detect temperature < 2°C. System sends `URGENT` broadcast to all supervisors via SMS and Push.
- **Pesticide Safety Window**: Field worker tries to enter a block still in the "Safety Window". System alerts the supervisor immediately.

## 36. Future Notification Expansion
- **Voice Calls**: Integration with Amazon Connect/Twilio Voice for emergency broadcasts.
- **WhatsApp**: (Future) Integration for worker communication in regions with high WhatsApp usage.

## 37. Multi-Channel Orchestration
- Logic to decide the best channel: `if (user.online) send(In-App) else send(Push)`.

## 38. Final Notification Enforcement Checklist
- [ ] Notifications are purely event-driven.
- [ ] Delivery is fully asynchronous.
- [ ] Templates are localized and support RTL.
- [ ] User preferences are respected (except for Security).
- [ ] Deduplication keys are used for all operational events.
- [ ] SMS is reserved for Critical/Emergency items.
- [ ] Audit logs capture final delivery status.
- [ ] Rate limiting is enforced at the gateway level.
- [ ] Deep-links are included for all operational alerts.
- [ ] High-priority queue is isolated from bulk traffic.
