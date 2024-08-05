from django.db import models
from django.contrib.auth.models import User

class GameState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='game_state')
    state = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def set_state(self, data):
        self.state = data
        self.save()

    def get_state(self):
        return self.state