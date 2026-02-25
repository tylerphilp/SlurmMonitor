# %%
import requests
from dotenv import load_dotenv
import os

# %%


class SlackMessenger:
    def __init__(self):
        # Read webhook from the env file
        load_dotenv()
        self.webhook_url = os.getenv("webhook_url")

    def send_message(self, message: str):
        message_payload = {"text": message}

        try:
            response = requests.post(self.webhook_url, json=message_payload)
            if response.status_code == 200:
                print("Message sent to slack")

            else:
                print(
                    f"Failed to send message. Response status: {response.status_code}"
                )

        except Exception as e:
            print(f"Exception occurred when sending message: {e}")
