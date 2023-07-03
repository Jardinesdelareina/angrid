import requests
from config import CLIENT, TELETOKEN, CHAT_ID


def send_message(message: str):
    return requests.get(
        f'https://api.telegram.org/bot{TELETOKEN}/sendMessage', 
        params=dict(chat_id=CHAT_ID, text=message)
    )


def get_balance_ticker(ticker: str):
    asset_balance = CLIENT.get_asset_balance(ticker)
    if ticker == 'USDT':
        round_balance = 1
    else:
        round_balance = 4
    return round(float(asset_balance.get('free')), round_balance)