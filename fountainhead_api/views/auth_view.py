"""Module for authentication views"""
import os
import requests
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.middleware import csrf
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from fountainhead_api.serializers import UserSerializer, GameStateSerializer
from fountainhead_api.models import GameState

def get_user_data_with_game_state(user):
    user_serializer = UserSerializer(user)
    game_state, created = GameState.objects.get_or_create(user=user)
    game_state_serializer = GameStateSerializer(game_state)
    return {
        "user": user_serializer.data,
        "game_state": game_state_serializer.data,
        "valid": True
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        django_login(request, user)
        response_data = get_user_data_with_game_state(user)
        response = Response(response_data, status=status.HTTP_200_OK)
        csrf_token = get_token(request)
        response.set_cookie('csrftoken', csrf_token, httponly=False)
        return response
    else:
        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        check_email = User.objects.filter(email=request.data['email']).first()
        if check_email is not None:
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_user = User.objects.create_user(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            first_name=request.data['firstName'],
            last_name=request.data['lastName']
        )
        
        # Save the current game state
        current_game_state = request.data.get('game_state', {})
        GameState.objects.create(user=new_user, state=current_game_state)
        
        django_login(request, new_user)
        response_data = get_user_data_with_game_state(new_user)
        response = Response(response_data, status=status.HTTP_201_CREATED)
        csrf_token = get_token(request)
        response.set_cookie('csrftoken', csrf_token, httponly=False)
        return response
    except IntegrityError:
        return Response({'error': 'A user with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    code = request.data['codeResponse']
    current_game_state = request.data.get('game_state', {})
    
    # Get access token from Google
    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = os.getenv('CLIENT_URL')
    data = {
        'code': code,
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': f'{redirect_uri}/login',
        'grant_type': 'authorization_code'
    }
    
    token_response = requests.post(token_url, data=data)
    token_data = token_response.json()
    
    # Get user info from Google
    user_info_url = f'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={token_data["access_token"]}'
    user_info_response = requests.get(user_info_url)
    user_info = user_info_response.json()
    
    # Check if user exists, if not create a new user
    user, created = User.objects.get_or_create(
        email=user_info['email'],
        defaults={
            'username': user_info['email'],
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', '')
        }
    )
    
    if created:
        user.set_unusable_password()
        user.save()
        # Create game state with the provided state for new user
        GameState.objects.create(user=user, state=current_game_state)
    else:
        # For existing users, we might want to update their game state if it's newer
        game_state, _ = GameState.objects.get_or_create(user=user)
        if current_game_state:  # Only update if a new state is provided
            game_state.state = current_game_state
            game_state.save()

    django_login(request, user)
    response_data = get_user_data_with_game_state(user)
    response = Response(response_data, status=status.HTTP_200_OK)
    csrf_token = get_token(request)
    response.set_cookie('csrftoken', csrf_token, httponly=False)
    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    django_logout(request)
    response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    response.delete_cookie('csrftoken')
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    response = get_user_data_with_game_state(request.user)
    return Response(response, status=status.HTTP_200_OK)