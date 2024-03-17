# utilities.py

def validate_json_input(data, required_fields):
    errors = {}
    for field in required_fields:
        if field not in data:
            errors[field] = 'This field is required.'
        elif not data[field]:  # Additional checks can be added here
            errors[field] = 'This field cannot be empty.'
    return errors
