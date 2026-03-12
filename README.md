# Multilingual Government Scheme Assistant - Specification

## Overview

This directory contains the complete specification for a hybrid serverless RAG-based system that helps rural Indian citizens discover government welfare schemes. The system uses AWS Lambda, Amazon Bedrock (Titan models), and FAISS vector database to provide cost-effective, multilingual scheme discovery.

## Document Structure

### 📋 Core Specification Documents

1. **[requirements.md](requirements.md)** - Functional requirements
   - 14 detailed requirements with acceptance criteria
   - Prototype vs production scope clearly defined
   - User stories for each requirement
   - Deferred features marked (voice, offline)

2. **[design.md](design.md)** - Technical architecture
   - 4-layer hybrid serverless architecture
   - Pluggable VectorStore interface pattern
   - Component diagrams and data flows
   - IAM roles and security policies
   - 28 correctness properties for testing

3. **[tasks.md](tasks.md)** - Implementation plan
   - 6 stages with 29 tasks
   - Step-by-step instructions (manual + automated)
   - Estimated time: 16-24 hours
   - Cost: $5-10/month (free tier optimized)

### 📚 Supporting Documents

4. **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Quick reference
   - Architecture summary
   - Technology decisions explained
   - Cost breakdown
   - Troubleshooting guide

5. **[FINAL_ARCHITECTURE_SUMMARY.md](FINAL_ARCHITECTURE_SUMMARY.md)** - Executive summary
   - Key decisions and rationale
   - Infrastructure diagrams
   - VectorStore pattern code examples
   - Migration path to production

6. **[AWS_CONFIGS.md](AWS_CONFIGS.md)** - Configuration reference
   - IAM policies (copy-paste ready)
   - OpenSearch index mappings
   - Lambda environment variables
   - Security group rules
   - Sample code snippets

7. **[ARCHITECTURE_UPDATE.md](ARCHITECTURE_UPDATE.md)** - Change log
   - Original vs new architecture comparison
   - Key changes documented

## Architecture at a Glance

```
User → CloudFront → API Gateway → Lambda (RAG) → FAISS (EC2) + Bedrock
                                                      ↓
Admin → S3 (raw/) → Lambda (Ingestion) → FAISS (EC2) + Bedrock
```

### Key Components

- **Frontend**: Static HTML/JS on S3 + CloudFront (permanent demo link)
- **API**: API Gateway HTTP API + Lambda (RAG orchestrator)
- **Vector DB**: FAISS on EC2 t3.micro (pluggable, can migrate to OpenSearch)
- **Embeddings**: Amazon Bedrock Titan Embeddings G1 (1536 dims)
- **LLM**: Amazon Bedrock Titan Text Express
- **Storage**: S3 (PDFs) + EBS (FAISS index)
- **Monitoring**: CloudWatch Logs, Metrics, Alarms

## Quick Start

### Prerequisites

1. AWS account with free tier available
2. AWS CLI v2 installed and configured
3. Region set to ap-south-1 (Mumbai)
4. Python 3.11 installed locally

### Implementation Steps

1. **Read the Spec** (1-2 hours)
   - Start with [FINAL_ARCHITECTURE_SUMMARY.md](FINAL_ARCHITECTURE_SUMMARY.md)
   - Review [requirements.md](requirements.md) for functional scope
   - Skim [design.md](design.md) for technical details

2. **Follow the Tasks** (16-24 hours)
   - Open [tasks.md](tasks.md)
   - Execute Stage 1: AWS Infrastructure Setup
   - Execute Stage 2: FAISS Service on EC2
   - Execute Stage 3: Ingestion Pipeline
   - Execute Stage 4: RAG Orchestrator
   - Execute Stage 5: Frontend
   - Execute Stage 6: Observability

3. **Test and Deploy**
   - Upload 5-10 sample scheme PDFs to S3
   - Test end-to-end via CloudFront URL
   - Share CloudFront URL as permanent demo link

### Cost Estimate

**Prototype (Free Tier - First 12 Months)**:
```
EC2 t3.micro:    $0 (750 hours free)
Lambda:          $0 (1M requests free)
API Gateway:     $0 (1M requests free)
S3:              $0 (5 GB free)
CloudFront:      $0 (1 TB transfer free)
Bedrock:         $5-10 (pay per use)
CloudWatch:      $1-2
-----------------------------------
Total:           $6-12/month ✅
```

