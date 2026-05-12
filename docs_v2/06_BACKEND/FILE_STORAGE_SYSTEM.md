# File Storage & Media Persistence Governance

| Metadata | Details |
| :--- | :--- |
| **Document ID** | ATLS-BACK-05 |
| **Status** | AUTHORITATIVE |
| **Version** | 2.0.0 |
| **Owner** | Infrastructure & Backend Team |
| **Applicability** | All ATLS Media Handling & Persistence |

## 1. Storage Philosophy
Media assets (images, videos, documents, audio) are critical operational evidence in ATLS.
- **Security First**: All media is private by default. Access is strictly controlled via signed URLs.
- **Durability**: Assets must survive infrastructure failures and be retrievable for 10+ years for compliance.
- **Tenant Integrity**: Files are physically and logically partitioned by `tenant_id`.

## 2. Object Storage Strategy
- **Provider**: AWS S3 or Google Cloud Storage.
- **Structure**:
```text
/atls-media-bucket
  /{tenant_id}
    /harvest
      /{year}/{month}/{day}/{file_uuid}.jpg
    /personnel
      /avatars/{user_uuid}.png
    /temp
      /{upload_id}/{filename}
```

## 3. Upload Lifecycle
ATLS uses a **Direct-to-Storage** upload flow to protect backend resources.
1. **Request**: Frontend requests a `Presigned URL` from the Backend.
2. **Permission**: Backend validates permissions and returns a URL + `StorageKey`.
3. **Upload**: Frontend uploads directly to Object Storage.
4. **Callback**: Frontend notifies Backend of success; Backend moves file from `temp/` to permanent domain folder.

## 4. Signed URLs
- **Expiry**: Maximum 15 minutes for uploads; 60 minutes for view-only links.
- **Generation**: Done via the `StorageService` using a private key.
- **FORBIDDEN**: Storing absolute URLs in the database. Only store the relative `StorageKey`.

## 5. CDN Rules
- **Access**: Use a CDN (CloudFront/Cloudflare) with Origin Access Identity (OAI).
- **Caching**: Aggressively cache public assets (avatars, system icons).
- **Operational Data**: Private assets must never be cached without signed URL validation at the edge.

## 6. Tenant Isolation
- **Bucket Policy**: Use IAM policies or Bucket Policies that restrict access based on the `{tenant_id}` prefix.
- **Validation**: The `StorageService` must verify that the requested path starts with the user's active `tenant_id`.

## 7. Media Ownership
- Every file must be linked to a `Media` record in the database.
- The `Media` record tracks `uploaded_by`, `tenant_id`, `mime_type`, `file_size`, and the associated domain entity (e.g., `HarvestReport`).

## 8. File Validation
- **MIME Type**: Validate against an allow-list (e.g., `image/jpeg`, `application/pdf`).
- **File Size**: Hard limits per type (e.g., Image: 10MB, Video: 100MB).
- **Magic Bytes**: Verify file headers to prevent extension spoofing.

## 9. Virus Scanning
- **Process**: All incoming files in `temp/` must be scanned (e.g., ClamAV) before being moved to permanent storage.
- **Automation**: Triggered via S3 Event Notifications (Lambda/Celery).

## 10. Compression Rules
- **Images**: Automatically generate WebP versions and thumbnails (200x200).
- **Documents**: Compress PDFs where possible without losing legibility.
- **Target**: High-quality operational photos should be < 1MB.

## 11. Video Processing
- **Transcoding**: Convert all uploaded videos to H.264/H.265 via an async pipeline.
- **Adaptive Streaming**: Generate HLS manifests for smooth mobile playback in low-bandwidth farm environments.

## 12. Async Upload Processing
- Use Celery to handle post-upload tasks:
    - Metadata extraction (EXIF data for GPS).
    - Thumbnail generation.
    - OCR for scanned invoices/logs.

## 13. Media Recovery
- **Soft Delete**: Files are moved to a `trash/` prefix for 30 days before permanent deletion.
- **Versioning**: Enable bucket versioning to recover from accidental overwrites.

## 14. Retention Rules
- **Standard**: 10 years for harvest and pesticide records.
- **Ephemeral**: 24 hours for temporary uploads and system logs.

## 15. Audit Logging
- Log every `GET`, `PUT`, and `DELETE` operation on the bucket.
- Record the `user_id` and `ip_address` for every signed URL request.

## 16. Access Permissions
- **System**: Only the `atls-backend` service account has `RW` access.
- **User**: Users have zero direct access; they must use the ATLS application proxy/signed URLs.

## 17. Performance Constraints
- **URL Generation**: < 20ms.
- **Latency**: Use regional buckets closest to the farm clusters to minimize latency.

## 18. AI Safety Rules
- **Public Buckets**: AI agents MUST NOT enable public access or "Static Website Hosting" on any media bucket.
- **Orphan Media**: FORBID deleting database records without a corresponding cleanup task for the physical file.
- **RAM Uploads**: FORBID reading large files into memory; use streams or direct-to-storage uploads.
- **Sync Processing**: FORBID synchronous video or image processing in the request-response cycle.
- **Unsafe Types**: FORBID uploading executable files (`.exe`, `.sh`, `.php`, `.js`).

## 19. Forbidden Storage Anti-Patterns
- **Local Storage**: Never store operational media on the local server filesystem.
- **Base64**: Never store images as Base64 strings in the database.
- **Predictable Names**: Never use original filenames in storage; use UUIDs to prevent collisions and information leakage.

## 20. Agricultural Media Scenarios
- **Pesticide Invoice**: Farmer uploads a PDF invoice. System scans for viruses, extracts the date and vendor via OCR, and stores it in the `finance` folder.
- **Harvest Evidence**: Field worker takes 5 photos of a crop load. Backend generates 200px thumbnails for the dashboard and stores the 4K originals for quality disputes.

## 21. Enforcement Checklist
- [ ] Bucket is private (Block Public Access enabled).
- [ ] Direct-to-storage upload flow implemented.
- [ ] Signed URLs used for all private media.
- [ ] Tenant-ID partitioning verified in the path.
- [ ] File type allow-list enforced.
- [ ] Virus scanning pipeline is active.
- [ ] Thumbnails generated asynchronously.
- [ ] No absolute URLs stored in the DB.
- [ ] Soft-delete policy active.
