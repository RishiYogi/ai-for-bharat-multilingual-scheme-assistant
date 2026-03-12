# ChromaDB Service API Endpoints

## Complete Endpoint Reference (8 Total)

| Endpoint | Method | Auth Required | Purpose | Use Case |
|----------|--------|---------------|---------|----------|
| `/health` | GET | ❌ No | Health check | Monitoring, load balancer checks |
| `/add` | POST | ✅ Yes | Add documents with embeddings | Ingestion pipeline |
| `/search` | POST | ✅ Yes | Search with filters | RAG orchestrator queries |
| `/delete` | POST | ✅ Yes | Delete by ID or scheme name | Selective deletion |
| `/delete_all` | POST | ✅ Yes | Delete entire collection | Reset/cleanup |
| `/rebuild` | POST | ✅ Yes | Reload collection | Hot reload after ingestion |
| `/stats` | GET | ❌ No | Detailed statistics | Debugging, monitoring |
| `/collections` | GET | ❌ No | List collections | Debugging |

---

## 1. GET /health

**Purpose**: Quick health check

**Authentication**: None

**Response**:
```json
{
  "status": "healthy",
  "total_vectors": 150,
  "dimension": 1024,
  "timestamp": "2026-03-05T10:30:45.123456"
}
```

**Use Cases**:
- Load balancer health checks
- Monitoring systems
- Quick status verification

---

## 2. POST /add

**Purpose**: Add documents with embeddings to ChromaDB collection

**Authentication**: Required (X-API-Key header)

**Request**:
```json
{
  "documents": [
    {
      "embedding": [0.1, 0.2, ..., 0.9],  // Must be exactly 1024 float values
      "text": "PM Kisan Samman Nidhi provides financial support...",
      "metadata": {
        "scheme_name": "PM Kisan Samman Nidhi",
        "category": "agriculture",  // Will be normalized to lowercase
        "state": "all",  // Will be normalized to lowercase
        "eligible_gender": "any",  // Will be normalized to lowercase
        "eligible_employment": ["unemployed", "self_employed"],  // Will be converted to comma-separated string
        "chunk_index": 0,
        "source_doc": "pm_kisan_guidelines.pdf"
      }
    }
  ]
}
```

**Validations**:
- ✅ Embedding dimension must be exactly 1024 (enforced)
- ✅ Metadata fields normalized to lowercase (category, state, gender)
- ✅ Arrays converted to comma-separated strings (eligible_employment)

**Response**:
```json
{
  "status": "success",
  "added_count": 1,
  "added_ids": ["a3f2b1c4-5d6e-7f8g-9h0i-1j2k3l4m5n6o"],
  "total_vectors": 151
}
```

**Required Metadata Fields**:
- `scheme_name` (string)
- `category` (string) - One of: education_skill, solar_subsidy, startup_selfemployment, housing_aid, water_sanitation, agriculture, healthcare, others
- `state` (string) - State code or "all"

**Optional Metadata Fields**:
- `eligible_gender` (string) - "any", "male", "female", "other"
- `eligible_employment` (array) - ["any"], ["unemployed"], ["employed"], ["self_employed"]
- `chunk_index` (int)
- `source_doc` (string)

**Use Cases**:
- Ingestion pipeline adding processed PDFs
- Bulk document uploads
- Collection population

---

## 3. POST /search

**Purpose**: Search for similar vectors with eligibility filtering

**Authentication**: Required (X-API-Key header)

**Request**:
```json
{
  "query_embedding": [0.1, 0.2, ..., 0.9],  // 1024 float values
  "top_k": 5,
  "category_filter": "agriculture",
  "state_filter": "maharashtra",
  "gender_filter": "female",
  "employment_filter": "unemployed"
}
```

**Response**:
```json
{
  "results": [
    {
      "doc_id": "a3f2b1c4-...",
      "score": 0.89,
      "text": "PM Kisan Samman Nidhi provides financial support...",
      "metadata": {
        "scheme_name": "PM Kisan Samman Nidhi",
        "category": "agriculture",
        "state": "all",
        "eligible_gender": "any",
        "eligible_employment": ["unemployed", "self_employed"]
      }
    }
  ],
  "total_docs": 150
}
```