**After Free Tier**: $15-25/month

## Key Design Decisions

### 1. Why FAISS instead of OpenSearch?

**Cost**: $0 vs $350-700/month
- FAISS on EC2 t3.micro is free tier eligible
- OpenSearch requires 24/7 cluster ($350+/month)
- Perfect for prototype evaluation

**Migration Path**: Easy upgrade to OpenSearch
- Pluggable VectorStore interface
- Change environment variable only
- No Lambda code changes required

### 2. Why Hybrid Serverless?

**Lambda for Compute**: Auto-scaling, pay-per-use
**EC2 for FAISS**: Persistent storage, 24/7 availability
**S3 + CloudFront**: Static frontend, global CDN

### 3. Why No VPC?

**Cost**: Avoid NAT Gateway ($32/month)
**Simplicity**: Faster cold starts, easier setup
**Security**: API key auth + Security Groups

### 4. Why Static Frontend?

**Simplicity**: Single HTML page, vanilla JS
**Stability**: No server-side rendering, no frameworks
**Cost**: $0 with free tier
**Permanent Link**: CloudFront URL for judges

## Prototype Scope

### ✅ Included

- Core RAG pipeline (PDF → Embeddings → FAISS → LLM)
- Multilingual support (10 Indian languages)
- Text-based web interface
- CloudFront permanent demo link
- Cost-optimized for free tier

### ❌ Deferred to Future

- Voice input/output (Transcribe + Polly)
- Offline capability (PWA + service workers)
- Automated web scraping
- User authentication
- Analytics dashboard

## Migration to Production

When ready to scale:

1. **Deploy OpenSearch Service** (3-node cluster)
2. **Implement OpenSearchVectorStore** (same interface)
3. **Change environment variable**: `VECTOR_DB_TYPE=opensearch`
4. **No Lambda code changes** (pluggable architecture)
5. **Add caching** (ElastiCache for frequent queries)
6. **Add voice** (Transcribe + Polly integration)
7. **Add offline** (PWA implementation)

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | HTML/JS + CloudFront | Simple, fast, cheap |
| API | API Gateway + Lambda | Serverless, auto-scaling |
| Vector DB | FAISS on EC2 | Free tier, pluggable |
| Embeddings | Bedrock Titan Embeddings | 1536 dims, multilingual |
| LLM | Bedrock Titan Text Express | Fast, cost-effective |
| Storage | S3 + EBS | Durable, scalable |
| Monitoring | CloudWatch | Integrated, comprehensive |

## Success Criteria

### Functional

- ✅ Accurate scheme retrieval (relevant results)
- ✅ Multilingual explanations (3 languages: English, Hindi, Tamil)
- ✅ Fast response times (<3 seconds)
- ✅ Source citations (transparency)

### Technical

- ✅ Stable permanent demo link (CloudFront)
- ✅ Clean, maintainable code
- ✅ Proper error handling
- ✅ CloudWatch monitoring

### Cost

- ✅ Under $20/month budget
- ✅ Free tier optimized
- ✅ No surprise charges

## Support

### Questions?

- Check [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for troubleshooting
- Review [AWS_CONFIGS.md](AWS_CONFIGS.md) for configuration details
- Read [design.md](design.md) for architecture deep dive

### Issues?

- Check CloudWatch Logs for errors
- Verify IAM roles and permissions
- Test components individually
- Review Security Group rules

## Next Steps

1. ✅ **Specs are finalized** - All documents updated
2. 🔧 **Configure AWS CLI** - Set region to ap-south-1
3. 🚀 **Start Stage 1** - Follow tasks.md sequentially
4. 🧪 **Test thoroughly** - Validate each stage
5. 🎯 **Deploy and share** - CloudFront URL is permanent link

## License

This specification is provided for educational and evaluation purposes.

## Contributors

- Architecture: Hybrid serverless with pluggable vector database
- Cost Optimization: Free tier maximization
- Evaluation Focus: Stable, reliable prototype

---

**Ready to implement!** Start with [tasks.md](tasks.md) Stage 1. 🚀
