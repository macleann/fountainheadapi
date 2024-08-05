from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from fountainhead_api.models import GameState
from fountainhead_api.serializers import GameStateSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_state(request):
    game_state, created = GameState.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = GameStateSerializer(game_state)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Get the game state data from the request
        new_state = request.data.get('game_state')
        
        if new_state is None:
            return Response({"error": "No game_state provided in the request"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the game state
        game_state.state = new_state
        game_state.save()
        
        serializer = GameStateSerializer(game_state)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_state(request):
    game_state, created = GameState.objects.get_or_create(user=request.user)
    game_state.state = {}
    game_state.save()
    return Response({"message": "Game state cleared successfully"}, status=status.HTTP_200_OK)