-- Initialize database with required extensions and types
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

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized with pgvector extension and enum types';
END $$; 