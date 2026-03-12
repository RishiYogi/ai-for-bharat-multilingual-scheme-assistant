# Design Document Updates Summary

## Key Implementation Changes (Completed as of March 2026)

### 1. Implementation Status
- **STAGE 1-6**: ✅ Completed
- **STAGE 7**: ⏳ Future Scope (PDF Export)
- **STAGE 8**: ✅ Completed (Gatekeeper integrated in RAG Orchestrator)
- **STAGE 9**: ⏳ Pending (Testing)

### 2. Vector Database
- **Implemented**: ChromaDB on EC2 (not FAISS)
- **Collection**: `govt_schemes`
- **Embedding Dimension**: 1024 (Titan Embeddings V2)
- **Distance Metric**: Cosine similarity
- **Persistence**: `/chroma_data` directory on EBS

### 3. User Input Fields (Updated)
- **Removed**: Income Range field
- **Added**: 
  - Community (required): General / OBC / PVTG / SC / ST / DNT
  - Physically Challenged (required): Yes / No

### 4. API Request/Response Format

**Request**:
```json
{
  "name": "string",
  "age": 25,
  "state": "tamil_nadu",
  "gender": "male",
  "community": "general",
  "physically_challenged": "no",
  "category": "agriculture",
  "language": "en",
  "query": "What farmer schemes are available?"
}
```

**Response**:
```json
{
  "response": "Markdown-formatted recommendations",
  "sources": ["scheme_name (Score: 0.85)"],
  "query_id": "uuid"
}
```

### 5. LLM Model
- **Model**: global.amazon.nova-2-lite-v1:0 (Nova 2 Lite)
- **API**: Bedrock Converse API (not InvokeModel)
- **Inference Profile**: us.amazon.nova-lite-v1:0

### 6. Metadata Structure
```json
{
  "scheme_name": "PM Surya Ghar Solar Subsidy",
  "category": "solar_subsidy",
  "state": "all",
  "eligible_gender": "any",
  "eligible_minage": 18,
  "eligible_maxage": 120,
  "eligible_community": "any",
  "eligible_physically_challenged": "any",
  "chunk_text": "...",
  "chunk_index": 0
}
```

### 7. RAG Orchestrator Features
- **Pure Vector Search**: No metadata filtering in ChromaDB query
- **Post-Retrieval Filtering**: Python-based metadata filtering after retrieval
- **Gatekeeper**: Integrated similarity threshold check (score < 0.3 returns "No relevant schemes")
- **Fallback Logic**: Returns top vector results if no filtered matches
- **CORS**: Full CORS support with OPTIONS handler
- **Query ID**: UUID tracking for all requests
- **Debug Logging**: Comprehensive CloudWatch logging

### 8. Frontend Updates
- **Markdown Rendering**: Converts markdown to HTML (###, **, *)
- **Custom Alert Dialog**: "AICloud for Bharat" title instead of domain
- **API Endpoint**: https://wgwpbn481c.execute-api.ap-south-1.amazonaws.com/query
- **CloudFront**: https://d1gkjmmqj8v9b8.cloudfront.net

### 9. Observability (STAGE 6)
- **Task 27**: View Lambda Logs in CloudWatch
- **Task 28**: CloudWatch Logs Insights queries
- **Task 29**: Monitor Lambda Metrics (invocations, errors, duration, throttles)

### 10. Chunking Strategy
- **Method**: Token-based splitting
- **Chunk Size**: 700 tokens
- **Overlap**: 120 tokens
- **Preserve**: Sentence boundaries

### 11. Eligibility Filtering
- **Fields**: age, gender, community, physically_challenged, category, state
- **Logic**: Post-retrieval filtering in Python
- **Fallback**: Returns top vector results if no matches

### 12. Cost Optimization
- **EC2**: t3.micro (free tier)
- **Lambda**: Free tier (1M requests)
- **API Gateway**: Free tier (1M requests)
- **S3**: Free tier (5 GB)
- **CloudFront**: Free tier (1 TB transfer)
- **Estimated Cost**: $5-10/month (Bedrock only)

## Files to Update in design.md

1. **Line 40-70**: Update implementation stages status
2. **Line 100-150**: Update architecture diagram (ChromaDB, not FAISS)
3. **Line 200-250**: Update user input fields (remove income, add community/physically_challenged)
4. **Line 300-350**: Update API request/response format
5. **Line 400-450**: Update vector database section (ChromaDB details)
6. **Line 500-550**: Update RAG Orchestrator responsibilities
7. **Line 600-650**: Update metadata structure
8. **Line 700-750**: Update LLM model (Nova 2 Lite, Converse API)
9. **Line 800-850**: Update observability section (STAGE 6 completed)
10. **Line 900-950**: Update gatekeeper section (integrated, not separate stage)

## Next Steps
1. Apply these changes to design.md
2. Update requirements.md to reflect completed implementation
3. Mark completed requirements as ✅
4. Update any requirement text that changed during implementation
