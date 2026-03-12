# ChromaDB Service - Final Architecture

## All Improvements Implemented ✅

### 1. Dictionary-Based Metadata Store (Built-in with ChromaDB)

**ChromaDB Approach**:
```python
# ChromaDB handles metadata storage automatically
collection.add(
    ids=["uuid-1", "uuid-2"],
    embeddings=[...],
    documents=["text1", "text2"],
    metadatas=[{"scheme_name": "..."}, {"scheme_name": "..."}]
)

# Retrieval is automatic
results = collection.query(query_embeddings=[...])
```

**Benefits**:
- ✅ No manual dictionary management
- ✅ Automatic persistence
- ✅ Built-in UUID support
- ✅ No index mismatch issues

---

### 2. Eligibility Metadata for Better Filtering

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

**Filtering Logic**:
```python
# ChromaDB native filtering for category, state, gender
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

# Retrieve more results for employment post-filtering
results = collection.query(
    query_embeddings=[...],
    where=where_filter,
    n_results=top_k * 3  # Retrieve 3x more for employment filtering
)

# Post-filter for employment (ChromaDB limitation)
filtered_results = [
    r for r in results 
    if employment_matches(r['metadata']['eligible_employment'], user_employment)
][:top_k]
```

**Benefits**:
- ✅ Native ChromaDB filtering for category, state, gender
- ✅ Reduces irrelevant results sent to LLM
- ✅ Saves LLM tokens and cost
- ✅ More precise recommendations

**Eligible Gender Values**:
- `"any"` - No gender restriction
- `"male"` - Only for males
- `"female"` - Only for females
- `"other"` - For other genders

**Eligible Employment Values** (comma-separated string):
- `"any"` - No employment restriction
- `"unemployed"` - Only for unemployed
- `"employed"` - Only for employed
- `"self_employed"` - Only for self-employed
- `"unemployed,self_employed"` - Multiple values

**Known Limitation**: Employment filtering uses post-processing (retrieve 3x more results) because ChromaDB doesn't support "array contains" filtering on comma-separated strings.

---

### 3. UUID Document IDs (Built-in with ChromaDB)

**ChromaDB Approach**:
```python
import uuid

for doc in documents:
    doc_id = str(uuid.uuid4())  # e.g., "a3f2b1c4-..."
    collection.add(
        ids=[doc_id],
        embeddings=[doc.embedding],
        documents=[doc.text],
        metadatas=[doc.metadata]
    )
```

**Benefits**:
- ✅ Globally unique IDs
- ✅ No collision risk
- ✅ Survives collection rebuilds
- ✅ Automatic by ChromaDB

**Example UUID**: `"a3f2b1c4-5d6e-7f8g-9h0i-1j2k3l4m5n6o"`

---

### 4. Automatic Persistence (ChromaDB Feature)

**ChromaDB Persistence**:
```python
# Persistent client with automatic saving
chroma_client = chromadb.PersistentClient(
    path="/data/chroma",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# All operations auto-persist to disk
collection.add(...)  # Automatically saved
collection.query(...)  # Reads from disk
```

**Benefits**:
- ✅ No manual save/load code
- ✅ Automatic crash recovery
- ✅ SQLite-based storage
- ✅ Easy to inspect with SQLite tools

**Storage Structure**:
```
/data/chroma/
  ├── chroma.sqlite3      # Main database
  └── [collection data]   # Embeddings and metadata
```

---

## Complete Metadata Schema

### Required Fields

```python
{
    "scheme_name": str,      # Name of the scheme
    "category": str,         # One of 8 categories (lowercase)
    "state": str            # State code or "all" (lowercase)
}
```

### Optional but Recommended Fields

```python
{
    "eligible_gender": str,           # "any", "male", "female", "other" (lowercase)
    "eligible_employment": str,       # Comma-separated: "unemployed,self_employed"
    "chunk_index": int,               # Position in original document
    "source_doc": str                 # Original PDF filename
}
```

### Complete Example

```python
{
    "text": "PM Kisan Samman Nidhi provides financial support of Rs 6000 per year to farmers.",
    "metadata": {
        "scheme_name": "PM Kisan Samman Nidhi",
        "category": "agriculture",
        "state": "all",
        "eligible_gender": "any",
        "eligible_employment": "unemployed,self_employed",
        "chunk_index": 0,
        "source_doc": "pm_kisan_guidelines.pdf"
    }
}
```

---

## API Endpoints (8 Total)

### 1. POST /add

**Request**:
```json
{
  "documents": [
    {
      "embedding": [0.1, 0.2, ...],  // 1024 dimensions (validated)
      "text": "scheme chunk text",
      "metadata": {
        "scheme_name": "PM Awas Yojana",
        "category": "housing_aid",  // Normalized to lowercase
        "state": "all",  // Normalized to lowercase
        "eligible_gender": "female",  // Normalized to lowercase
        "eligible_employment": ["unemployed", "self_employed"]  // Converted to comma-separated string
      }
    }
  ]
}
```

