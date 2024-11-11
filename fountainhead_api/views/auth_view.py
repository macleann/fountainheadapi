"""Module for authentication views"""
import os
import requests
from django.contrib.auth import authenticate
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from fountainhead_api.serializers import UserSerializer, GameStateSerializer
from fountainhead_api.models import GameState

def get_user_data_with_game_state(user):
    user_serializer = UserSerializer(user)
    game_state, created = GameState.objects.get_or_create(
        user=user,
        defaults={'state': {'locations': []}}
    )
    game_state_serializer = GameStateSerializer(game_state)
    return {
        "user": user_serializer.data,
        "game_state": game_state_serializer.data,
    }

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            user_data = get_user_data_with_game_state(user)
            response.data.update(user_data)
        return response

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        response_data = get_user_data_with_game_state(user)
        response_data.update(tokens)
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        check_email = User.objects.filter(email=request.data['email']).first()
        if check_email is not None:
            return Response({'error': 'A user with this email already exists.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        new_user = User.objects.create_user(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            first_name=request.data['firstName'],
            last_name=request.data['lastName']
        )
        
        # Initialize with clean state
        initial_state = request.data.get('game_state', {'locations': []})
        if isinstance(initial_state, dict) and 'state' in initial_state:
            initial_state = initial_state['state']
            
        game_state = GameState.objects.create(
            user=new_user,
            state=initial_state
        )
        
        tokens = get_tokens_for_user(new_user)
        response_data = get_user_data_with_game_state(new_user)
        response_data.update(tokens)
        return Response(response_data, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({'error': 'A user with this username already exists.'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def google_authenticate(request):
    credential = request.data['codeResponse']
    current_game_state = request.data.get('game_state', {'locations': []})
    
    try:
        idinfo = id_token.verify_oauth2_token(credential, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')

        # Check if user exists, if not create a new user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        
        if created:
            user.set_unusable_password()
            user.save()
            
            # Clean the state before creating
            if isinstance(current_game_state, dict) and 'state' in current_game_state:
                current_game_state = current_game_state['state']
            
            GameState.objects.create(
                user=user, 
                state=current_game_state
            )

        tokens = get_tokens_for_user(user)
        response_data = get_user_data_with_game_state(user)
        response_data.update(tokens)
        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    response_data = get_user_data_with_game_state(request.user)
    return Response(response_data, status=status.HTTP_200_OK)