# Task 1.2: IAM Role Setup with Updated Model IDs

## Problem
The original IAM roles were created with outdated Bedrock model IDs:
- ❌ `amazon.titan-embed-text-v1` (not available in ap-south-1)
- ❌ `amazon.titan-text-express-v1` (not available in ap-south-1)

## Solution
Updated model IDs for ap-south-1 region:
- ✅ `amazon.titan-embed-text-v2:0` (embeddings, 1024 dimensions)
- ✅ `global.amazon.nova-2-lite-v1:0` (LLM - inference profile)

## Quick Start (Recommended)

### Option 1: Automated Script (Windows)
```cmd
cd scripts
setup_iam_roles.bat
```

### Option 2: Automated Script (Linux/Mac)
```bash
cd scripts
chmod +x setup_iam_roles.sh
./setup_iam_roles.sh
```

### Option 3: Manual Commands
Follow the detailed steps in `.kiro/specs/govt-scheme-rag/tasks.md` under Task 1.2.

## What Gets Created

### 1. SchemeIngestionLambdaRole
**Purpose**: Used by Lambda function that processes PDFs and generates embeddings

**Permissions**:
- CloudWatch Logs (via AWSLambdaBasicExecutionRole)
- S3 access to `aicloud-bharat-schemes/*` (GetObject, PutObject, DeleteObject)
- Bedrock InvokeModel for `amazon.titan-embed-text-v2:0`

### 2. RAGOrchestratorLambdaRole
**Purpose**: Used by Lambda function that handles user queries

**Permissions**:
- CloudWatch Logs (via AWSLambdaBasicExecutionRole)
- Bedrock InvokeModel for:
  - `amazon.titan-embed-text-v2:0` (query embeddings)
  - `global.amazon.nova-2-lite-v1:0` (LLM responses - inference profile)

## Verification

After running the setup script, verify roles exist:
```bash
aws iam list-roles --query 'Roles[?contains(RoleName, `Lambda`)].RoleName'
```

Expected output:
```json
[
    "RAGOrchestratorLambdaRole",
    "SchemeIngestionLambdaRole"
]
```

## Next Step: Test Bedrock

After IAM roles are created, test the Bedrock models:

```bash
# Install boto3 if not already installed
pip install boto3

# Run test
python scripts/test_bedrock.py
```

Expected output:
```
==========================================================
Testing Amazon Bedrock Models in ap-south-1
==========================================================

[TEST 1] Testing Titan Embeddings V2...
✅ Embedding generated successfully
   Dimension: 1024
   First 5 values: [0.123, -0.456, 0.789, ...]
   ✅ Dimension is 1024 (Titan V2 standard)

[TEST 2] Testing Nova 2 Lite LLM...
✅ LLM response generated successfully
   Response: A solar subsidy scheme is a government program...
   Response length: 87 characters

==========================================================
Bedrock testing complete!
==========================================================
```

## Important Notes

1. **Embedding Dimension Changed**: Titan V2 uses 1024 dimensions (V1 was 1536)
2. **API Format Changed**: Nova 2 Lite uses `messages` array format (different from Titan Text Express)
3. **Region Locked**: All resources must be in ap-south-1 (Mumbai)
4. **No Manual Model Enabling**: As of 2026, Bedrock model access is automatic

## Troubleshooting

### "NoSuchEntity" error when deleting roles
This is normal if roles don't exist yet. Script continues automatically.

### "AccessDeniedException" when testing Bedrock
- Verify IAM roles were created successfully
- Check AWS credentials: `aws sts get-caller-identity`
- Ensure region is ap-south-1: `aws configure get region`

### "Could not connect to endpoint"
- Check internet connectivity
- Verify region configuration
- Ensure AWS CLI is installed: `aws --version`

## Files Created

The setup script creates these temporary policy files (can be deleted after setup):
- `lambda-trust-policy.json`
- `ingestion-s3-policy.json`
- `ingestion-bedrock-policy.json`
- `orchestrator-bedrock-policy.json`

## After Completion

Once both IAM setup and Bedrock testing are successful:
1. Update task status in `tasks.md`:
   - Mark Task 1.2 as complete: `[x]`
   - Mark Task 1.4 as complete: `[x]`
2. Proceed to Stage 2: FAISS Vector Service on EC2
