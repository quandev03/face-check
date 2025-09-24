#!/usr/bin/env python3
"""
Script test kết nối Database và MinIO
"""

import psycopg2
from minio import Minio
from minio.error import S3Error
import sys
import os

# Database configuration
DB_CONFIG = {
    'host': '160.191.245.38',
    'port': 5433,
    'database': 'face_attendance',
    'user': 'postgres',
    'password': 'postgres'
}

# MinIO configuration  
MINIO_CONFIG = {
    'endpoint': '160.191.245.38:9000',
    'access_key': 'admin',
    'secret_key': 'Ngoquan@2003',
    'secure': False
}

def test_database_connection():
    """Test PostgreSQL connection"""
    print("🔍 Testing PostgreSQL connection...")
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Check for pgvector extension
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');")
        has_pgvector = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL connection successful!")
        print(f"   Version: {version[:50]}...")
        print(f"   pgvector extension: {'✅ Installed' if has_pgvector else '❌ Not installed'}")
        
        if not has_pgvector:
            print("⚠️  Warning: pgvector extension is required for face embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_minio_connection():
    """Test MinIO connection"""
    print("\n🔍 Testing MinIO connection...")
    try:
        # Create MinIO client
        client = Minio(
            MINIO_CONFIG['endpoint'],
            access_key=MINIO_CONFIG['access_key'],
            secret_key=MINIO_CONFIG['secret_key'],
            secure=MINIO_CONFIG['secure']
        )
        
        # Test connection by listing buckets
        buckets = list(client.list_buckets())
        
        print("✅ MinIO connection successful!")
        print(f"   Endpoint: {MINIO_CONFIG['endpoint']}")
        print(f"   Buckets found: {len(buckets)}")
        
        for bucket in buckets:
            print(f"   - {bucket.name} (created: {bucket.creation_date})")
        
        # Check if face-images bucket exists
        bucket_name = 'face-images'
        if client.bucket_exists(bucket_name):
            print(f"✅ Bucket '{bucket_name}' exists")
        else:
            print(f"⚠️  Bucket '{bucket_name}' does not exist")
            try:
                client.make_bucket(bucket_name)
                print(f"✅ Created bucket '{bucket_name}'")
            except Exception as e:
                print(f"❌ Failed to create bucket '{bucket_name}': {e}")
        
        return True
        
    except S3Error as e:
        print(f"❌ MinIO S3 error: {e}")
        return False
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        return False

def test_network_connectivity():
    """Test basic network connectivity"""
    print("\n🔍 Testing network connectivity...")
    
    import socket
    
    # Test database port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((DB_CONFIG['host'], DB_CONFIG['port']))
        sock.close()
        
        if result == 0:
            print(f"✅ Database port {DB_CONFIG['port']} is reachable")
        else:
            print(f"❌ Database port {DB_CONFIG['port']} is not reachable")
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
    
    # Test MinIO port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((DB_CONFIG['host'], 9000))
        sock.close()
        
        if result == 0:
            print(f"✅ MinIO port 9000 is reachable")
        else:
            print(f"❌ MinIO port 9000 is not reachable")
    except Exception as e:
        print(f"❌ MinIO connectivity test failed: {e}")

def main():
    """Main test function"""
    print("🧪 Connection Test for Face Recognition Service")
    print("=" * 50)
    
    # Test network connectivity first
    test_network_connectivity()
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test MinIO connection
    minio_ok = test_minio_connection()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"   MinIO: {'✅ OK' if minio_ok else '❌ FAILED'}")
    
    if db_ok and minio_ok:
        print("\n🎉 All connections successful! Ready to run Docker container.")
        print("\n🚀 Next steps:")
        print("   1. Run: ./docker-run.sh (macOS/Linux)")
        print("   2. Or: docker-run.bat (Windows)")
        print("   3. Or: docker-compose up --build")
        return 0
    else:
        print("\n❌ Some connections failed. Please check configuration.")
        print("\n🔧 Troubleshooting:")
        if not db_ok:
            print("   - Verify PostgreSQL is running at 160.191.245.38:5433")
            print("   - Check username/password: postgres/postgres")
            print("   - Ensure database 'face_attendance' exists")
            print("   - Install pgvector extension if missing")
        if not minio_ok:
            print("   - Verify MinIO is running at 160.191.245.38:9000")
            print("   - Check credentials: admin/Ngoquan@2003")
            print("   - Check firewall settings")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 