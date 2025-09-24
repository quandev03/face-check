#!/usr/bin/env python3

# Fix database.py - add commit to execute_one method

with open('database.py', 'r') as f:
    content = f.read()

# Fix execute_one method to include commit
old_method = '''    def execute_one(self, query, params=None):
        """Execute query and fetch one result"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()'''

new_method = '''    def execute_one(self, query, params=None):
        """Execute query and fetch one result"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                conn.commit()
                return result'''

content = content.replace(old_method, new_method)

with open('database.py', 'w') as f:
    f.write(content)

print("✅ Fixed database.py - added commit to execute_one method")
