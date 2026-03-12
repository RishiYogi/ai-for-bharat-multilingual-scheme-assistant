# Final Architecture Summary

## ✅ Architecture Finalized: FAISS on EC2 + Lambda

### Key Decisions

1. **Vector Database**: FAISS on EC2 t3.micro (NOT OpenSearch)
   - Reason: Free tier eligible, cost-effective for prototype
   - Cost: $0/month (free tier) vs $350-700/month (OpenSearch)

2. **Pluggable Design**: VectorStore interface pattern
   - Default: FaissVectorStore (HTTP client to EC2 API)
   - Future: OpenSearchVectorStore (easy migration)
   - Lambda code never directly references FAISS or OpenSearch

3. **Deployment**: Hybrid Serverless
   - Lambda for compute (ingestion + RAG orchestration)
   - EC2 for persistent FAISS service (24/7)
   - S3 + CloudFront for static frontend

4. **Security**: Public EC2 with API key authentication
   - No VPC, no NAT Gateway (cost optimization)
   - Security Group restricts access
   - API key at application level

5. **Permanent Link**: CloudFront URL
   - No custom domain (keep it simple)
   - CloudFront URL is the demo link for judges

6. **Budget**: $5-10/month (free tier optimized)
   - EC2 t3.micro: $0 (free tier)
   - EBS 8 GB: $0 (free tier)
   - Lambda: $0 (free tier)
   - Bedrock: $5-10 (pay per use)

## Infrastructure Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Judge/Evaluator)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              CloudFront (PERMANENT DEMO LINK)                │
│                  https://...cloudfront.net                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  S3: Static Frontend                         │
│              (index.html, app.js, styles.css)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              API Gateway: POST /query                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: RAGOrchestratorFunction                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  VectorStoreFactory.get_store()                      │   │
│  │  └─> FaissVectorStore (HTTP client)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│  EC2: FAISS Service  │      │   Bedrock: Titan Models      │
│  ┌────────────────┐  │      │  - Titan Embeddings G1       │
│  │ FastAPI        │  │      │  - Titan Text Express        │
│  │ POST /add      │  │      └──────────────────────────────┘
│  │ POST /search   │  │
│  │ GET /health    │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ EBS 8 GB       │  │
│  │ /data/         │  │
│  │ faiss_index.bin│  │
│  │ metadata.json  │  │
│  └────────────────┘  │
└──────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Admin Uploads PDF                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              S3: aicloud-bharat-schemes                      │
│              raw/ → processed/                               │
└────────────────────────┬────────────────────────────────────┘
                         │ (S3 Event Trigger)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: SchemeIngestionFunction                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  VectorStoreFactory.get_store()                      │   │
│  │  └─> FaissVectorStore (HTTP client)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│  EC2: FAISS Service  │      │   Bedrock: Titan Embeddings  │
│  POST /add           │      └──────────────────────────────┘
└──────────────────────┘
```

## VectorStore Interface Pattern

```python
# Abstract base class
class VectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents, embeddings, metadata) -> dict
    
    @abstractmethod
    def search(self, query_embedding, top_k=5) -> List[dict]
    
    @abstractmethod
    def delete_index() -> dict
    
    @abstractmethod
    def health_check() -> dict

# Implementations
class FaissVectorStore(VectorStore):
    """HTTP client to EC2 FAISS API (default for prototype)"""
    
class OpenSearchVectorStore(VectorStore):
    """boto3 OpenSearch client (future for production)"""

# Factory
class VectorStoreFactory:
    @staticmethod
    def get_store() -> VectorStore:
        db_type = os.getenv("VECTOR_DB_TYPE", "faiss")
        if db_type == "faiss":
            return FaissVectorStore()
        elif db_type == "opensearch":
            return OpenSearchVectorStore()

