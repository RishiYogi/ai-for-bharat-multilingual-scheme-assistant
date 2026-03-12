# Implementation Guide: Multilingual Government Scheme Assistant

## Quick Start

This guide helps you implement the hybrid serverless RAG-based government scheme assistant using AWS Lambda, Bedrock, and FAISS on EC2.

## Architecture Summary

### 4-Layer Hybrid Serverless Architecture

**Layer 1: Vector Database (FAISS on EC2)**
- EC2 t3.micro runs FastAPI serving FAISS
- Persistent storage on 8 GB EBS volume
- Public API with key authentication
- Pluggable design (can migrate to OpenSearch later)

**Layer 2: Admin Ingestion Pipeline**
- Admin uploads PDF → S3 `raw/` folder
- S3 event triggers `SchemeIngestionFunction` Lambda
- Lambda: Extract text → Chunk → Generate embeddings → Store in FAISS
- Move PDF to `processed/` folder

**Layer 3: RAG Orchestrator**
- User submits query via static frontend (HTML/JS)
- API Gateway receives POST /query
- `RAGOrchestratorFunction` Lambda:
  - Generate query embedding
  - Call FAISS API for k-NN search (k=5)
  - Construct prompt with chunks
  - Call Bedrock LLM for response
  - Return structured JSON with schemes

**Layer 4: Observability**
- CloudWatch monitors Lambda, EC2, API Gateway, Bedrock
- Alarms for errors, latency, cost
- Dashboards for real-time metrics

## Technology Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Compute | AWS Lambda (Python 3.11) + EC2 t3.micro | Serverless + persistent FAISS service |
| Vector DB | FAISS on EC2 | Free tier eligible, pluggable architecture |
| Embeddings | Bedrock Titan Embeddings G1 | 1536 dims, multilingual, managed |
| LLM | Bedrock Titan Text Express | Fast, cost-effective, multilingual |
| Frontend | Static HTML/JS on S3 + CloudFront | Simple, fast, cheap |
| API | API Gateway HTTP API | Simpler and cheaper than REST API |
| VPC | Non-VPC Lambda | Faster cold starts, lower cost |
| Region | ap-south-1 (Mumbai) | Low latency for Indian users |

## Implementation Stages

### Stage 1: AWS Infrastructure Setup (1-2 hours)
- Create S3 bucket with `raw/` and `processed/` folders
- Create IAM roles for Lambda functions
- Enable Bedrock model access
- Test Bedrock API calls

### Stage 2: FAISS Vector Service on EC2 (3-4 hours)
- Launch EC2 t3.micro instance
- Install Python, FastAPI, FAISS
- Implement VectorStore interface + FAISS backend
- Deploy FastAPI service with systemd
- Test /add, /search, /health endpoints

### Stage 3: Ingestion Pipeline (4-6 hours)
- Implement VectorStore client library (pluggable)
- Write SchemeIngestionFunction Lambda code
- Deploy Lambda with dependencies
- Configure S3 event trigger
- Test end-to-end: Upload PDF → Verify in FAISS

### Stage 4: RAG Orchestrator (4-6 hours)
- Write RAGOrchestratorFunction Lambda code
- Deploy Lambda
- Create API Gateway HTTP API
- Implement prompt engineering
- Test API with curl/Postman

### Stage 5: Frontend (2-3 hours)
- Create HTML form with required fields
- Write JavaScript to call API Gateway
- Upload to S3
- Create CloudFront distribution (PERMANENT LINK)
- Test end-to-end in browser

### Stage 6: Observability (2-3 hours)
- Configure CloudWatch Logs (30-day retention)
- Create alarms for errors, latency, cost
- Create monitoring dashboard
- Set up AWS Budgets
- Implement structured logging

**Total Estimated Time**: 16-24 hours

## Key Configuration Values

```
Region: ap-south-1
S3 Bucket: aicloud-bharat-schemes
EC2 Instance: t3.micro (FAISS service)
EC2 Public IP: <noted during setup>
FAISS API Port: 8000
Embedding Model: amazon.titan-embed-text-v1
LLM Model: amazon.titan-text-express-v1
Embedding Dimension: 1536
Lambda Runtime: Python 3.11
Lambda Architecture: arm64 (Graviton2)
```

