-- Initialize convosphere database
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user', 'guest');
CREATE TYPE assistant_status AS ENUM ('active', 'inactive', 'draft');
CREATE TYPE tool_category AS ENUM ('search', 'file', 'api', 'database', 'custom');

-- Create audit log function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create full-text search function
CREATE OR REPLACE FUNCTION search_conversations(search_term TEXT)
RETURNS TABLE(id UUID, title TEXT, similarity REAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        similarity(c.title, search_term) as similarity
    FROM conversations c
    WHERE c.title ILIKE '%' || search_term || '%'
       OR similarity(c.title, search_term) > 0.3
    ORDER BY similarity DESC;
END;
$$ LANGUAGE plpgsql; 