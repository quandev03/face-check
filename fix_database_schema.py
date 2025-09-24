#!/usr/bin/env python3

# Fix database schema in database.py

with open('database.py', 'r') as f:
    content = f.read()

# Fix the face_embeddings table creation
old_table = '''        # Create face_embeddings table
        """
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id BIGSERIAL PRIMARY KEY,
            employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            vector vector(128) NOT NULL,
            model_name VARCHAR(64) NOT NULL DEFAULT 'face_recognition',
            model_version VARCHAR(32) NOT NULL DEFAULT '1.0',
            distance_metric VARCHAR(8) NOT NULL DEFAULT 'l2','''

new_table = '''        # Create face_embeddings table
        """
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id BIGSERIAL PRIMARY KEY,
            employee_id VARCHAR(50) NOT NULL REFERENCES employees(employee_code) ON DELETE CASCADE,
            vector vector(128) NOT NULL,
            model_name VARCHAR(64) NOT NULL DEFAULT 'face_recognition',
            model_version VARCHAR(32) NOT NULL DEFAULT '1.0',
            distance_metric VARCHAR(8) NOT NULL DEFAULT 'l2','''

content = content.replace(old_table, new_table)

with open('database.py', 'w') as f:
    f.write(content)

print("✅ Fixed database schema in database.py")
