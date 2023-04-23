import requests
from telegram.config import config


def send_to_telegram(message):

    apiToken = config.bot_token.get_secret_value()
    chatID = '-1001935066797'  # t.me/cadastr
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