**Query Parameters**:
- `query_embedding` (required) - 1024-dimensional vector
- `top_k` (optional, default=5) - Number of results (1-20)
- `category_filter` (optional) - Filter by category
- `state_filter` (optional) - Filter by state
- `gender_filter` (optional) - Filter by eligible gender
- `employment_filter` (optional) - Filter by eligible employment

**Filtering Logic**:
```
ChromaDB native filtering for category, state, gender:
- category == category_filter (if provided)
- (state == state_filter OR state == "all") (if provided)
- (eligible_gender == gender_filter OR eligible_gender == "any") (if provided)

Employment filtering uses post-processing:
- Retrieve top_k * 3 results
- Filter for employment match
- Return top_k results
```

**Known Limitation**: Employment filtering uses post-processing because ChromaDB doesn't support "array contains" on comma-separated strings. The service retrieves 3x more results to compensate.

**Score Interpretation**:
- 1.0 = Identical vectors
- 0.8-1.0 = Highly similar
- 0.6-0.8 = Moderately similar
- <0.6 = Low similarity

**Use Cases**:
- RAG orchestrator retrieving relevant schemes
- User query processing
- Similarity search with eligibility constraints

---

## 4. POST /delete

**Purpose**: Delete specific documents by ID or scheme name

**Authentication**: Required (X-API-Key header)

**Request (by IDs)**:
```json
{
  "ids": ["uuid-1", "uuid-2"]
}
```

**Request (by scheme name)**:
```json
{
  "scheme_name": "PM Kisan Samman Nidhi"
}
```

**Response**:
```json
{
  "status": "success",
  "deleted_count": 5,
  "message": "Deleted 5 documents"
}
```

**Use Cases**:
- Remove specific documents
- Delete all chunks for a scheme
- Selective cleanup

---

## 5. POST /delete_all

**Purpose**: Delete entire collection and reinitialize

**Authentication**: Required (X-API-Key header)

**Request**: Empty body

**Response**:
```json
{
  "status": "success",
  "message": "Collection deleted and reinitialized"
}
```

**Use Cases**:
- Reset collection during development
- Clean slate before re-ingestion
- Emergency cleanup

**Warning**: This deletes ALL vectors and metadata. Use with caution!

---

## 6. POST /rebuild

**Purpose**: Reload ChromaDB collection without restarting server

**Authentication**: Required (X-API-Key header)

**Request**: Empty body

**Response**:
```json
{
  "status": "success",
  "message": "Collection rebuilt",
  "old_vector_count": 100,
  "new_vector_count": 150,
  "timestamp": "2026-03-05T10:30:45.123456"
}
```

**Use Cases**:
- After ingestion pipeline adds new documents
- Hot reload during development
- Recovery from in-memory issues
- Manual collection updates

**Benefits**:
- ✅ Zero downtime
- ✅ No server restart required
- ✅ Shows before/after counts
- ✅ Instant reload

**Example Workflow**:
```bash
# 1. Ingestion pipeline adds documents
# 2. Call /rebuild to refresh collection
curl -X POST http://ec2-ip:8000/rebuild \
  -H "X-API-Key: your-api-key"

# 3. New documents are now searchable
```

---

## 7. GET /stats

**Purpose**: Detailed statistics for debugging and monitoring

**Authentication**: None (for easy debugging)

**Response**:
```json
{
  "status": "healthy",
  "collection_info": {
    "name": "government_schemes",
    "total_vectors": 150,
    "dimension": 1024,
    "distance_metric": "cosine"
  },
  "storage": {
    "persist_directory": "/data/chroma",
    "database_size_mb": 2.5
  },
  "metadata_stats": {
    "total_documents": 150,
    "categories": {
      "agriculture": 45,
      "education_skill": 30,
      "solar_subsidy": 25,
      "healthcare": 20,
      "housing_aid": 15,
      "water_sanitation": 10,
      "startup_selfemployment": 3,
      "others": 2
    },
    "states": {
      "all": 80,
      "maharashtra": 20,
      "karnataka": 15,
      "tamil_nadu": 12,
      "delhi": 10,
      "gujarat": 8,
      "rajasthan": 5
    },
    "eligible_genders": {
      "any": 100,
      "female": 30,
      "male": 20
    },
    "eligible_employments": {
      "any": 80,
      "unemployed": 40,
      "self_employed": 30,
      "employed": 20
    }
  },
  "timestamp": "2026-03-05T10:30:45.123456"
}
```

