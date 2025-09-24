#!/usr/bin/env python3

# Fix schema validation error

with open('schemas.py', 'r') as f:
    content = f.read()

# Fix FaceEnrollRequestSchema
old_schema = '''class FaceEnrollRequestSchema(Schema):
    employee_id = fields.Integer(required=True)
    created_by = fields.String(allow_none=True, validate=validate.Length(max=64))
    source = fields.String(missing='ENROLL', validate=validate.OneOf(['ENROLL', 'VERIFY', 'IMPORT']))'''

new_schema = '''class FaceEnrollRequestSchema(Schema):
    employee_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    created_by = fields.String(allow_none=True, validate=validate.Length(max=64))
    source = fields.String(missing='ENROLL', validate=validate.OneOf(['ENROLL', 'VERIFY', 'IMPORT']))'''

content = content.replace(old_schema, new_schema)

# Fix RecognitionResponseSchema
old_response = '''class RecognitionResponseSchema(Schema):
    success = fields.Boolean()
    error = fields.String(allow_none=True)
    employee_id = fields.Integer(allow_none=True)
    employee_code = fields.String(allow_none=True)
    full_name = fields.String(allow_none=True)'''

new_response = '''class RecognitionResponseSchema(Schema):
    success = fields.Boolean()
    error = fields.String(allow_none=True)
    employee_id = fields.String(allow_none=True)  # Now varchar (employee_code)
    employee_code = fields.String(allow_none=True)
    full_name = fields.String(allow_none=True)'''

content = content.replace(old_response, new_response)

with open('schemas.py', 'w') as f:
    f.write(content)

print("✅ Fixed schema validation - employee_id -> employee_code")
