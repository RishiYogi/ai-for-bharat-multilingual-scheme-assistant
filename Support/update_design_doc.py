#!/usr/bin/env python3
"""
Script to update the design.md file with the requested changes for govt-scheme-rag spec.
"""

def update_design_md():
    # Read the file
    with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update 1: Replace category values in Page 2 User Input Form sections
    # Old: Agriculture / Healthcare / Education / Housing / Employment
    # New: Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme
    content = content.replace(
        '- **Category** (dropdown, required): Agriculture / Healthcare / Education / Housing / Employment',
        '- **Category** (dropdown, required): Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme'
    )
    
    # Update 2: Add category field to Request Format sections and update note
    # Find and replace the request format JSON blocks
    old_request_1 = '''**Request Format**:
```json
{
  "name": "string",
  "age": 25,
  "city": "Mumbai",
  "gender": "Male",
  "income_range": "3-5L",
  "language": "Hindi",
  "query": "मुझे कृषि योजनाओं के बारे में बताएं"
}
```'''
    
    new_request_1 = '''**Request Format**:
```json
{
  "name": "string",
  "age": 25,
  "city": "Mumbai",
  "gender": "Male",
  "income_range": "3-5L",
  "category": "solar_subsidy",
  "language": "Hindi",
  "query": "मुझे कृषि योजनाओं के बारे में बताएं"
}
```

**Note**: The `category` field is required and must be one of: solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme'''
    
    content = content.replace(old_request_1, new_request_1)
    
    # Update 3: Update metadata structure to include category field
    old_metadata = '''**Metadata Structure**:
```json
{
  "doc_id_0": {
    "scheme_id": "pm-kisan-2024",
    "scheme_name": "PM-KISAN",
    "chunk_text": "...",
    "chunk_index": 0,
    "department": "Agriculture",
    "state": "All India",
    "city": "All",
    "source_url": "https://pmkisan.gov.in/...",
    "last_updated": "2024-03-15"
  }
}
```'''
    
    new_metadata = '''**Metadata Structure**:
```json
{
  "doc_id_0": {
    "scheme_id": "pm-kisan-2024",
    "scheme_name": "PM-KISAN",
    "category": "agriculture",
    "chunk_text": "...",
    "chunk_index": 0,
    "department": "Agriculture",
    "state": "All India",
    "city": "All",
    "source_url": "https://pmkisan.gov.in/...",
    "last_updated": "2024-03-15"
  }
}
```'''
    
    content = content.replace(old_metadata, new_metadata)
    
    # Update 4: Update S3 Storage folders to include download/
    old_s3_folders = '''- **Folders**: 
  - `raw/` - Uploaded PDFs (triggers Lambda)
  - `processed/` - Successfully processed PDFs'''
    
    new_s3_folders = '''- **Folders**: 
  - `raw/` - Uploaded PDFs (triggers Lambda)
  - `processed/` - Successfully processed PDFs
  - `download/` - Generated PDF exports (Future Scope)'''
    
    content = content.replace(old_s3_folders, new_s3_folders)
    
    # Update 5: Add category filtering to RAGOrchestratorFunction responsibilities
    old_rag_resp = '''**Responsibilities**:
1. Validate input (required fields, data types)
2. Generate query embedding using Bedrock Titan Embeddings
3. Call FAISS API (POST /search) for k-NN search (k=5)
4. Construct structured reasoning prompt with retrieved chunks
5. Call Bedrock Titan Text Express for LLM generation
6. Parse LLM response into structured JSON
7. Return schemes with eligibility, benefits, citations, confidence
8. Log query and response to CloudWatch'''
    
    new_rag_resp = '''**Responsibilities**:
1. Validate input (required fields, data types)
2. Generate query embedding using Bedrock Titan Embeddings
3. Call FAISS API (POST /search) for k-NN search (k=5)
4. Filter vector search results by category metadata
5. Include category context in LLM prompt
6. Construct structured reasoning prompt with retrieved chunks
7. Call Bedrock Titan Text Express for LLM generation
8. Parse LLM response into structured JSON
9. Return schemes with eligibility, benefits, citations, confidence
10. Log query and response to CloudWatch'''
    
    content = content.replace(old_rag_resp, new_rag_resp)
    
    # Update 6: Update Vector Store Usage to show category filtering
    old_vector_usage = '''**Vector Store Usage**:
```python
from vectorstore.factory import VectorStoreFactory

vector_store = VectorStoreFactory.get_store()  # Returns FaissVectorStore
results = vector_store.search(query_embedding, top_k=5)
```'''
    
    new_vector_usage = '''**Vector Store Usage**:
```python
from vectorstore.factory import VectorStoreFactory

vector_store = VectorStoreFactory.get_store()  # Returns FaissVectorStore
results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)
```'''
    
    content = content.replace(old_vector_usage, new_vector_usage)
    
    # Update 7: Update FAISS FastAPI Endpoints description
    old_faiss_endpoints = '''**FAISS FastAPI Endpoints**:
- `POST /add` - Add documents with embeddings
- `POST /search` - k-NN similarity search (k=5, cosine similarity)
- `POST /delete` - Delete index
- `GET /health` - Health check endpoint'''
    
    new_faiss_endpoints = '''**FAISS FastAPI Endpoints**:
- `POST /add` - Add documents with embeddings
- `POST /search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering
- `POST /delete` - Delete index
- `GET /health` - Health check endpoint'''
    
    content = content.replace(old_faiss_endpoints, new_faiss_endpoints)
    
    # Update 8: Add note about CloudWatch monitoring
    old_observability = '''#### 7. Observability Layer (CloudWatch)



**Note on CloudWatch Monitoring**: CloudWatch monitors backend services only (Lambda functions, API Gateway, EC2 FAISS service). Frontend errors and client-side issues are handled in the browser console and not logged to CloudWatch. User-facing error messages are displayed in the selected language on the frontend.'''
    
    new_observability = '''#### 7. Observability Layer (CloudWatch)

**Note on CloudWatch Monitoring**: CloudWatch monitors backend services only (Lambda functions, API Gateway, EC2 FAISS service). Frontend errors and client-side issues are handled in the browser console and not logged to CloudWatch. User-facing error messages are displayed in the selected language on the frontend.'''
    
    content = content.replace(old_observability, new_observability)
    
    # Update 9: Update Technology Stack Frontend entry
    old_tech_stack = '''### Technology Stack (Hybrid Serverless)

### Compute
- **Lambda Functions**: Python 3.11 runtime'''
    
    # Find the Frontend entry in Technology Stack
    content = content.replace(
        '- **Static Frontend**: S3 + CloudFront',
        '- **Static Frontend**: Static HTML/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront'
    )
    
    # Write the updated content back
    with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully updated design.md with all requested changes")
    print("\nUpdates made:")
    print("1. ✅ Updated category dropdown values to: Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme")
    print("2. ✅ Added category field to Request Format with note about required values")
    print("3. ✅ Added category field to FAISS metadata structure")
    print("4. ✅ Added download/ folder to S3 storage")
    print("5. ✅ Added category filtering responsibilities to RAGOrchestratorFunction")
    print("6. ✅ Updated Vector Store Usage example to show category filtering")
    print("7. ✅ Updated FAISS FastAPI Endpoints description to mention category filtering")
    print("8. ✅ Fixed CloudWatch monitoring note formatting")
    print("9. ✅ Updated Technology Stack Frontend entry")

if __name__ == '__main__':
    update_design_md()
