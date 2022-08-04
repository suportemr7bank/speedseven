"""
Core channels consumer
"""

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class EmailBatchConsumer(WebsocketConsumer):
    """
    Consumer form email batch page
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.consumer_group_name = 'batch_email'


    def connect(self):
        # connection has to be accepted
        self.accept()

        # join the room group
        async_to_sync(self.channel_layer.group_add)(
            self.consumer_group_name,
            self.channel_name,
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.consumer_group_name,
            self.channel_name,
        )

    def send_batch_email(self, event):
        """
        Send message to update email sending status
        """
        self.send(text_data=json.dumps(event))
