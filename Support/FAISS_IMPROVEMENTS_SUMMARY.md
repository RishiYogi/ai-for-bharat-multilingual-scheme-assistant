# ChromaDB Service Implementation Summary

## ChromaDB Migration Benefits

### Why ChromaDB Over FAISS

**ChromaDB Advantages**:
- ✅ Automatic metadata storage (no manual management)
- ✅ Built-in persistence with SQLite (crash-safe)
- ✅ Native metadata filtering with where clauses
- ✅ Simpler codebase (~50 fewer lines)
- ✅ Easier debugging with SQLite inspection tools
- ✅ Automatic UUID generation
- ✅ Single `pip install` setup

**FAISS Challenges** (that ChromaDB solves):
- Manual metadata store management
- Manual index save/load operations
- Post-filtering only (no native metadata filtering)
- Complex index-to-UUID mapping
- Binary index files (harder to debug)

---

## Key Features Implemented

### 1. ✅ Automatic Metadata Management

**ChromaDB Approach**:
```python
# ChromaDB handles everything automatically
collection.add(
    ids=["uuid-1", "uuid-2"],
    embeddings=[[...], [...]],
    documents=["text1", "text2"],
    metadatas=[
        {"scheme_name": "PM Kisan", "category": "agriculture"},
        {"scheme_name": "Solar Scheme", "category": "solar_subsidy"}
    ]
)

# Retrieval is automatic with native filtering
results = collection.query(
    query_embeddings=[[...]],
    where={"category": "agriculture"},
    n_results=5
)
```

**Benefits**:
- ✅ No manual dictionary management
- ✅ Automatic persistence to SQLite
- ✅ Built-in UUID support
- ✅ No index mismatch issues
- ✅ Native metadata filtering

---

### 2. ✅ Eligibility Metadata with Native Filtering

**Metadata Structure**:
```python
{
    "scheme_name": "PM Awas Yojana",
    "category": "housing_aid",
    "state": "all",
    "eligible_gender": "female",
    "eligible_employment": "unemployed,self_employed",  # Comma-separated string
    "chunk_index": 0,
    "source_doc": "pmay_guidelines.pdf"
}
```

**ChromaDB Native Filtering** (category, state, gender):
```python
where_filter = {
    "$and": [
        {"category": "housing_aid"},
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

results = collection.query(
    query_embeddings=[...],
    where=where_filter,
    n_results=top_k * 3  # Retrieve more for employment post-filtering
)
```

**Employment Post-Filtering** (ChromaDB limitation):
```python
# ChromaDB doesn't support "array contains" on comma-separated strings
# Solution: Retrieve 3x more results, then post-filter
filtered_results = [
    r for r in results 
    if employment_matches(r['metadata']['eligible_employment'], user_employment)
][:top_k]
```

**Benefits**:
- ✅ Native filtering for category, state, gender (fast)
- ✅ Reduces irrelevant results sent to LLM
- ✅ Saves LLM tokens and cost
- ✅ More precise recommendations

**Known Limitation**: Employment filtering uses post-processing (acceptable for prototype scale)

---

### 3. ✅ Similarity Scores with Proper Conversion

**ChromaDB Distance**: Cosine distance (0 = identical, 2 = opposite)

**API Score**: Similarity score (1.0 = identical, 0.0 = opposite)

**Conversion Formula**:
```python
score = 1.0 - (distance / 2.0)
```

**Examples**:
- Distance 0.0 → Score 1.0 (identical vectors)
- Distance 1.0 → Score 0.5 (orthogonal vectors)
- Distance 2.0 → Score 0.0 (opposite vectors)

**Search Response**:
```json
{
  "results": [
    {
      "doc_id": "uuid-1",
      "score": 0.89,
      "text": "PM Kisan Samman Nidhi provides financial support...",
      "metadata": {
        "scheme_name": "PM Kisan Samman Nidhi",
        "category": "agriculture",
        "state": "all"
      }
    }
  ],
  "total_docs": 150
}
```

**Use in STAGE 6 Gatekeeper**:
```python
if results[0]['score'] < 0.7:
    return "No relevant schemes found"
else:
    # Call LLM with retrieved chunks
    pass
```

---

### 4. ✅ Comprehensive Debugging Endpoints

**New Endpoints for Observability**:

#### GET /stats
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
      "solar_subsidy": 25
    },
    "states": {
      "all": 80,
      "maharashtra": 20,
      "karnataka": 15
    }
  }
}
```

#### GET /collections
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
1. Verify PDFs were ingested correctly
2. Check category/state distribution
3. Monitor storage growth
4. Debug filtering issues
5. Quick health check without authentication

---

### 5. ✅ Input Validations

**Embedding Dimension Validation**:
```python
if len(doc.embedding) != 1024:
    raise HTTPException(
        status_code=400,
        detail=f"Embedding dimension must be 1024, got {len(doc.embedding)}"
    )
```

**Metadata Normalization**:
```python
# Normalize to lowercase for consistent filtering
metadata['category'] = metadata.get('category', '').lower()
metadata['state'] = metadata.get('state', '').lower()
metadata['eligible_gender'] = metadata.get('eligible_gender', 'any').lower()
```

**Array to String Conversion**:
```python
# ChromaDB doesn't support array metadata
if isinstance(metadata.get('eligible_employment'), list):
    metadata['eligible_employment'] = ','.join(metadata['eligible_employment'])
