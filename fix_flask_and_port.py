#!/usr/bin/env python3

# Fix Flask before_first_request and update port to 5555

import re

# Fix app.py - remove deprecated @app.before_first_request
with open('app.py', 'r') as f:
    content = f.read()

# Remove the deprecated decorator and move initialization to main block
content = re.sub(
    r'# Initialize database on startup\n@app\.before_first_request\ndef initialize\(\):\s*"""Initialize database tables"""\s*try:\s*init_database\(\)\s*logger\.info\("Application initialized successfully"\)\s*except Exception as e:\s*logger\.error\(f"Failed to initialize application: \{e\}"\)\s*raise',
    '# Database initialization moved to main block',
    content,
    flags=re.DOTALL
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed Flask before_first_request deprecation")

# Update port in docker-compose.yml
with open('docker-compose.yml', 'r') as f:
    content = f.read()

content = content.replace('PORT: 5000', 'PORT: 5555')
content = content.replace('"5555:5000"', '"5555:5555"')
content = content.replace('localhost:5000', 'localhost:5555')

with open('docker-compose.yml', 'w') as f:
    f.write(content)

print("✅ Updated port to 5555 in docker-compose.yml")

# Update other files
files_to_update = [
    'config.env.example',
    'README.md', 
    'SETUP.md',
    'DOCKER.md',
    'test_api.py',
    'test_connection.py'
]

for filename in files_to_update:
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        content = content.replace('localhost:5000', 'localhost:5555')
        content = content.replace('PORT=5000', 'PORT=5555')
        
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {filename}")
    except FileNotFoundError:
        print(f"⚠️  File {filename} not found, skipping")

print("\n🎉 All fixes applied!")
print("Now run: docker-compose up --build -d")
