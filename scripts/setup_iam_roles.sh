#!/bin/bash

# Script to delete old IAM roles and create new ones with updated Bedrock model IDs
# For Multilingual Government Scheme Assistant
# Region: ap-south-1 (Mumbai)

echo "=========================================="
echo "IAM Role Setup for Bedrock Models"
echo "=========================================="

# Step 1: Delete old roles (if they exist) - MUST detach policies first
echo ""
echo "[STEP 1] Deleting old IAM roles..."
echo "Cleaning up SchemeIngestionLambdaRole..."
aws iam detach-role-policy --role-name SchemeIngestionLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name S3AccessPolicy 2>/dev/null
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name BedrockAccessPolicy 2>/dev/null
aws iam delete-role --role-name SchemeIngestionLambdaRole 2>/dev/null && echo "  ✅ Deleted SchemeIngestionLambdaRole" || echo "  ⚠️  SchemeIngestionLambdaRole not found (OK if first time)"

echo "Cleaning up RAGOrchestratorLambdaRole..."
aws iam detach-role-policy --role-name RAGOrchestratorLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null
aws iam delete-role-policy --role-name RAGOrchestratorLambdaRole --policy-name BedrockAccessPolicy 2>/dev/null
aws iam delete-role --role-name RAGOrchestratorLambdaRole 2>/dev/null && echo "  ✅ Deleted RAGOrchestratorLambdaRole" || echo "  ⚠️  RAGOrchestratorLambdaRole not found (OK if first time)"

# Step 2: Create trust policy file
echo ""
echo "[STEP 2] Creating trust policy file..."
cat > lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
echo "✅ Created lambda-trust-policy.json"

# Step 3: Create SchemeIngestionLambdaRole
echo ""
echo "[STEP 3] Creating SchemeIngestionLambdaRole..."
aws iam create-role \
  --role-name SchemeIngestionLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy \
  --role-name SchemeIngestionLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create S3 policy
cat > ingestion-s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::aicloud-bharat-schemes/*"
    }
  ]
}
EOF

# Create Bedrock policy for Titan Embeddings V2
cat > ingestion-bedrock-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name SchemeIngestionLambdaRole \
  --policy-name S3AccessPolicy \
  --policy-document file://ingestion-s3-policy.json

aws iam put-role-policy \
  --role-name SchemeIngestionLambdaRole \
  --policy-name BedrockAccessPolicy \
  --policy-document file://ingestion-bedrock-policy.json

echo "✅ Created SchemeIngestionLambdaRole with policies"

# Step 4: Create RAGOrchestratorLambdaRole
echo ""
echo "[STEP 4] Creating RAGOrchestratorLambdaRole..."
aws iam create-role \
  --role-name RAGOrchestratorLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy \
  --role-name RAGOrchestratorLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create Bedrock policy for both models
cat > orchestrator-bedrock-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": [
        "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0",
        "arn:aws:bedrock:ap-south-1::foundation-model/global.amazon.nova-2-lite-v1:0"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name RAGOrchestratorLambdaRole \
  --policy-name BedrockAccessPolicy \
  --policy-document file://orchestrator-bedrock-policy.json

echo "✅ Created RAGOrchestratorLambdaRole with policies"

# Step 5: Verify roles created
echo ""
echo "[STEP 5] Verifying roles..."
aws iam list-roles --query 'Roles[?contains(RoleName, `Lambda`)].RoleName'

echo ""
echo "=========================================="
echo "IAM Role Setup Complete!"
echo "=========================================="
echo ""
echo "Next step: Run 'python scripts/test_bedrock.py' to test Bedrock models"
