# Media & Operational Evidence Domain

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-DOM-MED |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Operations & Backend Team |
| **Applicability** | Global Media Storage & Evidence Verification |

## 1. Media Domain Philosophy
In ATLS, media is more than just "files"; it is **Operational Evidence**. Whether it's a photo of a harvest load, a video of a broken tractor, or a voice note from a field worker, media serves as the objective truth for agricultural operations.
- **Evidence-First**: Every file must prove a physical action or state.
- **Context-Aware**: Media is useless without its associated metadata (GPS, Timestamp, Actor).
- **Resilient**: Capturing evidence must work in deep-field locations with zero connectivity.

## 2. Operational UX Evidence Principles
- **One-Tap Capture**: Minimize friction for field workers.
- **Automatic Verification**: Use background processes to verify the location and time of capture.
- **Tamper Evidence**: Detect if a photo was taken live or uploaded from a local gallery (where prohibited).

## 3. Media Aggregate Structure
The core aggregate is the `Media` entity:
- **Identifier**: `media_id` (UUIDv7).
- **Storage**: `storage_key`, `bucket_name`, `provider`.
- **Meta**: `mime_type`, `file_size`, `original_filename`.
- **Context**: `tenant_id`, `uploaded_by`, `captured_at`, `synced_at`.
- **Evidence**: `gps_coordinates` (Point), `device_metadata` (JSON).
- **Linking**: `parent_type` (e.g., `Harvest`), `parent_id`.

## 4. Media Ownership Rules
- **Mandatory Parent**: Every media record must belong to a parent operational entity.
- **Transfer of Ownership**: When a "Temporary Upload" is linked to a `HarvestReport`, the `Media` record is updated to reflect this permanent association.
- **Deletion**: Deleting a parent entity must trigger the deletion (or archival) of all its linked media.

## 5. Evidence Linking Strategy
- Use a **Generic Foreign Key** or a specific **MediaLink** table to associate media with diverse aggregates across the system without creating DB-level circular dependencies.

## 6. Upload Lifecycle
1. **Presigned URL**: Frontend requests a secure upload target.
2. **Transfer**: Client uploads directly to the `temp/` storage prefix.
3. **Registration**: Client notifies the Media Domain of the successful upload.
4. **Validation**: Async pipeline scans for viruses and extracts metadata.
5. **Promotion**: Upon domain logic completion, the file is moved to its permanent `tenant/` path.

## 7. Temporary Upload Handling
- Media in the `temp/` state is automatically purged after 24 hours if not linked to a parent entity.

## 8. Media Verification Workflow
- For critical reports (e.g., Pesticide Application), the system compares the `captured_at` timestamp with the `synced_at` timestamp and the GPS location with the target `Field` boundary to flag discrepancies.

## 9. Image Handling Rules
- **Standard**: WebP for web delivery; original preserved for audit.
- **Exif**: Mandatory extraction of `Orientation`, `Software`, and `GPS`.

## 10. Video Handling Rules
- **Transcoding**: Automatically convert to H.264/H.265 for cross-device compatibility.
- **Adaptive**: Generate multiple resolutions (360p, 720p, 1080p) for low-bandwidth environments.

## 11. Voice Note Rules
- **Format**: Opus/Ogg for high compression.
- **Transcription**: Automatically trigger an AI transcription service for searchable "Audio Logs".

## 12. Document Attachment Rules
- **Support**: PDF, DOCX, XLSX.
- **Security**: Mandatory virus scan before allow-listing for view.

## 13. Metadata Extraction
- **Rule**: Extraction must happen asynchronously via a Celery worker.
- **Fields**: Resolution, Color space, Bitrate, EXIF tags, GPS.

## 14. EXIF & GPS Rules
- **Operational Requirement**: GPS metadata must be checked against the active `Enclosure` or `Block` during harvest.
- **Privacy**: Strip GPS metadata before sharing media outside the farm's tenant boundary.

## 15. Media Compression Strategy
- **Client-Side**: Compress to < 500KB before upload for mobile users on Edge/3G.
- **Server-Side**: Generate "Display Versions" to reduce data usage for dashboard users.

## 16. Thumbnail Generation
- Generate `sm` (100x100), `md` (400x400), and `lg` (1200px width) versions for all images.
- **Videos**: Extract a frame at 0.5s for the thumbnail.

## 17. Offline Media Strategy
- **Queueing**: Store media in the device's local persistent storage (IndexedDB/FileSystem) until a stable connection is detected.
- **Retries**: Implement exponential backoff for large file uploads.

