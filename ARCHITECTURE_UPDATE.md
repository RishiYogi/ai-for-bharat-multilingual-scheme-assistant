# Architecture Update Summary

## Changes from Original to New Architecture

### Original Architecture
- EC2-based deployment with Streamlit UI
- Manual PDF processing scripts
- Monolithic application approach

### New Architecture (Lambda-Based)
- **Layer 1**: Admin Ingestion Pipeline (S3 + Lambda event-driven)
- **Layer 2**: RAG Orchestrator (API Gateway + Lambda)
- **Layer 3**: Observability (CloudWatch comprehensive monitoring)
- Serverless, event-driven, scalable

## Key Components

### S3 Bucket Structure
- Bucket name: `aicloud-bharat-schemes`
- Folders: `raw/` and `processed/`
- Event trigger: `s3:ObjectCreated:*` on `raw/`

### Lambda Functions
1. **SchemeIngestionFunction**: Triggered by S3 uploads, processes PDFs
2. **RAGOrchestratorFunction**: Handles user queries via API Gateway

### Frontend
- Static HTML + JavaScript
- Hosted on S3 + CloudFront (future)
- Single POST `/query` endpoint

### Models
- Embeddings: `amazon.titan-embed-text-v1`
- LLM: `amazon.titan-text-express-v1`

## Region
- All resources in: **ap-south-1 (Mumbai)**
