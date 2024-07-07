from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="User API Title",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register_user'),
    path('auth/login/', views.login_user, name='login_user'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # User endpoints
    path('api/users/<int:pk>/', views.get_user_details, name='get_user_details'),
    
    # Organisation endpoints
    path('api/organisations/', views.get_organisations, name='get_organisations'),
    path('api/organisations/<str:orgId>/', views.get_organisation, name='get_organisation'),
    path('api/organisations/<str:orgId>/users/', views.add_user_to_organisation, name='add_user_to_organisation'),
    path('api/organisations/create/', views.create_organisation, name='create_organisation'),
]