```

**Benefits**:
- ✅ Prevents dimension mismatch errors
- ✅ Ensures consistent filtering (case-insensitive)
- ✅ Handles ChromaDB metadata limitations
- ✅ Better error messages for debugging

---

## Updated API Endpoints (8 Total)

| Endpoint | Method | Auth | Purpose | Change |
|----------|--------|------|---------|--------|
| `/health` | GET | ❌ No | Health check | No change |
| `/add` | POST | ✅ Yes | Add documents | Added validations |
| `/search` | POST | ✅ Yes | Search with filters | Improved employment filtering |
| `/delete` | POST | ✅ Yes | Delete by ID or scheme | **Behavior changed** |
| `/delete_all` | POST | ✅ Yes | Delete entire collection | **NEW** |
| `/rebuild` | POST | ✅ Yes | Reload collection | No change |
| `/stats` | GET | ❌ No | Detailed statistics | Updated for ChromaDB |
| `/collections` | GET | ❌ No | List collections | **NEW** |

---

## Example Usage

### Adding Documents

```python
import requests

response = requests.post(
    "http://ec2-ip:8000/add",
    headers={"X-API-Key": "your-api-key"},
    json={
        "documents": [
            {
                "embedding": [0.1, 0.2, ...],  # Must be exactly 1024 dimensions
                "text": "PM Kisan Samman Nidhi provides financial support...",
                "metadata": {
                    "scheme_name": "PM Kisan Samman Nidhi",
                    "category": "AGRICULTURE",  # Will be normalized to "agriculture"
                    "state": "ALL",  # Will be normalized to "all"
                    "eligible_gender": "ANY",  # Will be normalized to "any"
                    "eligible_employment": ["unemployed", "self_employed"],  # Will be converted to "unemployed,self_employed"
                    "chunk_index": 0,
                    "source_doc": "pm_kisan.pdf"
                }
            }
        ]
    }
)
```

### Searching with Filters

```python
response = requests.post(
    "http://ec2-ip:8000/search",
    headers={"X-API-Key": "your-api-key"},
    json={
        "query_embedding": [0.1, 0.2, ...],  # 1024 dimensions
        "top_k": 5,
        "category_filter": "agriculture",
        "state_filter": "maharashtra",
        "gender_filter": "female",
        "employment_filter": "unemployed"
    }
)

results = response.json()
for result in results['results']:
    print(f"Score: {result['score']:.2f}")
    print(f"Text: {result['text']}")
    print(f"Scheme: {result['metadata']['scheme_name']}")
```

### Getting Statistics

```python
response = requests.get("http://ec2-ip:8000/stats")
stats = response.json()

print(f"Total vectors: {stats['collection_info']['total_vectors']}")
print(f"Storage size: {stats['storage']['database_size_mb']} MB")
print(f"Categories: {stats['metadata_stats']['categories']}")
```

### Listing Collections

```python
response = requests.get("http://ec2-ip:8000/collections")
collections = response.json()

for coll in collections['collections']:
    print(f"Collection: {coll['name']}, Count: {coll['count']}")
```

---

## Validation in `/add` Endpoint

The `/add` endpoint now validates:

**1. Embedding Dimension**:
```python
if len(doc.embedding) != 1024:
    raise HTTPException(
        status_code=400,
        detail=f"Embedding dimension must be 1024, got {len(doc.embedding)}"
    )
```

**2. Required Metadata Fields**:
```python
for doc in request.documents:
    if 'scheme_name' not in doc.metadata:
        raise HTTPException(status_code=400, detail="metadata must include 'scheme_name'")
    if 'category' not in doc.metadata:
        raise HTTPException(status_code=400, detail="metadata must include 'category'")
    if 'state' not in doc.metadata:
        raise HTTPException(status_code=400, detail="metadata must include 'state'")
```

**3. Metadata Normalization**:
```python
# Normalize to lowercase for consistent filtering
doc.metadata['category'] = doc.metadata['category'].lower()
doc.metadata['state'] = doc.metadata['state'].lower()
if 'eligible_gender' in doc.metadata:
    doc.metadata['eligible_gender'] = doc.metadata['eligible_gender'].lower()
```

**4. Array Conversion**:
```python
# Convert arrays to comma-separated strings (ChromaDB limitation)
if isinstance(doc.metadata.get('eligible_employment'), list):
    doc.metadata['eligible_employment'] = ','.join(doc.metadata['eligible_employment'])
```

This ensures data quality and prevents errors during search operations.

---

## Summary of Improvements

✅ **Automatic Metadata Management**: ChromaDB handles storage and persistence  
✅ **Native Filtering**: Where clauses for category, state, gender (employment post-filtered)  
✅ **Similarity Scores**: Proper conversion from cosine distance to similarity  
✅ **Debugging Endpoints**: `/stats` and `/collections` for observability  
✅ **Input Validations**: Dimension check, metadata normalization, array conversion  
✅ **Simpler Codebase**: ~50 fewer lines than FAISS implementation  

**Known Limitations** (acceptable for prototype):
1. Employment filtering uses post-processing (retrieve 3x more results)
2. Metadata arrays converted to comma-separated strings
3. Slightly higher memory usage than FAISS

All changes are ready for STAGE 4 (Ingestion Pipeline) integration.
