from marshmallow import Schema, fields, validate, ValidationError

class EmployeeSchema(Schema):
    id = fields.Integer(dump_only=True)
    employee_code = fields.String(required=True, validate=validate.Length(min=5, max=20))
    full_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(allow_none=True)
    department = fields.String(allow_none=True, validate=validate.Length(max=100))
    position = fields.String(allow_none=True, validate=validate.Length(max=100))
    status = fields.String(validate=validate.OneOf(['ACTIVE', 'INACTIVE']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class FaceEmbeddingSchema(Schema):
    id = fields.Integer(dump_only=True)
    employee_id = fields.String(required=True, validate=validate.Length(min=5, max=20))
    model_name = fields.String(dump_only=True)
    model_version = fields.String(dump_only=True)
    distance_metric = fields.String(dump_only=True)
    quality_score = fields.Float(allow_none=True, validate=validate.Range(min=0, max=1))
    liveness_score = fields.Float(allow_none=True, validate=validate.Range(min=0, max=1))
    bbox = fields.List(fields.Integer(), allow_none=True)
    source = fields.String(validate=validate.OneOf(['ENROLL', 'VERIFY', 'IMPORT']))
    status = fields.String(validate=validate.OneOf(['ACTIVE', 'INACTIVE', 'DELETED']))
    image_url = fields.String(allow_none=True)
    sha256 = fields.String(dump_only=True)
    created_by = fields.String(allow_none=True, validate=validate.Length(max=64))
    created_at = fields.DateTime(dump_only=True)
    
    # Employee info (joined)
    employee_code = fields.String(dump_only=True)
    full_name = fields.String(dump_only=True)

class FaceEnrollRequestSchema(Schema):
    employee_code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    created_by = fields.String(allow_none=True, validate=validate.Length(max=64))
    source = fields.String(missing='ENROLL', validate=validate.OneOf(['ENROLL', 'VERIFY', 'IMPORT']))

class FaceUpdateRequestSchema(Schema):
    quality_score = fields.Float(allow_none=True, validate=validate.Range(min=0, max=1))
    liveness_score = fields.Float(allow_none=True, validate=validate.Range(min=0, max=1))
    status = fields.String(allow_none=True, validate=validate.OneOf(['ACTIVE', 'INACTIVE']))
    created_by = fields.String(allow_none=True, validate=validate.Length(max=64))

class RecognitionResponseSchema(Schema):
    success = fields.Boolean()
    error = fields.String(allow_none=True)
    employee_id = fields.String(allow_none=True)  # Now varchar (employee_code)
    employee_code = fields.String(allow_none=True)
    full_name = fields.String(allow_none=True)
    department = fields.String(allow_none=True)
    position = fields.String(allow_none=True)
    confidence = fields.Float(allow_none=True)
    distance = fields.Float(allow_none=True)
    quality_score = fields.Float(allow_none=True)
    best_distance = fields.Float(allow_none=True)

class ApiResponseSchema(Schema):
    success = fields.Boolean()
    message = fields.String(allow_none=True)
    error = fields.String(allow_none=True)
    data = fields.Raw(allow_none=True) 