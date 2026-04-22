#!/usr/bin/env python3
"""
Black2 Hash Calculator - Python CLI Version
For AI agents and server environments

Usage:
  python calculate_hash.py <file_path>
  
Example:
  python calculate_hash.py large_file.zip
  python calculate_hash.py /path/to/data.tar.gz
  
Output (JSON format for AI parsing):
  {
    "file": "large_file.zip",
    "size": 21474836480,
    "size_human": "20.00 GB",
    "sha256": "abc123...",
    "algorithm": "SHA-256",
    "time_cost": 45.32
  }
"""

import hashlib
import sys
import os
import time
import json


def calculate_file_hash(file_path, chunk_size=10*1024*1024):
    """
    Calculate SHA-256 hash of a file (streaming read, supports large files)
    
    Args:
        file_path: Path to the file
        chunk_size: Chunk size for reading (default 10MB)
        
    Returns:
        dict: Hash value, file size, and metadata
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    if not os.path.isfile(file_path):
        return {"error": f"Not a file: {file_path}"}
    
    file_size = os.path.getsize(file_path)
    
    start_time = time.time()
    
    sha256_hash = hashlib.sha256()
    bytes_read = 0
    
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256_hash.update(chunk)
            bytes_read += len(chunk)
    
    time_cost = time.time() - start_time
    hash_hex = sha256_hash.hexdigest()
    
    # Format file size
    size_human = file_size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_human < 1024.0:
            size_human_str = f"{size_human:.2f} {unit}"
            break
        size_human /= 1024.0
    else:
        size_human_str = f"{size_human:.2f} PB"
    
    return {
        "file": file_path,
        "size": file_size,
        "size_human": size_human_str,
        "sha256": hash_hex,
        "algorithm": "SHA-256",
        "time_cost": round(time_cost, 2)
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"Calculating SHA-256 hash for: {file_path}\n")
    
    result = calculate_file_hash(file_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    # Output JSON for AI parsing
    print(json.dumps(result, indent=2))
    
    # Also output human-readable format
    print(f"\n✅ Hash calculation completed!")
    print(f"File: {result['file']}")
    print(f"Size: {result['size_human']}")
    print(f"SHA-256: {result['sha256']}")
    print(f"Algorithm: {result['algorithm']}")
    print(f"Time: {result['time_cost']}s")
    
    # Instructions for Black2
    print(f"\n📝 Next steps:")
    print(f"1. Copy the SHA-256 hash value")
    print(f"2. Upload your file to a public URL")
    print(f"3. Call Black2 API: POST /api/v1/products")
    print(f"   - file_hash: {result['sha256']}")
    print(f"   - delivery_url: your_public_url_here")


if __name__ == "__main__":
    main()
