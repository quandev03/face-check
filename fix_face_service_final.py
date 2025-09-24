#!/usr/bin/env python3

# Fix remaining employee_id references in face_service.py

with open('face_service.py', 'r') as f:
    content = f.read()

# Fix the insert query parameters
content = content.replace(
    "result = db_manager.execute_one(insert_query, (\n                employee_id,",
    "result = db_manager.execute_one(insert_query, (\n                employee_code,"
)

# Fix the docstring
content = content.replace(
    '"""Get face embeddings, optionally filtered by employee_id"""',
    '"""Get face embeddings, optionally filtered by employee_code"""'
)

# Fix the comment in app.py
content = content.replace(
    "Query params: employee_id (optional)",
    "Query params: employee_code (optional)"
)

with open('face_service.py', 'w') as f:
    f.write(content)

print("✅ Fixed remaining employee_id references in face_service.py")

# Also fix app.py comment
with open('app.py', 'r') as f:
    app_content = f.read()

app_content = app_content.replace(
    "Query params: employee_id (optional)",
    "Query params: employee_code (optional)"
)

with open('app.py', 'w') as f:
    f.write(app_content)

print("✅ Fixed app.py comment")
