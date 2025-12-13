-- Initialize database with required extensions, types, and tables
-- This file is executed when PostgreSQL container starts for the first time

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
DO $$ BEGIN
    CREATE TYPE face_source AS ENUM ('ENROLL', 'VERIFY', 'IMPORT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE face_status AS ENUM ('ACTIVE', 'INACTIVE', 'DELETED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create employees table
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

-- Create face_embeddings table
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

-- Create attendance_logs table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_face_embeddings_employee_id ON face_embeddings(employee_id);
CREATE INDEX IF NOT EXISTS idx_face_embeddings_status ON face_embeddings(status);
CREATE INDEX IF NOT EXISTS idx_face_embeddings_sha256 ON face_embeddings(sha256);
CREATE INDEX IF NOT EXISTS idx_employees_code ON employees(employee_code);
CREATE INDEX IF NOT EXISTS idx_att_logs_emp_time ON attendance_logs(employee_code, recognized_at);
CREATE INDEX IF NOT EXISTS idx_att_logs_device_time ON attendance_logs(device_code, recognized_at);

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized with pgvector extension, enum types, tables, and indexes';
END $$;





