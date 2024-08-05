import os
from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create an instance of the OpenAI class
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    try:
        # Extract the message and conversation history from the request data
        message = request.data.get('message')
        conversation_history = request.data.get('conversation_history', [])

        if not message:
            return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the messages for the API call
        system_prompt = {"role": "system", "content": "You are a house cat named Old Friend. You have vast knowledge of the world of Fountainhead."}
        messages = [system_prompt] + conversation_history + [{"role": "user", "content": message}]

        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1.3,
        )

        # Extract the assistant's reply
        reply = response.choices[0].message.content

        # Update the conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply}
        ]

        return Response({
            "reply": reply,
            "conversation_history": updated_history
        })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)