**Use Cases**:
- Verify ingestion completed successfully
- Check category/state distribution
- Monitor storage growth
- Debug filtering issues
- Quick health check

**Why No Auth?**:
- Read-only endpoint
- No sensitive data exposed
- Useful for quick debugging
- Can be restricted by security group

---

## 8. GET /collections

**Purpose**: List available ChromaDB collections for debugging

**Authentication**: None (for easy debugging)

**Response**:
```json
{
  "collections": [
    {
      "name": "government_schemes",
      "count": 150,
      "metadata": {"hnsw:space": "cosine"}
    }
  ]
}
```

**Use Cases**:
- Verify collection exists
- Check collection configuration
- Debug collection issues
- Quick status check

---

## Authentication

All write endpoints (`/add`, `/delete`, `/delete_all`, `/rebuild`) and `/search` require API key authentication.

**Header Format**:
```
X-API-Key: your-secure-api-key-here
```

**Setting API Key**:
```bash
# In .env file
CHROMA_API_KEY=your-secure-api-key-here-change-this
```

**Example Request**:
```bash
curl -X POST http://ec2-ip:8000/add \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"documents": [...]}'
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request**:
```json
{
  "detail": "metadata must include 'scheme_name'"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Invalid API key"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Error adding documents: <error message>"
}
```

---

## Example Usage Workflows

### Workflow 1: Ingestion Pipeline

```python
import requests

# 1. Generate embedding (must be 1024 dimensions)
embedding = generate_embedding(chunk_text)

# 2. Add to ChromaDB
response = requests.post(
    "http://ec2-ip:8000/add",
    headers={"X-API-Key": "your-api-key"},
    json={
        "documents": [{
            "embedding": embedding,
            "text": chunk_text,
            "metadata": {
                "scheme_name": "PM Kisan",
                "category": "agriculture",  # Will be normalized to lowercase
                "state": "all",
                "eligible_gender": "any",
                "eligible_employment": ["unemployed"]  # Will be converted to comma-separated string
            }
        }]
    }
)

# 3. Rebuild collection (if batch processing)
requests.post(
    "http://ec2-ip:8000/rebuild",
    headers={"X-API-Key": "your-api-key"}
)
```

### Workflow 2: RAG Query

```python
# 1. Generate query embedding
query_embedding = generate_embedding(user_query)

# 2. Search with filters
response = requests.post(
    "http://ec2-ip:8000/search",
    headers={"X-API-Key": "your-api-key"},
    json={
        "query_embedding": query_embedding,
        "top_k": 5,
        "category_filter": user_category,
        "state_filter": user_state,
        "gender_filter": user_gender,
        "employment_filter": user_employment
    }
)

results = response.json()['results']

# 3. Check gatekeeper threshold
if results[0]['score'] < 0.7:
    return "No relevant schemes found"

# 4. Send to LLM
llm_response = call_llm(results)
```

### Workflow 3: Monitoring

```python
# Check stats periodically
response = requests.get("http://ec2-ip:8000/stats")
stats = response.json()

print(f"Total vectors: {stats['index_info']['total_vectors']}")
print(f"Storage size: {stats['storage']['total_size_mb']} MB")
print(f"Categories: {stats['metadata_stats']['categories']}")
```

---

## Summary

**8 endpoints total**:
- 3 read-only (no auth): `/health`, `/stats`, `/collections`
- 5 write/search (auth required): `/add`, `/search`, `/delete`, `/delete_all`, `/rebuild`

**Key Features**:
- ✅ UUID-based document IDs (automatic)
- ✅ Built-in metadata storage with ChromaDB
- ✅ SQLite persistence (automatic, crash-safe)
- ✅ Eligibility filtering (gender + employment)
- ✅ Hot reload with `/rebuild`
- ✅ Comprehensive stats with `/stats`
- ✅ Dimension validation (1024 enforced)
- ✅ Metadata normalization (lowercase)

**Known Limitations** (acceptable for prototype):
- Employment filtering uses post-processing (retrieve 3x more)
- Metadata arrays converted to comma-separated strings
- Score conversion: `score = 1.0 - (distance / 2.0)`

Ready for STAGE 3 implementation! 🚀
