# ChromaDB Architecture Clarifications

## 1. ChromaDB Distance Metric and Normalization ✅

**Question**: How does ChromaDB handle cosine similarity?

**Answer**: ChromaDB uses cosine distance natively when configured with `hnsw:space = "cosine"`.

### ChromaDB Configuration

```python
# Collection with cosine similarity
collection = chroma_client.get_or_create_collection(
    name="government_schemes",
    metadata={"hnsw:space": "cosine"}  # Cosine distance metric
)
```

### No Manual Normalization Needed

Unlike FAISS IndexFlatIP, ChromaDB handles normalization internally:

```python
# In /add endpoint - no normalization needed
collection.add(
    ids=[str(uuid.uuid4())],
    embeddings=[doc.embedding],  # Raw embeddings (1024-dim)
    documents=[doc.text],
    metadatas=[doc.metadata]
)

# In /search endpoint - no normalization needed
results = collection.query(
    query_embeddings=[request.query_embedding],  # Raw query embedding
    n_results=top_k
)
```

### Distance to Similarity Conversion

ChromaDB returns cosine distance (0 = identical, 2 = opposite):

```python
# Convert distance to similarity score
score = 1.0 - (distance / 2.0)
```

**Examples**:
- Distance 0.0 → Score 1.0 (identical)
- Distance 1.0 → Score 0.5 (orthogonal)
- Distance 2.0 → Score 0.0 (opposite)

### Result
- ✅ ChromaDB handles cosine similarity natively
- ✅ No manual normalization required
- ✅ Simple distance-to-score conversion
- ✅ Scores range from 0.0 to 1.0

---

## 2. Metadata Storage and Filtering

**Question**: How does ChromaDB store metadata with vectors?

**Answer**: **INTEGRATED** - ChromaDB stores metadata alongside vectors in its internal SQLite database.

### Storage Architecture

```python
# Single ChromaDB collection with integrated storage
collection = chroma_client.get_or_create_collection(
    name="government_schemes",
    metadata={"hnsw:space": "cosine"}
)

# Add documents with metadata (all stored together)
collection.add(
    ids=["uuid-1", "uuid-2"],
    embeddings=[[...], [...]],  # 1024-dim vectors
    documents=["text1", "text2"],
    metadatas=[
        {
            "scheme_name": "PM Kisan",
            "category": "agriculture",
            "state": "all",
            "eligible_gender": "any",
            "eligible_employment": "unemployed,self_employed"
        },
        {
            "scheme_name": "Solar Scheme",
            "category": "solar_subsidy",
            "state": "maharashtra",
            "eligible_gender": "any",
            "eligible_employment": "any"
        }
    ]
)
```

### Storage Structure

```
/data/chroma/
  └── chroma.sqlite3          # SQLite database
      ├── Collections table   # Collection metadata
      ├── Embeddings table    # Vector embeddings
      └── Metadata table      # Document metadata
```

### Required Metadata Fields

Each document MUST include:
- `scheme_name` (string) - Name of the government scheme
- `category` (string) - One of: education_skill, solar_subsidy, startup_selfemployment, housing_aid, water_sanitation, agriculture, healthcare, others
- `state` (string) - State code (e.g., "tamil_nadu", "maharashtra") OR "all" for central schemes

Optional but recommended:
- `eligible_gender` (string) - "any", "male", "female", "other"
- `eligible_employment` (string) - Comma-separated: "unemployed,self_employed"
- `chunk_index` (int) - Position of this chunk in the original document
- `source_doc` (string) - Original PDF filename

**Note**: All metadata fields are normalized to lowercase for consistent filtering.

### How Filtering Works

**Native Filtering** (category, state, gender):
```python
# ChromaDB where clause for native filtering
where_filter = {
    "$and": [
        {"category": "agriculture"},
        {"$or": [
            {"state": "maharashtra"},
            {"state": "all"}
        ]},
        {"$or": [
            {"eligible_gender": "female"},
            {"eligible_gender": "any"}
        ]}
    ]
}

# Query with native filtering
results = collection.query(
    query_embeddings=[query_vector],
    where=where_filter,
    n_results=top_k * 3  # Retrieve more for employment post-filtering
)
```

