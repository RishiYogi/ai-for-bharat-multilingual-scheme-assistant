@echo off
REM Script to forcefully delete old IAM roles with all attached policies
REM Run this if the simple delete fails due to attached policies

echo ==========================================
echo Deleting Old IAM Roles (Force)
echo ==========================================

echo.
echo [1] Detaching policies from SchemeIngestionLambdaRole...
aws iam detach-role-policy --role-name SchemeIngestionLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>nul
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name S3AccessPolicy 2>nul
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name BedrockAccessPolicy 2>nul
aws iam delete-role --role-name SchemeIngestionLambdaRole 2>nul && echo Done: Deleted SchemeIngestionLambdaRole || echo Note: Role not found or already deleted

echo.
echo [2] Detaching policies from RAGOrchestratorLambdaRole...
aws iam detach-role-policy --role-name RAGOrchestratorLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>nul
aws iam delete-role-policy --role-name RAGOrchestratorLambdaRole --policy-name BedrockAccessPolicy 2>nul
aws iam delete-role --role-name RAGOrchestratorLambdaRole 2>nul && echo Done: Deleted RAGOrchestratorLambdaRole || echo Note: Role not found or already deleted

echo.
echo ==========================================
echo Cleanup Complete!
echo ==========================================
echo.
echo Now run: setup_iam_roles.bat
pause
