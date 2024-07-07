from rest_framework import serializers
from .models import User, Organisation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('userId', 'firstName', 'lastName', 'email', 'password', 'phone')
        extra_kwargs = {
            'password': {'write_only': True},
            'userId': {'read_only': True},  # Assuming userId is generated automatically
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user



class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ('orgId', 'name', 'description')
        extra_kwargs = {
            'orgId': {'read_only': True},  # Assuming orgId is generated automatically
        }