# Lambda usage (never directly references FAISS or OpenSearch)
vector_store = VectorStoreFactory.get_store()
vector_store.add_documents(chunks, embeddings, metadata)
results = vector_store.search(query_embedding, top_k=5)
```

## Cost Breakdown (Monthly)

### Prototype Phase (Free Tier - First 12 Months)
```
EC2 t3.micro (750 hours):       $0
EBS 8 GB (30 GB free):          $0
Lambda (1M requests):           $0
API Gateway (1M requests):      $0
S3 (5 GB storage):              $0
CloudFront (1 TB transfer):     $0
Bedrock Embeddings:             $1-2
Bedrock LLM:                    $3-5
CloudWatch Logs:                $1-2
-----------------------------------
Total:                          $5-10/month ✅
```

### After Free Tier (Month 13+)
```
EC2 t3.micro (730 hours):       $7.50
EBS 8 GB:                       $0.80
Lambda:                         $0-5
API Gateway:                    $0-1
S3:                             $0-1
CloudFront:                     $0-1
Bedrock:                        $5-10
CloudWatch:                     $1-2
-----------------------------------
Total:                          $15-25/month
```

## Migration Path to Production

When ready to scale (after evaluation):

1. **Deploy OpenSearch Service**:
   - Create 3-node cluster (t3.small or r6g.large)
   - Configure k-NN index
   - Set up IAM access policies

2. **Implement OpenSearchVectorStore**:
   - Same interface as FaissVectorStore
   - Use boto3 OpenSearch client
   - Handle authentication with AWS4Auth

3. **Update Environment Variable**:
   - Change `VECTOR_DB_TYPE` from "faiss" to "opensearch"
   - Update `OPENSEARCH_ENDPOINT` in Lambda env vars

4. **No Lambda Code Changes Required**:
   - VectorStoreFactory automatically returns OpenSearchVectorStore
   - All Lambda code continues to work unchanged

5. **Migrate Data** (optional):
   - Export FAISS index metadata
   - Re-index documents into OpenSearch
   - Or keep both running during transition

## Files Updated

✅ **design.md**: Complete architecture with FAISS + pluggable pattern
✅ **tasks.md**: 6 stages with FAISS EC2 setup, Lambda deployment, frontend
✅ **IMPLEMENTATION_GUIDE.md**: Updated with FAISS architecture and costs
✅ **FINAL_ARCHITECTURE_SUMMARY.md**: This file

## Next Steps

1. **Review Updated Documents**:
   - Read design.md for complete architecture
   - Read tasks.md for step-by-step implementation
   - Read IMPLEMENTATION_GUIDE.md for quick reference

2. **Configure AWS CLI**:
   - Install AWS CLI v2
   - Run `aws configure`
   - Set region to ap-south-1

3. **Start Implementation**:
   - Begin with Stage 1 (AWS Infrastructure Setup)
   - Follow tasks.md sequentially
   - Test each stage before moving to next

4. **Save Permanent Link**:
   - CloudFront URL from Stage 5 is the demo link
   - Share with judges for evaluation

## Questions Answered

✅ **Why FAISS instead of OpenSearch?**
- Cost: $0 vs $350-700/month
- Free tier eligible for prototype
- Easy migration path to OpenSearch later

✅ **Why EC2 instead of Lambda for FAISS?**
- FAISS needs persistent storage
- Lambda has ephemeral storage
- EC2 provides EBS for persistence

✅ **Why pluggable architecture?**
- Easy migration to OpenSearch in production
- No Lambda code changes required
- Just change environment variable

✅ **Why non-VPC Lambda?**
- Avoid NAT Gateway costs ($32/month)
- Faster cold starts
- Simpler architecture

✅ **What's the permanent link?**
- CloudFront URL (generated in Stage 5)
- Remains active as long as resources are running
- No custom domain needed

## Ready to Implement!

All specs are finalized. You can now:
1. Configure AWS CLI
2. Start with Stage 1 in tasks.md
3. Execute each task sequentially
4. Test thoroughly at each stage

**Estimated Total Time**: 16-24 hours
**Estimated Cost**: $5-10/month (free tier optimized)
**Permanent Demo Link**: CloudFront URL (Stage 5)

Good luck with the implementation! 🚀
