import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
from contextlib import contextmanager
import logging
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self.init_pool()
    
    def init_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                Config.DB_POOL_MIN_CONN, Config.DB_POOL_MAX_CONN,
                Config.DATABASE_URL,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Database connection pool initialized (min: {Config.DB_POOL_MIN_CONN}, max: {Config.DB_POOL_MAX_CONN})")
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute query with connection from pool"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
                return cursor.rowcount
    
    def execute_one(self, query, params=None):
        """Execute query and fetch one result"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                conn.commit()
                return result
    
    def close_all_connections(self):
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

def init_database():
    """Initialize database with required tables and enums"""
    init_queries = [
        # Create enum types
        """
        DO $$ BEGIN
            CREATE TYPE face_source AS ENUM ('ENROLL', 'VERIFY', 'IMPORT');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        
        """
        DO $$ BEGIN
            CREATE TYPE face_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        
        # Enable pgvector extension
        "CREATE EXTENSION IF NOT EXISTS vector;",
        
        # Create employees table if not exists
        """
        CREATE TABLE IF NOT EXISTS employees (
            id BIGSERIAL PRIMARY KEY,
            employee_code VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            department VARCHAR(100),
            position VARCHAR(100),
            status VARCHAR(20) DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """,
        
        # Create face_embeddings table
        """
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id BIGSERIAL PRIMARY KEY,
            employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_code) ON DELETE CASCADE,
            vector vector(128) NOT NULL,
            model_name VARCHAR(64) NOT NULL DEFAULT 'face_recognition',
            model_version VARCHAR(32) NOT NULL DEFAULT '1.0',
            distance_metric VARCHAR(8) NOT NULL DEFAULT 'l2',
            quality_score REAL,
            liveness_score REAL,
            bbox INT4[4],
            source face_source NOT NULL DEFAULT 'ENROLL',
            status face_status NOT NULL DEFAULT 'ACTIVE',
            image_url TEXT,
            sha256 CHAR(64) NOT NULL,
            created_by VARCHAR(64),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
        
        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_face_embeddings_employee_id ON face_embeddings(employee_id);",
        "CREATE INDEX IF NOT EXISTS idx_face_embeddings_status ON face_embeddings(status);",
        "CREATE INDEX IF NOT EXISTS idx_face_embeddings_sha256 ON face_embeddings(sha256);",
        "CREATE INDEX IF NOT EXISTS idx_employees_code ON employees(employee_code);",
        
        # Attendance logs table to record recognition events (check-in/out history)
        """
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id BIGSERIAL PRIMARY KEY,
            employee_code VARCHAR(50) NOT NULL REFERENCES employees(employee_code) ON DELETE CASCADE,
            recognized_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            device_code VARCHAR(64),
            confidence REAL,
            distance REAL,
            quality_score REAL,
            bbox INT4[4],
            image_url TEXT,
            source VARCHAR(32) DEFAULT 'RECOGNIZE' NOT NULL
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_att_logs_emp_time ON attendance_logs(employee_code, recognized_at);",
        "CREATE INDEX IF NOT EXISTS idx_att_logs_device_time ON attendance_logs(device_code, recognized_at);",
    ]
    
    try:
        for query in init_queries:
            db_manager.execute_query(query)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise 