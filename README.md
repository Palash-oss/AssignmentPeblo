# Peblo TV — Full-Stack Kids' Streaming Platform

Peblo TV is an end-to-end kids' streaming media system featuring an **Internal Editorial CMS**, a **FastAPI + PostgreSQL Backend**, and a public **Netflix-style Viewer UI**.

---

## 🚀 Quick Start (One-Command Launch)

Bring up the entire stack instantly from a clean checkout:

```bash
docker-compose up --build
```

### Access URLs:
- **Viewer UI (Netflix Experience)**: [http://localhost:3001](http://localhost:3001)
- **Internal CMS (Editorial Tool)**: [http://localhost:3000](http://localhost:3000)
- **API Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📜 Architectural Questions & System Decisions

### 1. Atomic Publishing Architecture
- **Implementation**: `execute_catalog_publish` serializes the published catalogue JSON and writes it to a staging file (`catalog.json.tmp_<PID>`) in the storage backend. Once fully written and flushed (`fsync`), it calls `os.replace` to atomically swap the staging file with the live `catalog.json`.
- **Mid-Publish Death**: If the server or container dies mid-publish, only the unlinked temporary `.tmp` file remains in storage. The live `catalog.json` is never overwritten in place and remains untouched and clean. On subsequent runs, orphaned `.tmp` files are ignored and overwritten. A reader never sees a half-written file.

### 2. Storage Abstraction & Cloudflare R2 Migration
- **Abstraction**: `StorageBackend` defines an abstract base class with `save`, `save_atomic`, `get_url`, `delete`, `exists`, and `read`.
- **R2 Migration**: To move to Cloudflare R2:
  1. Create a `R2Storage(StorageBackend)` class in `backend/app/services/storage.py` using `boto3` (S3-compatible endpoint).
  2. Update the single factory function `get_storage()` to return `R2Storage()`.
  3. **Zero call sites** across API endpoints or services need to change.

### 3. Search Implementation & Scale Bottlenecks
- **Implementation**: `GET /catalog/search` executes SQL queries joining `Show`, `Season`, and `Episode` tables using `ILIKE` substring matching and array checks, composing `q`, `category`, `language`, and `section` with strict `AND` logic.
- **Scale Limit**: Substring `ILIKE '%query%'` requires full table scans. Performance degrades around **50,000 to 100,000 episode rows** under high concurrency.
- **Next Step**: At scale, transition to PostgreSQL Full-Text Search (`tsvector`/`tsquery` with GIN indexes) or an external index engine like **Meilisearch** or **Elasticsearch** synchronized via database triggers.

### 4. Pre-Published Catalogue vs. On-Demand Database Queries
- **Why Pre-Publish**: Public kids' streaming browsing is heavily read-dominant. Serving static `catalog.json` direct from storage yields $O(1)$ response times, zero database load during traffic spikes, and extreme infrastructure stability.
- **Pain Points**: Editorial edits in CMS do not immediately reflect on the Viewer UI until an explicit Publish job succeeds (staleness window). In addition, validation blocks prevent publishing fixes until all blocking issues across the catalogue are resolved.

### 5. Time-Boxed Scope & Trade-offs
- **Omitted SSO Login**: Used server-side role dependency headers (`X-User-Role: admin` / `editor`) instead of complex OAuth2/OIDC servers to focus on platform validation rules.
- **Mock Player**: Implemented interactive video player thumbnail overlays instead of real-time HLS video encoding.

### 6. AI Tools Usage & Verification (Explicitly Graded)
- **Tools**: Gemini 3.6 Flash / Antigravity pair programmer.
- **Accepted Output**: Scaffold structure for Pydantic V2 schemas, Pillow image decoding, and TanStack Query state setup.
- **Rejected / Corrected Output**:
  - *Atomic File Swap*: AI initially proposed writing directly to `catalog.json` using `open("catalog.json", "w")`. I rejected this because interrupting `open()` leaves corrupted/empty files. Replaced with staging file swap (`os.replace`) with `fsync`.
  - *Seed Transaction Abort*: AI initially wrapped `db.add()` in a try/except `IntegrityError` without savepoint handling. When `ep_9001` failed, SQLAlchemy aborted the entire session transaction, wiping out preceding seeded shows. I corrected it to run pre-check queries before insertion, ensuring valid seed data is preserved while collision issues are cleanly logged.

---

## ⏱️ Time Spent Breakdown

| Part | Description | Time Spent |
| :--- | :--- | :--- |
| **Part A** | Backend (FastAPI, Models, Storage, Image Validator, Publish Job, Search, Pytest) | ~3.5 hours |
| **Part B** | Internal CMS (React, TanStack Query, Artwork Upload Slots, Validation Report, History) | ~2.5 hours |
| **Part C** | Viewer UI (Netflix Layout, Hero Banner, Season 0 Filter, Language Switcher, Search) | ~2.5 hours |
| **Part D** | Docker Compose, GitHub Actions CI/CD Pipeline, Health Check, Security Config | ~1.0 hour |
| **Part E** | README & Technical Documentation | ~0.5 hours |

---

## 🧪 Running Tests Locally

To run the backend test suite locally:

```bash
cd backend
python -m pytest -v
```