**Post-Filtering** (employment - ChromaDB limitation):
```python
# ChromaDB doesn't support "array contains" on comma-separated strings
# Solution: Retrieve 3x more results, then post-filter
filtered_results = []
for result in results:
    employment_str = result['metadata'].get('eligible_employment', 'any')
    employment_list = employment_str.split(',')
    
    # Check if user's employment matches
    if user_employment in employment_list or 'any' in employment_list:
        filtered_results.append(result)
    
    if len(filtered_results) >= top_k:
        break

return filtered_results[:top_k]
```

### Filtering Logic

**Category + State + Gender Filtering** (native):
```
(metadata.category == user_category) 
AND 
(metadata.state == user_state OR metadata.state == "all")
AND
(metadata.eligible_gender == user_gender OR metadata.eligible_gender == "any")
```

**Employment Filtering** (post-processing):
```
user_employment IN metadata.eligible_employment.split(',') 
OR 
"any" IN metadata.eligible_employment.split(',')
```

**Example**:
- User query: category="agriculture", state="maharashtra", gender="female", employment="unemployed"
- Native filtering matches:
  - ✅ category="agriculture", state="maharashtra", gender="female"
  - ✅ category="agriculture", state="all", gender="any"
  - ❌ category="agriculture", state="karnataka", gender="female" (wrong state)
  - ❌ category="solar_subsidy", state="maharashtra", gender="female" (wrong category)