**Validations**:
- ✅ Embedding dimension must be exactly 1024
- ✅ Metadata fields normalized to lowercase (category, state, gender)
- ✅ Arrays converted to comma-separated strings

**Response**:
```json
{
  "status": "success",
  "added_count": 1,
  "added_ids": ["a3f2b1c4-..."],
  "total_vectors": 150
}
```

### 2. POST /search

**Request**:
```json
{
  "query_embedding": [0.1, 0.2, ...],  // 1024 dimensions
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
      "text": "PM Kisan Samman Nidhi provides...",
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

### 3. GET /health

**Response**:
```json
{
  "status": "healthy",
  "total_vectors": 150,
  "dimension": 1024,
  "timestamp": "2026-03-05T10:30:45.123456"
}
```

### 4. POST /delete

**Purpose**: Delete specific documents by ID or scheme name

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

### 4b. POST /delete_all

**Purpose**: Delete entire collection and reinitialize (replaces old FAISS /delete behavior)

**Request**: Empty body

**Response**:
```json
{
  "status": "success",
  "message": "Collection deleted and reinitialized"
}
```

### 5. POST /rebuild

**Purpose**: Reload ChromaDB collection without restarting the server

**Use Cases**:
- After ingestion pipeline adds new documents
- After manual updates to collection
- Recovery from in-memory issues
- Hot reload during development

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

**Benefits**:
- ✅ No server restart required
- ✅ Zero downtime reload
- ✅ Shows before/after vector counts
- ✅ Useful for debugging

### 6. GET /stats

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
      "education_skill": 30
    },
    "states": {
      "all": 80,
      "maharashtra": 20
    },
    "eligible_genders": {
      "any": 100,
      "female": 30,
      "male": 20
    },
    "eligible_employments": {
      "any": 80,
      "unemployed": 40,
      "self_employed": 30
    }
  },
  "timestamp": "2026-03-05T10:30:45.123456"
}
```

### 7. GET /collections

**Purpose**: List available ChromaDB collections for debugging

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

---

## Filtering Hierarchy

**Retrieval-time filters** (in FAISS service):
1. Category filter (required)
2. State filter (required)
3. Gender filter (NEW)
4. Employment filter (NEW)

**Prompt-time context** (in RAG orchestrator):
1. Age
2. Income range
3. User query

**Benefits of retrieval-time filtering**:
- Reduces irrelevant chunks sent to LLM
- Saves LLM tokens and cost
- More precise recommendations
- Faster response times

---

## Summary of All Improvements

| Improvement | ChromaDB Implementation | Benefit |
|-------------|------------------------|---------|
| Metadata storage | Built-in with ChromaDB | Automatic persistence |
| Document IDs | UUID (automatic) | No index mismatch |
| Persistence | PersistentClient + SQLite | Automatic, crash-safe |
| Filtering | Native where clauses + employment post-filter | More precise (with known limitation) |
| Eligibility | Retrieval-time (category, state, gender) | Saves LLM tokens |
| Dimension validation | Enforced at /add | Prevents embedding errors |
| Metadata normalization | Lowercase conversion | Consistent filtering |

**Known Limitations** (acceptable for prototype):
1. Employment filtering uses post-processing (retrieve 3x more results)
2. Metadata arrays converted to comma-separated strings
3. Score conversion: `score = 1.0 - (distance / 2.0)`

---

## Next Steps for STAGE 4 (Ingestion Pipeline)

When implementing the ingestion pipeline, you'll need to:

1. **Extract eligibility criteria from PDFs**:
   - Parse scheme documents for gender requirements
   - Parse scheme documents for employment requirements
   - Default to "any" if not specified

2. **Structure metadata correctly**:
   ```python
   metadata = {
       "scheme_name": extracted_name,
       "category": determined_category,  # Will be normalized to lowercase
       "state": extracted_state or "all",  # Will be normalized to lowercase
       "eligible_gender": extracted_gender or "any",  # Will be normalized to lowercase
       "eligible_employment": extracted_employment or ["any"],  # Will be converted to comma-separated string
       "chunk_index": chunk_idx,
       "source_doc": pdf_filename
   }
   ```

3. **Call ChromaDB /add endpoint**:
   ```python
   response = requests.post(
       f"{CHROMA_URL}/add",
       headers={"X-API-Key": API_KEY},
       json={
           "documents": [
               {
                   "embedding": embedding_vector,  # Must be 1024 dimensions
                   "text": chunk_text,
                   "metadata": metadata
               }
           ]
       }
   )
   ```

The ChromaDB service is now production-ready for prototype evaluation! 🚀
