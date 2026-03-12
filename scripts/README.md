# Setup Scripts for Government Scheme RAG System

## Overview
This directory contains scripts to set up IAM roles and test Bedrock models with the correct model IDs for ap-south-1 region.

## Model IDs (Updated for 2026)
- **Embeddings**: `amazon.titan-embed-text-v2:0` (1024 dimensions)
- **LLM**: `global.amazon.nova-2-lite-v1:0` (inference profile)

## Files

### 1. `setup_iam_roles.bat` (Windows)
Automated script to delete old IAM roles and create new ones with correct Bedrock permissions.

**Usage:**
```cmd
cd scripts
setup_iam_roles.bat
```

### 2. `setup_iam_roles.sh` (Linux/Mac)
Same as above but for Unix-based systems.

**Usage:**
```bash
cd scripts
chmod +x setup_iam_roles.sh
./setup_iam_roles.sh
```

### 3. `test_bedrock.py`
Python script to test both Bedrock models (embeddings and LLM).

**Prerequisites:**
```bash
pip install boto3
```

**Usage:**
```bash
python scripts/test_bedrock.py
```

**Expected Output:**
- ✅ Embedding dimension: 1024
- ✅ LLM response: Valid text about solar subsidies
- Both tests complete in <2 seconds

## Manual Steps (Alternative to Automated Scripts)

If you prefer to run commands manually, follow the steps in `tasks.md` under Task 1.2.

## What the Scripts Do

### IAM Role Setup Script:
1. Deletes old IAM roles (if they exist)
2. Creates trust policy for Lambda
3. Creates `SchemeIngestionLambdaRole` with:
   - S3 access to `aicloud-bharat-schemes` bucket
   - Bedrock access to Titan Embeddings V2
4. Creates `RAGOrchestratorLambdaRole` with:
   - Bedrock access to Titan Embeddings V2 and Nova 2 Lite

### Bedrock Test Script:
1. Tests Titan Embeddings V2 with sample text
2. Tests Nova 2 Lite LLM with sample prompt
3. Validates response format and dimensions

## Troubleshooting

### Error: "An error occurred (NoSuchEntity) when calling the DeleteRole operation"
This is normal if roles don't exist yet. The script will continue.

### Error: "An error occurred (AccessDeniedException) when calling the InvokeModel operation"
- Check that IAM roles have correct Bedrock permissions
- Verify model IDs are correct for ap-south-1 region
- Ensure AWS credentials are configured: `aws configure`

### Error: "Could not connect to the endpoint URL"
- Verify region is set to ap-south-1: `aws configure get region`
- Check internet connectivity

## Next Steps

After successful IAM setup and Bedrock testing:
1. Mark Task 1.2 as complete in `tasks.md`
2. Mark Task 1.4 as complete in `tasks.md`
3. Proceed to Stage 2: FAISS Vector Service on EC2
