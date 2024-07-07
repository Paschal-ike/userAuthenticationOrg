from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer, OrganisationSerializer
from .models import Organisation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Register a new user and create a default organisation for them.",
    request_body=UserSerializer,
    responses={
        201: openapi.Response(
            description="Registration successful",
            examples={
                "application/json": {
                    'status': 'success',
                    'message': 'Registration successful',
                    'data': {
                        'accessToken': 'your_jwt_access_token',
                        'user': {
                            'username': 'johndoe',
                            'email': 'johndoe@example.com',
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'nin': '123456789012',
                            'phone_number': '1234567890'
                        }
                    }
                }
            }
        ),
        400: openapi.Response(
            description="Registration unsuccessful",
            examples={
                "application/json": {
                    'status': 'Bad request',
                    'message': 'Registration unsuccessful',
                    'errors': {
                        'username': ['This field is required.'],
                        'email': ['This field is required.'],
                        'password': ['This field is required.']
                    }
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # Hash the password before saving
        user = serializer.save()
        # Create default organisation
        org_name = f"{user.first_name}'s Organisation"
        organisation = Organisation.objects.create(name=org_name)
        # Return response with access token and user data
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'success',
            'message': 'Registration successful',
            'data': {
                'accessToken': str(refresh.access_token),
                'user': serializer.data
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        'status': 'Bad request',
        'message': 'Registration unsuccessful',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Authenticate a user and return an access token.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password')
        },
        required=['email', 'password']
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'accessToken': 'your_jwt_access_token',
                        'user': {
                            'username': 'johndoe',
                            'email': 'johndoe@example.com',
                            'first_name': 'John',
                            'last_name': 'Doe',
                            'nin': '123456789012',
                            'phone_number': '1234567890'
                        }
                    }
                }
            }
        ),
        401: openapi.Response(
            description="Authentication failed",
            examples={
                "application/json": {
                    'status': 'Bad request',
                    'message': 'Authentication failed',
                    'statusCode': 401
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)

    if user:
        serializer = UserSerializer(user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'accessToken': str(refresh.access_token),
                'user': serializer.data
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': status.HTTP_401_UNAUTHORIZED
        }, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve user details by user ID.",
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description="User ID", type=openapi.TYPE_INTEGER
        )
    ],
    responses={
        200: openapi.Response(
            description="User details retrieved",
            examples={
                "application/json": {
                    'status': 'success',
                    'message': 'User details retrieved',
                    'data': {
                        'username': 'johndoe',
                        'email': 'johndoe@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'nin': '123456789012',
                        'phone_number': '1234567890'
                    }
                }
            }
        ),
        403: openapi.Response(
            description="Forbidden",
            examples={
                "application/json": {
                    'status': 'Forbidden',
                    'message': 'You do not have permission to access this user details'
                }
            }
        ),
        404: openapi.Response(
            description="Not Found",
            examples={
                "application/json": {
                    'status': 'Not Found',
                    'message': 'User not found'
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request, id):
    try:
        # Retrieve user details
        user = User.objects.get(id=id)
        # Check if the requesting user has access to this user's details (e.g., own record or in organizations they belong to or created)
        # Example logic, adjust according to your actual requirements:
        if request.user == user or request.user.organisations.filter(id=user.organisation.id).exists():
            serializer = UserSerializer(user)
            return Response({
                'status': 'success',
                'message': 'User details retrieved',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Forbidden',
                'message': 'You do not have permission to access this user details'
            }, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({
            'status': 'Not Found',
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organisations(request):
    try:
        # Retrieve organisations that the user belongs to or created
        organisations = request.user.organisations.all()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response({
            'status': 'success',
            'message': 'Organisations retrieved',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'Internal Server Error',
            'message': 'Failed to retrieve organisations',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organisation(request, orgId):
    try:
        # Retrieve a single organisation that the user belongs to or created
        organisation = request.user.organisations.get(id=orgId)
        serializer = OrganisationSerializer(organisation)
        return Response({
            'status': 'success',
            'message': 'Organisation retrieved',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Organisation.DoesNotExist:
        return Response({
            'status': 'Not Found',
            'message': 'Organisation not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'Internal Server Error',
            'message': 'Failed to retrieve organisation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organisation(request):
    try:
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            # Create a new organisation and associate it with the current user
            organisation = serializer.save()
            request.user.organisations.add(organisation)
            return Response({
                'status': 'success',
                'message': 'Organisation created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'Bad Request',
            'message': 'Failed to create organisation',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'Internal Server Error',
            'message': 'Failed to create organisation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_to_organisation(request, orgId):
    try:
        organisation = request.user.organisations.get(id=orgId)
        userId = request.data.get('userId')
        user_to_add = User.objects.get(id=userId)
        
        # Optionally, perform additional checks or validations here
        
        # Add user to organisation
        organisation.members.add(user_to_add)
        
        return Response({
            'status': 'success',
            'message': 'User added to organisation successfully'
        }, status=status.HTTP_200_OK)
    except Organisation.DoesNotExist:
        return Response({
            'status': 'Not Found',
            'message': 'Organisation not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({
            'status': 'Not Found',
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'Internal Server Error',
            'message': 'Failed to add user to organisation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

