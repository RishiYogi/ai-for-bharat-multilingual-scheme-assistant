@echo off
REM Script to delete old IAM roles and create new ones with updated Bedrock model IDs
REM For Multilingual Government Scheme Assistant
REM Region: ap-south-1 (Mumbai)

echo ==========================================
echo IAM Role Setup for Bedrock Models
echo ==========================================

REM Step 1: Delete old roles (if they exist) - MUST detach policies first
echo.
echo [STEP 1] Deleting old IAM roles...
echo Cleaning up SchemeIngestionLambdaRole...
aws iam detach-role-policy --role-name SchemeIngestionLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>nul
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name S3AccessPolicy 2>nul
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name BedrockAccessPolicy 2>nul
aws iam delete-role --role-name SchemeIngestionLambdaRole 2>nul && echo   Done: Deleted SchemeIngestionLambdaRole || echo   Note: SchemeIngestionLambdaRole not found (OK if first time)

echo Cleaning up RAGOrchestratorLambdaRole...
aws iam detach-role-policy --role-name RAGOrchestratorLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>nul
aws iam delete-role-policy --role-name RAGOrchestratorLambdaRole --policy-name BedrockAccessPolicy 2>nul
aws iam delete-role --role-name RAGOrchestratorLambdaRole 2>nul && echo   Done: Deleted RAGOrchestratorLambdaRole || echo   Note: RAGOrchestratorLambdaRole not found (OK if first time)

REM Step 2: Create trust policy file
echo.
echo [STEP 2] Creating trust policy file...
(
echo {
echo   "Version": "2012-10-17",
echo   "Statement": [
echo     {
echo       "Effect": "Allow",
echo       "Principal": {
echo         "Service": "lambda.amazonaws.com"
echo       },
echo       "Action": "sts:AssumeRole"
echo     }
echo   ]
echo }
) > lambda-trust-policy.json
echo Done: Created lambda-trust-policy.json

REM Step 3: Create SchemeIngestionLambdaRole
echo.
echo [STEP 3] Creating SchemeIngestionLambdaRole...
aws iam create-role --role-name SchemeIngestionLambdaRole --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy --role-name SchemeIngestionLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

REM Create S3 policy
(
echo {
echo   "Version": "2012-10-17",
echo   "Statement": [
echo     {
echo       "Effect": "Allow",
echo       "Action": [
echo         "s3:GetObject",
echo         "s3:PutObject",
echo         "s3:DeleteObject"
echo       ],
echo       "Resource": "arn:aws:s3:::aicloud-bharat-schemes/*"
echo     }
echo   ]
echo }
) > ingestion-s3-policy.json

REM Create Bedrock policy for Titan Embeddings V2
(
echo {
echo   "Version": "2012-10-17",
echo   "Statement": [
echo     {
echo       "Effect": "Allow",
echo       "Action": "bedrock:InvokeModel",
echo       "Resource": "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0"
echo     }
echo   ]
echo }
) > ingestion-bedrock-policy.json

aws iam put-role-policy --role-name SchemeIngestionLambdaRole --policy-name S3AccessPolicy --policy-document file://ingestion-s3-policy.json

aws iam put-role-policy --role-name SchemeIngestionLambdaRole --policy-name BedrockAccessPolicy --policy-document file://ingestion-bedrock-policy.json

echo Done: Created SchemeIngestionLambdaRole with policies

REM Step 4: Create RAGOrchestratorLambdaRole
echo.
echo [STEP 4] Creating RAGOrchestratorLambdaRole...
aws iam create-role --role-name RAGOrchestratorLambdaRole --assume-role-policy-document file://lambda-trust-policy.json

aws iam attach-role-policy --role-name RAGOrchestratorLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

REM Create Bedrock policy for both models
(
echo {
echo   "Version": "2012-10-17",
echo   "Statement": [
echo     {
echo       "Effect": "Allow",
echo       "Action": "bedrock:InvokeModel",
echo       "Resource": [
echo         "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0",
echo         "arn:aws:bedrock:ap-south-1::foundation-model/global.amazon.nova-2-lite-v1:0"
echo       ]
echo     }
echo   ]
echo }
) > orchestrator-bedrock-policy.json

aws iam put-role-policy --role-name RAGOrchestratorLambdaRole --policy-name BedrockAccessPolicy --policy-document file://orchestrator-bedrock-policy.json

echo Done: Created RAGOrchestratorLambdaRole with policies

REM Step 5: Verify roles created
echo.
echo [STEP 5] Verifying roles...
aws iam list-roles --query "Roles[?contains(RoleName, 'Lambda')].RoleName"

echo.
echo ==========================================
echo IAM Role Setup Complete!
echo ==========================================
echo.
echo Next step: Run 'python scripts\test_bedrock.py' to test Bedrock models
pause
