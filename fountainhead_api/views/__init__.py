# __init__.py for views
from .auth_view import register, login, google_authenticate, logout, get_user, CustomTokenObtainPairView
from .gamestate_view import my_state, clear_state
from .chat_view import chat