from rest_framework import serializers
from fountainhead_api.models import GameState

class GameStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameState
        fields = ('state', 'last_updated')
        
    def to_representation(self, instance):
        # Get the base representation
        representation = super().to_representation(instance)
        
        # If state is nested, unnest it
        if isinstance(representation['state'], dict) and 'state' in representation['state']:
            representation['state'] = representation['state']['state']
            
        return representation
        
    def to_internal_value(self, data):
        # If we're getting nested state data, unnest it before saving
        if isinstance(data.get('state'), dict) and 'state' in data['state']:
            data = data.copy()
            data['state'] = data['state']['state']
            
        return super().to_internal_value(data)