## 18. Sync Recovery Rules
- If an upload is interrupted, the frontend must resume from the last successful byte (using `Range` headers if supported by the provider).

## 19. Media Deduplication
- (Future) Use Content-Addressable Storage (CAS) hashes (SHA-256) to identify duplicate files within a tenant and save storage space.

## 20. Storage Partitioning
- Path: `/{tenant_id}/{entity_type}/{year}/{month}/{file_uuid}.ext`.

## 21. Tenant Isolation
- **Verification**: The `StorageService` must never accept or provide a path that does not start with the requester's `tenant_id`.

## 22. Signed URL Strategy
- All private media is served via **Short-Lived Signed URLs** (max 60 mins).
- **Public**: Only system-level assets (icons, brand logos) can be public.

## 23. Media Security Rules
- **Encryption**: AES-256 at rest.
- **Integrity**: MD5 checksum verification upon upload completion.

## 24. Virus Scanning Rules
- **Process**: Mandatory for all uploads.
- **Action**: Files flagged as infected are immediately deleted and the `uploaded_by` user's account is flagged for review.

## 25. Media Access Permissions
- **Rule**: If a user cannot view a `HarvestReport`, they cannot view its linked `Media`.
- **Validation**: Signed URL generation requires a permission check against the parent entity.

## 26. Media Read Models
- Use a `MediaGallery` read model for fast rendering of "All Photos in Block X" without scanning every operational log.

## 27. Search & Filtering
- Support filtering by `mime_type`, `uploader`, `date_range`, and `parent_entity`.

## 28. Media Retention Rules
- **Standard**: 10 years for compliance.
- **Ephemeral**: 30 days for system logs/temporary files.

## 29. Media Archival Strategy
- Move inactive media (> 24 months old) to cold storage (e.g., AWS S3 Glacier).

## 30. Async Processing Pipelines
- `Upload -> Virus Scan -> Metadata -> Thumbnail -> OCR -> Index`.

## 31. OCR & AI Extraction
- **Invoices**: Extract vendor, amount, and date from scanned PDFs.
- **Damage Detection**: (Future) AI analysis of equipment photos to flag repair needs.

## 32. Performance Constraints
- **Presigned URL generation**: < 50ms.
- **Dashboard Thumbnail load**: < 200ms (via CDN).

## 33. Mobile Media UX Constraints
- **Low-End Devices**: Limit background upload threads to 1.
- **Data Usage**: Prompt user before uploading videos on cellular data.

## 34. AI Safety Rules
- **Orphan Media**: AI agents MUST NOT implement logic that leaves "Orphan Media" (files in storage with no database record).
- **Public Buckets**: FORBID enabling public access on any operational media bucket.
- **Base64**: FORBID storing media as Base64 strings in the database; use object storage.
- **Sync Video**: FORBID synchronous video processing or transcoding.
- **Unsafe Types**: FORBID uploads of `.exe`, `.js`, `.html`, or other execution-capable types.
- **Validation**: FORBID signed URL generation without a valid parent-entity permission check.
- **Access**: FORBID any logic that allows one tenant to access another tenant's `storage_key`.

## 35. Forbidden Media Anti-Patterns
- **Local Server Storage**: Never store media on the application server's local disk.
- **Filenames as IDs**: Never rely on the original user filename for storage; use UUIDs.
- **Global Pointers**: Using absolute URLs in the database; store only relative keys.

## 36. Real Agricultural Media Scenarios
- **Harvest Batch Quality**: A supervisor takes 3 photos of a grape bin. The system tags them with the specific load ID and GPS of the field, allowing the winery to verify the origin upon delivery.
- **Broken Irrigation Pipe**: A worker records a 10-second video of a leak. The system transcodes it and attaches it to an `EquipmentRepair` task, notifying the maintenance team.

## 37. Future Media Expansion
- **AR Evidence**: (Future) AR-tagged photos that overlay field boundaries onto the captured image for 100% location certainty.

## 38. Final Media Enforcement Checklist
- [ ] Media always has a parent entity.
- [ ] Direct-to-storage upload is used.
- [ ] Signed URLs protect all operational files.
- [ ] Tenant-ID partitioning is active.
- [ ] Virus scanning pipeline is operational.
- [ ] Thumbnails generated asynchronously.
- [ ] Metadata (GPS) extracted for all photos.
- [ ] Retention policy configured.
- [ ] No Base64 in the database.
