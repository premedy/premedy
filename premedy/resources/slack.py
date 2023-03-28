import logging
import os

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import ssl
import certifi
from premedy import config

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
ssl_context = ssl.create_default_context(cafile=certifi.where())

# next replace the previous line where you call the WebClient with the new line:
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"), ssl=ssl_context)
logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)

channel_id = os.environ.get("SLACK_BOT_CHANNEL")


def send_message(message: str):
    try:
        # Call the chat.postMessage method using the WebClient
        # The client passes the token you included in initialization
        client.chat_postMessage(channel=channel_id, text=message)

    except SlackApiError as e:
        print(f"Error: {e}")
