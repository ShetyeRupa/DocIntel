#!/usr/bin/env python
"""Batch ingestion script for documents"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.pipeline import IngestionPipeline
import argparse

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into DocIntel")
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    args = parser.parse_args()
    
    print("🚀 Starting DocIntel Ingestion Pipeline")
    print(f"📁 Processing directory: {args.directory}")
    
    pipeline = IngestionPipeline()
    results = pipeline.batch_ingest(args.directory)
    
    print("\n📊 Ingestion Summary:")
    print(f"  Total documents: {results['total_documents']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Total chunks: {results['total_chunks']}")
    
    if results['successful'] > 0:
        print("\n✅ Ingestion complete!")
    else:
        print("\n❌ No documents were processed successfully.")
        sys.exit(1)

if __name__ == "__main__":
    main()