## Cost Estimates (Monthly - Free Tier Optimized)

| Service | Usage | Cost (USD) |
|---------|-------|------------|
| EC2 t3.micro (24/7) | 750 hours (free tier) | $0 |
| EBS 8 GB | Free tier (30 GB available) | $0 |
| Lambda (both functions) | Free tier (1M requests) | $0 |
| API Gateway | Free tier (1M requests) | $0 |
| Bedrock Embeddings | 100K tokens | $1-2 |
| Bedrock LLM | 500K tokens | $3-5 |
| S3 | Free tier (5 GB) | $0 |
| CloudFront | Free tier (1 TB transfer) | $0 |
| CloudWatch Logs | 5 GB ingestion | $1-2 |
| **Total** | | **$5-10/month** |

**After Free Tier Expires (12 months)**:
- EC2 t3.micro: $7.50/month
- EBS 8 GB: $0.80/month
- Total: $13-20/month

## Security Checklist

- [ ] All resources in ap-south-1 region
- [ ] S3 bucket has Block Public Access enabled
- [ ] EC2 Security Group restricts port 8000 access
- [ ] FAISS API uses API key authentication
- [ ] Lambda functions use least-privilege IAM roles
- [ ] API Gateway uses HTTPS only
- [ ] CloudFront uses HTTPS only
- [ ] No PII collected (no Aadhaar, bank details, DOB)
- [ ] CloudWatch Logs enabled for audit trail

## Performance Targets

| Metric | Target | Monitoring |
|--------|--------|------------|
| Query Latency (p95) | < 3 seconds | CloudWatch Alarm |
| FAISS Search (p95) | < 200 ms | EC2 Metrics |
| LLM Generation (p95) | < 2 seconds | Bedrock Metrics |
| Lambda Cold Start | < 2 seconds | Lambda Insights |
| API Gateway 5XX | < 2% | CloudWatch Alarm |
| Lambda Errors | < 5% | CloudWatch Alarm |

## Troubleshooting

### Lambda Timeout
- **Symptom**: Lambda times out after 30 seconds
- **Solution**: Increase timeout to 60 seconds, optimize FAISS API call, reduce LLM max_tokens

### FAISS API Connection Refused
- **Symptom**: Lambda cannot connect to FAISS API
- **Solution**: Verify EC2 Security Group allows port 8000, check EC2 is running, verify API key

### Bedrock Throttling
- **Symptom**: Bedrock returns 429 Too Many Requests
- **Solution**: Implement exponential backoff, request quota increase from AWS

### High Costs
- **Symptom**: AWS bill higher than expected
- **Solution**: Check Lambda concurrency limits, verify CloudWatch log retention, stop EC2 if not needed

### Low Retrieval Quality
- **Symptom**: Irrelevant schemes returned
- **Solution**: Improve chunking strategy, add more schemes, tune k-NN parameters

## Next Steps After Implementation

1. **Add More Schemes**: Upload PDFs to S3 `raw/` folder
2. **Improve Prompts**: Iterate on prompt engineering for better responses
3. **Migrate to OpenSearch**: Change VECTOR_DB_TYPE to "opensearch", implement OpenSearchVectorStore
4. **Add Analytics**: Track query patterns, popular schemes
5. **Add Feedback**: Allow users to rate scheme recommendations
6. **Add Voice**: Integrate Amazon Transcribe and Polly
7. **Add Multilingual UI**: Translate frontend to regional languages

## Permanent Demo Link

**CloudFront URL**: `https://...cloudfront.net` (generated in Stage 5)

This is the permanent link for judges to evaluate the prototype. It will remain active as long as:
- EC2 instance is running
- Lambda functions are deployed
- S3 + CloudFront are configured

## Support

For questions or issues:
- Check CloudWatch Logs for error details
- Review AWS documentation for each service
- Test components individually before integration
- Use AWS Support (if you have a support plan)

## References

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
