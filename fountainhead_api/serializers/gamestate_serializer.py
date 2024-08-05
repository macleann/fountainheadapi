from rest_framework import serializers
from fountainhead_api.models import GameState

class GameStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameState
        fields = ('state', 'last_updated')