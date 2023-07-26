from binance.helpers import round_step_size
from config import CLIENT

ticker = 'SOLUSDT'

asset_balance_replace_usdt = ticker.replace('USDT', '')
asset_balance = CLIENT.get_asset_balance(asset_balance_replace_usdt)
balance_free = float('455.9488484')
symbol_info = CLIENT.get_symbol_info(ticker)
step_size = symbol_info.get('filters')[1]['stepSize']
print(round_step_size(balance_free, step_size))
#print(symbol_info)