- Post-filtering for employment:
  - ✅ eligible_employment="unemployed,self_employed" (contains "unemployed")
  - ✅ eligible_employment="any" (matches all)
  - ❌ eligible_employment="employed" (doesn't contain "unemployed")

### Limitations and Trade-offs

**Acceptable for Prototype**:

1. **Employment Post-Filtering**:
   - ChromaDB doesn't support "array contains" on comma-separated strings
   - Solution: Retrieve 3x more results (top_k * 3), then post-filter
   - Impact: May return fewer than top_k results if many don't match employment filter
   - Mitigation: Acceptable for prototype scale (10-20 PDFs, 500-2000 vectors)

2. **Metadata Array Conversion**:
   - ChromaDB stores metadata as simple key-value pairs (no arrays)
   - Solution: Convert arrays to comma-separated strings
   - Example: `["unemployed", "self_employed"]` → `"unemployed,self_employed"`
   - Impact: None (transparent conversion in API)

3. **Native vs Post-Filtering Performance**:
   - Native filtering (category, state, gender): Fast, happens during vector search
   - Post-filtering (employment): Slower, happens after retrieval
   - Impact: Negligible for prototype scale

**Production Alternatives** (if needed later):
- Use separate collections per category (reduces filtering overhead)
- Migrate to Elasticsearch/OpenSearch (better metadata filtering)
- Use Pinecone/Weaviate (native metadata filtering with vectors)

### Persistence

```python
# ChromaDB PersistentClient with automatic persistence
chroma_client = chromadb.PersistentClient(
    path="/data/chroma",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# All operations auto-persist to SQLite
collection.add(...)     # Automatically saved
collection.query(...)   # Reads from disk
collection.delete(...)  # Automatically saved
```

**Storage Structure**:
```
/data/chroma/
  └── chroma.sqlite3      # SQLite database (automatic)
      ├── Collections     # Collection metadata
      ├── Embeddings      # Vector data
      └── Metadata        # Document metadata
```

**Benefits**:
- ✅ Automatic persistence (no manual save/load)
- ✅ Crash-safe (SQLite transactions)
- ✅ Easy to inspect (SQLite tools)
- ✅ Survives EC2 restarts

---

## 3. API Endpoints

**Question**: How many endpoints are created?

**Answer**: **8 endpoints** (updated from 6)

### Endpoint Summary

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/health` | GET | ❌ No | Health check, returns total vectors and dimension |
| `/add` | POST | ✅ Yes (API Key) | Add documents with embeddings to collection |
| `/search` | POST | ✅ Yes (API Key) | Search for similar vectors with optional filters |
| `/delete` | POST | ✅ Yes (API Key) | Delete specific documents by ID or scheme name |
| `/delete_all` | POST | ✅ Yes (API Key) | Delete entire collection and reinitialize |
| `/rebuild` | POST | ✅ Yes (API Key) | Reload collection without restarting server |
| `/stats` | GET | ❌ No | Detailed statistics for debugging |
| `/collections` | GET | ❌ No | List available collections |

### New Endpoints Details

#### `/delete` (Behavior Changed)
**Old FAISS behavior**: Deleted entire index  
**New ChromaDB behavior**: Delete specific documents

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

#### `/delete_all` (NEW)
Replaces old `/delete` behavior - deletes entire collection

**Request**: Empty body

**Response**:
```json
{
  "status": "success",
  "message": "Collection deleted and reinitialized"
}
```

#### `/collections` (NEW)
Lists available ChromaDB collections for debugging

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

### Search Response with Scores

**Example `/search` response**:
```json
{
  "results": [
    {
      "doc_id": "uuid-1",
      "score": 0.89,
      "text": "PM Kisan Samman Nidhi provides financial support of Rs 6000 per year to farmers.",
      "metadata": {
        "scheme_name": "PM Kisan Samman Nidhi",
        "category": "agriculture",
        "state": "all",
        "eligible_gender": "any",
        "eligible_employment": ["unemployed", "self_employed"],  // Converted back to array
        "chunk_index": 0,
        "source_doc": "pm_kisan_guidelines.pdf"
      }
    },
    {
      "doc_id": "uuid-5",
      "score": 0.76,
      "text": "Kisan Credit Card scheme provides short-term credit to farmers...",
      "metadata": {
        "scheme_name": "Kisan Credit Card",
        "category": "agriculture",
        "state": "all",
        "eligible_gender": "any",
        "eligible_employment": ["any"],
        "chunk_index": 2,
        "source_doc": "kcc_scheme.pdf"
      }
    }
  ],
  "total_docs": 150
}
```

**Score interpretation**:
- Score range: 0.0 to 1.0 (converted from cosine distance)
- 1.0 = identical vectors
- 0.8-1.0 = highly similar
- 0.6-0.8 = moderately similar
- <0.6 = low similarity

**Use in STAGE 6 Gatekeeper**:
- Set threshold (e.g., 0.7)
- If top result score < threshold → Don't call LLM, return "No relevant schemes found"
- If top result score >= threshold → Call LLM with retrieved chunks

**Use Cases**:
1. **Verify ingestion**: Check if PDFs were processed correctly
2. **Debug filtering**: See category/state distribution
3. **Monitor storage**: Track index size growth
4. **Troubleshoot**: Quickly see index health without authentication

**Why No Auth?**:
- Read-only endpoint (no sensitive data)
- Useful for quick debugging
- Can be restricted by security group (only accessible from Lambda or your IP)

---

## 4. Summary

### Architecture Decisions

✅ **Distance Metric**: Cosine similarity (native ChromaDB support)  
✅ **Metadata Storage**: Integrated with ChromaDB (SQLite)  
✅ **Filtering**: Native for category/state/gender, post-processing for employment  
✅ **Endpoints**: 8 total (health, add, search, delete, delete_all, rebuild, stats, collections)  
✅ **Observability**: `/stats` and `/collections` endpoints for debugging  
✅ **Validations**: Dimension check (1024), metadata normalization, array conversion  

### Trade-offs (Acceptable for Prototype)

| Aspect | Current Approach | Production Alternative |
|--------|------------------|------------------------|
| Employment Filtering | Post-filtering (3x retrieval) | Separate collections per category |
| Metadata Arrays | Comma-separated strings | Elasticsearch/OpenSearch |
| Scalability | Single EC2 instance | Multi-instance with load balancer |
| Vector Search | ChromaDB (exact + HNSW) | Pinecone/Weaviate (managed) |

### Known Limitations

1. **Employment Post-Filtering**: Retrieve 3x more results to compensate
2. **Metadata Arrays**: Converted to comma-separated strings (transparent to API)
3. **Score Conversion**: `score = 1.0 - (distance / 2.0)` (validated correct)

### Next Steps

1. Complete STAGE 3 (ChromaDB service setup)
2. Test all 8 endpoints thoroughly
3. Use `/stats` and `/collections` to verify collection health
4. Proceed to STAGE 4 (Ingestion Pipeline)
