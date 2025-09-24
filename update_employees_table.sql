-- Update employees table to use employee_code as primary key

-- Step 1: Check current structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'employees' 
ORDER BY ordinal_position;

-- Step 2: Add unique constraint to employee_code if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'employees_employee_code_key'
    ) THEN
        ALTER TABLE employees ADD CONSTRAINT employees_employee_code_key UNIQUE (employee_code);
    END IF;
END $$;

-- Step 3: Update face_embeddings to reference employee_code
-- First, let's see what data we have
SELECT 
    fe.id as face_id,
    fe.employee_id as old_employee_id,
    e.employee_code,
    e.full_name
FROM face_embeddings fe
LEFT JOIN employees e ON fe.employee_id::VARCHAR = e.employee_code
WHERE fe.status = 'ACTIVE';

-- Step 4: Update face_embeddings.employee_id to use employee_code
UPDATE face_embeddings 
SET employee_id = e.employee_code
FROM employees e 
WHERE face_embeddings.employee_id::VARCHAR = e.employee_code;

-- Step 5: Add foreign key constraint
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'face_embeddings_employee_id_fkey'
    ) THEN
        ALTER TABLE face_embeddings DROP CONSTRAINT face_embeddings_employee_id_fkey;
    END IF;
END $$;

-- Add new foreign key constraint
ALTER TABLE face_embeddings 
ADD CONSTRAINT face_embeddings_employee_id_fkey 
FOREIGN KEY (employee_id) REFERENCES employees(employee_code);

-- Step 6: Add index for performance
CREATE INDEX IF NOT EXISTS idx_face_embeddings_employee_code ON face_embeddings(employee_id);

-- Step 7: Verify the changes
SELECT 
    'face_embeddings' as table_name,
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'face_embeddings' AND column_name = 'employee_id'
UNION ALL
SELECT 
    'employees' as table_name,
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'employees' AND column_name = 'employee_code';

COMMIT;
