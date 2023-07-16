import requests
import pandas as pd
from sqlalchemy import text
from config import TELETOKEN, CHAT_ID, ENGINE

symbol_list = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT']
round_list = {'BTCUSDT': 2, 'ETHUSDT': 2, 'BNBUSDT': 1, 'XRPUSDT': 4}


def send_message(message: str):
    return requests.get(
        f'https://api.telegram.org/bot{TELETOKEN}/sendMessage', 
        params=dict(chat_id=CHAT_ID, text=message)
    )


def execute_query(query: str):
    with ENGINE.connect() as conn:
        result = conn.execute(text(query))
        df_result = pd.DataFrame(result.fetchall())
        return float(df_result.iloc[-1].values)
