# utils.py

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import User  # Replace with your actual user model if not using Django's default

def create_access_token(user):
    """ Generate access token for the given user """
    token_payload = {
        'user_id': str(user.id),  # Assuming user.id is the unique identifier
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time (1 day in this example)
        'iat': datetime.utcnow(),  # Token issue time
    }
    return jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')

def decode_access_token(token):
    """ Decode and verify access token """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        return User.objects.get(id=user_id)  # Replace with your actual user model
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return None
