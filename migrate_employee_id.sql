-- Migration script to change employee_id from integer to varchar in face_embeddings table

-- Step 1: Add new column with varchar type
ALTER TABLE face_embeddings 
ADD COLUMN employee_id_new VARCHAR(50);

-- Step 2: Copy data from old column to new column (convert integer to string)
UPDATE face_embeddings 
SET employee_id_new = employee_id::VARCHAR;

-- Step 3: Drop the old column
ALTER TABLE face_embeddings 
DROP COLUMN employee_id;

-- Step 4: Rename new column to original name
ALTER TABLE face_embeddings 
RENAME COLUMN employee_id_new TO employee_id;

-- Step 5: Add NOT NULL constraint
ALTER TABLE face_embeddings 
ALTER COLUMN employee_id SET NOT NULL;

-- Step 6: Add foreign key constraint (if needed)
-- Note: This will only work if employees table also has employee_code as primary key
-- If not, you might need to adjust the employees table structure

-- Step 7: Add index for performance
CREATE INDEX idx_face_embeddings_employee_id ON face_embeddings(employee_id);

-- Step 8: Update any existing foreign key constraints
-- Drop existing foreign key if it exists
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'face_embeddings_employee_id_fkey'
    ) THEN
        ALTER TABLE face_embeddings DROP CONSTRAINT face_embeddings_employee_id_fkey;
    END IF;
END $$;

-- Add new foreign key constraint (assuming employees table has employee_code as primary key)
-- If employees table still uses integer id, you'll need to update it first
-- ALTER TABLE face_embeddings 
-- ADD CONSTRAINT face_embeddings_employee_id_fkey 
-- FOREIGN KEY (employee_id) REFERENCES employees(employee_code);

COMMIT;
