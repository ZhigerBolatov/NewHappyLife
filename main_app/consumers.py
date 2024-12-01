import json
import openai
import os
from channels.generic.websocket import AsyncWebsocketConsumer


openai.api_key = os.environ.get("OPENAI_API_KEY")


class OpenAIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This method handles the connection. It runs when a WebSocket is opened.
        self.room_group_name = 'openai_chat'  # You can create a room for multiple users.

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # This method handles the disconnection.
        pass

    async def receive(self, text_data):
        # Receive a message from WebSocket
        data = json.loads(text_data)
        user_message = data['message']

        # Make request to OpenAI API
        response = await self.chat_with_openai(user_message)

        # Send the OpenAI response back to WebSocket
        await self.send(text_data=json.dumps({
            'message': response,
        }))

    async def chat_with_openai(self, message):
        # Make asynchronous request to OpenAI API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  # You can use "gpt-4" if available
            prompt=message,
            max_tokens=150,
            temperature=0.7,
        )
        return response['choices'][0]['text'].strip()
