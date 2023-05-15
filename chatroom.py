import chatgpt_stuff
import random

class User:
    # uses chatgpt_stuff.use_chatgpt(messages_object) to talk
    # chatroom object requires a `send` function
    # mapper is a something that lets it talk. by default uses the chatgpt api, but could be anything.

    def __init__(self, username):
        self.username = username
        self.chatroom = None
        self.mapper = self._chatroomstate_to_text

    def _chatroomstate_to_text(self, chatroomstate):
        messages = [
            {
                'role': 'system',
                'content': f'You are a simulated chatroom user. Your name: {self.username}.\nCurrent chatroom: {str(chatroomstate)}\n\nPlease respond in a human-like way. Your job is to entertain whoever is reading this chatroom simulation.'
            }
        ]
        response = chatgpt_stuff.use_chatgpt(messages)
        return response

    def talk(self):
        state = self.chatroom.get_current_state()
        text = self.mapper(state)
        self.chatroom.send(
            self,
            text
        )

class Chatroom:
    """
    should handle:
        - sending a message
        - getting the current state of the chatroom
    """
    def __init__(self):
        self.messages = []

    def add_message(self, user, text):
        self.messages.append({
            'user object': user,
            'text': text
        })

    def get_current_state(self):
        lines = []
        for message in self.messages:
            lines.append(f'{message["user object"].username}:')
            lines.append(f'    {message["text"]}')
            lines.append('-'*10)
        return '\n'.join(lines)

    def send(self, user_obj, text):
        assert isinstance(user_obj, User)
        assert isinstance(text, str)
        self.add_message(user_obj, text)