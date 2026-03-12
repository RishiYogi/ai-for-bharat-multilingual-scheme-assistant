# Design.md Update Summary

## Updates Required

The following updates need to be applied to `.kiro/specs/govt-scheme-rag/design.md`:

### 1. Update Category Dropdown Values (2 occurrences)
**Find:** `Agriculture / Healthcare / Education / Housing / Employment`
**Replace with:** `Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme`

**Locations:** Lines 185 and 237 (Page 2: User Input Form sections)

### 2. Update Category API Values (2 occurrences)
**Find:** `agriculture, healthcare, education, housing, employment`
**Replace with:** `solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme`

**Locations:** Lines 288 and 333 (Note sections after Request Format)

### 3. Update FAISS Endpoint Description (1 occurrence)
**Find:** `- \`POST /search\` - k-NN similarity search (k=5, cosine similarity)`
**Replace with:** `- \`POST /search\` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering`

**Location:** Line ~120 (FAISS FastAPI Endpoints section)

### 4. Update Vector Store Usage (1 occurrence)
**Find:** `results = vector_store.search(query_embedding, top_k=5)`
**Replace with:** `results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)`

**Location:** Line ~580 (RAGOrchestratorFunction Vector Store Usage section)

### 5. Add Category Filtering to RAGOrchestratorFunction Responsibilities
**Find the section with 8 responsibilities and replace with 10 responsibilities:**

**Old:**
```
**Responsibilities**:
1. Validate input (required fields, data types)
2. Generate query embedding using Bedrock Titan Embeddings
3. Call FAISS API (POST /search) for k-NN search (k=5)
4. Construct structured reasoning prompt with retrieved chunks
5. Call Bedrock Titan Text Express for LLM generation
6. Parse LLM response into structured JSON
7. Return schemes with eligibility, benefits, citations, confidence
8. Log query and response to CloudWatch
```

**New:**
```
**Responsibilities**:
1. Validate input (required fields, data types)
2. Generate query embedding using Bedrock Titan Embeddings
3. Call FAISS API (POST /search) for k-NN search (k=5)
4. Filter vector search results by category metadata
5. Include category context in LLM prompt
6. Construct structured reasoning prompt with retrieved chunks
7. Call Bedrock Titan Text Express for LLM generation
8. Parse LLM response into structured JSON
9. Return schemes with eligibility, benefits, citations, confidence
10. Log query and response to CloudWatch
```

### 6. Update Technology Stack Frontend Entry
**Find:** `- **Static Frontend**: S3 + CloudFront`
**Replace with:** `- **Static Frontend**: Static HTML/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront`

### 7. Metadata Structure Already Updated ✅
The metadata structure already includes the `category` field at line 625.

### 8. S3 Storage Folders Already Updated ✅
The S3 storage section already includes the `download/` folder at lines 650 and 695.

### 9. CloudWatch Monitoring Note Already Present ✅
The CloudWatch monitoring note is already present at line 710.

## How to Apply Updates

### Option 1: Use Python Script
Run the provided `comprehensive_update.py` script:
```bash
python3 comprehensive_update.py
```

### Option 2: Manual Find & Replace
Use your text editor's find & replace feature to make each change listed above.

### Option 3: Use sed (Linux/Mac)
```bash
cd .kiro/specs/govt-scheme-rag/

# Backup
cp design.md design.md.backup

# Apply updates
sed -i 's/Agriculture \/ Healthcare \/ Education \/ Housing \/ Employment/Solar Subsidy \/ Housing Aid \/ Education Loan \/ Startup Support \/ Jal Jeevan Scheme/g' design.md
sed -i 's/agriculture, healthcare, education, housing, employment/solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme/g' design.md
sed -i 's/- `POST \/search` - k-NN similarity search (k=5, cosine similarity)/- `POST \/search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering/g' design.md
sed -i 's/results = vector_store\.search(query_embedding, top_k=5)/results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)/g' design.md
sed -i 's/- \*\*Static Frontend\*\*: S3 + CloudFront/- **Static Frontend**: Static HTML\/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront/g' design.md
```

## Verification

After applying updates, verify:
1. Category dropdown shows: Solar Subsidy, Housing Aid, Education Loan, Startup Support, Jal Jeevan Scheme
2. Category API values are: solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme
3. FAISS endpoint mentions "optional category metadata filtering"
4. Vector Store Usage includes `category_filter=user_category`
5. RAGOrchestratorFunction has 10 responsibilities (including category filtering)
6. Technology Stack Frontend mentions "3-page flow"
