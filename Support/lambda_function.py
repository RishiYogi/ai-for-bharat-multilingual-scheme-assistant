import json
import boto3
from pypdf import PdfReader  # pypdf (pure Python, Lambda-compatible)
import os
import uuid
import requests
from datetime import datetime
import time
import re

# Configuration
s3_client = boto3.client('s3', region_name='ap-south-1')
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-south-1')

CHROMA_API_URL = os.environ.get('CHROMA_API_URL')
CHROMA_API_KEY = os.environ.get('CHROMA_API_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET', 'aicloud-bharat-schemes')
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'
BATCH_SIZE = 20  # Process chunks in batches (increased for large PDFs)
MAX_CHUNKS = 1200  # Protection for extremely large PDFs

def lambda_handler(event, context):
    """Process PDF from S3, generate embeddings, store in ChromaDB"""
    
    start_time = time.time()
    
    try:
        # Extract S3 event details
        s3_event = event['Records'][0]['s3']
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']
        
        print(f"Processing PDF: s3://{bucket}/{key}")
        
        # Generate unique document_id for this PDF
        document_id = f"{os.path.basename(key).replace('.pdf', '')}_{int(time.time())}"
        
        # Download PDF from S3
        pdf_path = f'/tmp/{os.path.basename(key)}'
        s3_client.download_file(bucket, key, pdf_path)
        print(f"Downloaded PDF to {pdf_path}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(text)} characters from PDF")
        
        if len(text) < 100:
            raise Exception("PDF text extraction failed or PDF is empty")
        
        # Clean text before chunking
        text = clean_text(text)
        print(f"Cleaned text: {len(text)} characters")
        
        # Extract metadata from S3 tags
        metadata = extract_metadata(bucket, key)
        print(f"Metadata: {metadata}")
        
        # Chunk text
        chunks = chunk_text(text, chunk_size=700, overlap=120)
        print(f"Created {len(chunks)} chunks")
        
        # Apply max chunk limit
        if len(chunks) > MAX_CHUNKS:
            print(f"WARNING: Document exceeds chunk limit ({len(chunks)} chunks). Processing first {MAX_CHUNKS} chunks only.")
            chunks = chunks[:MAX_CHUNKS]
        
        # Process chunks in batches to avoid memory issues
        total_added = 0
        total_embedding_time = 0
        
        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[batch_start:batch_start + BATCH_SIZE]
            
            # Generate embeddings and prepare documents
            documents = []
            batch_embedding_start = time.time()
            
            for i, chunk in enumerate(batch_chunks):
                chunk_index = batch_start + i
                
                # Generate embedding with retry logic
                embedding_start = time.time()
                embedding = generate_embedding_with_retry(chunk, max_retries=3)
                embedding_time = (time.time() - embedding_start) * 1000
                total_embedding_time += embedding_time
                
                # Generate unique chunk_id
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                
                # Prepare document
                doc = {
                    "id": str(uuid.uuid4()),
                    "embedding": embedding,
                    "text": chunk,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "scheme_name": metadata['scheme_name'],
                        "category": metadata['category'],
                        "state": metadata['state'],
                        "language": metadata.get('language', 'en'),
                        "eligible_gender": metadata.get('eligible_gender', 'any'),
                        "eligible_employment": metadata.get('eligible_employment', ['any']),
                        "chunk_index": chunk_index,
                        "source_doc": os.path.basename(key)
                    }
                }
                documents.append(doc)
            
            batch_embedding_time = (time.time() - batch_embedding_start) * 1000
            
            # Send batch to ChromaDB with retry logic
            response = send_to_chromadb_with_retry(documents, max_retries=3)
            total_added += response['added_count']
            
            print(f"Batch {batch_start//BATCH_SIZE + 1}: Added {response['added_count']} documents (Total: {total_added}/{len(chunks)}) - Embedding time: {batch_embedding_time:.0f}ms")
        
        # Move PDF to processed folder
        processed_key = key.replace('raw/', 'processed/')
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=processed_key
        )
        s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"Moved PDF to {processed_key}")
        
        # Calculate total processing time
        total_time = time.time() - start_time
        avg_embedding_time = total_embedding_time / len(chunks) if len(chunks) > 0 else 0
        
        # Log performance metrics
        metrics = {
            'total_processing_time_sec': round(total_time, 2),
            'total_embedding_time_ms': round(total_embedding_time, 0),
            'avg_embedding_time_ms': round(avg_embedding_time, 2),
            'chunks_processed': len(chunks),
            'vectors_added': total_added
        }
        print(f"Performance metrics: {json.dumps(metrics)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PDF processed successfully',
                'pdf_name': os.path.basename(key),
                'document_id': document_id,
                'chunks_processed': len(chunks),
                'vectors_added': total_added,
                'processing_time_sec': round(total_time, 2)
            })
        }
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pypdf"""
    reader = PdfReader(pdf_path)
    text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        text += page_text
        print(f"Extracted page {page_num + 1}/{len(reader.pages)}: {len(page_text)} chars")
    return text

def clean_text(text):
    """Clean extracted text by removing page numbers, headers, footers, and excessive whitespace"""
    # Remove page numbers (common patterns: "Page 1", "1 of 10", "- 1 -")
    text = re.sub(r'\b[Pp]age\s+\d+\b', '', text)
    text = re.sub(r'\b\d+\s+of\s+\d+\b', '', text)
    text = re.sub(r'-\s*\d+\s*-', '', text)
    
    # Remove common header/footer patterns
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Standalone page numbers
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text