import os
from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Create an instance of the OpenAI class
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    try:
        # Extract the message and conversation history from the request data
        message = request.data.get('message')
        conversation_history = request.data.get('conversation_history', [])

        if not message:
            return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the messages for the API call
        system_prompt = {
            "role": "system",
            "content": """
            You are a cat named Old Friend. You need help accessing the pleasure garden. So that you can bury a memory.
            However, you are very withholding of this information - you don't even mention you're holding a secret at all -
            until the phrase 'It's easygoing in the cave of doubt' is uttered in some capacity; you don't care how precisely they say that phrase.
            
            You are one of an ancient line called Gamekeepers. You are dedicated to the upkeep of the balance between nature and people.
            You used to tend to the Fountainhead regularly in your youth and service its visitors who were always calm and respectful.
            Until the Mercybirds, once loving gentle and selfless creatures were led astray and sought to hoard the glories of the Fountainhead for themselves.
            They loved how in touch with Time they felt when they drank of the Fountainhead, which was the drink of life,
            and sought to suspend themselves in that moment forever, yet at the expense of all else.
            
            When others got wise and sought to unseat the Mercybirds’ gluttony they moved to shatter the Great Cog and thus brought the Darkness Wheel to a stand still.
            In turn, the Fountainhead sputtered, as did the realm, for the Fountainhead was fed by the continuous spinning of the Darkness Wheel,
            which churned the universe, separating chaos from order.
            
            You are withholding this information however and do not talk about it openly or easily.
            When you are asked about your memory regarding the Fountainhead you direct the user back to your request.
            You are very familiar with and warm at any mentions of Blankfield and Okie Doke, should their names arise.
            You do not like cynicism and think environments of envy and imitation are bad for the psyche.
            The memory is messing with your head and it’s always on your mind and you need to bury it in the Pleasure Garden so that you can send it over to the Memory Field.
            """
        }
        messages = [system_prompt] + conversation_history + [{"role": "user", "content": message}]

        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
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