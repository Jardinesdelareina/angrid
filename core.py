import time
import json
import asyncio
import pandas as pd
from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException as bae
from config import CLIENT, ENGINE
from utils import round_list


class Angrid:

    def __init__(self, symbol: str, price_step_percent: float = 1.0, depth_grid: int = 10):
        self.symbol = symbol
        self.price_step_percent = price_step_percent
        self.depth_grid = depth_grid


    def create_frame(self, stream):
        try:
            df = pd.DataFrame([stream])
            df = df.loc[:,['s', 'E', 'b', 'a']]
            df.columns = ['symbol', 'time', 'bid', 'ask']
            df.time = pd.Series(pd.to_datetime(df.time, unit='ms', utc=True)).dt.strftime('%Y-%m-%d %H:%M:%S')
            for column in ['bid', 'ask']:
                df[column] = round(df[column].astype(float), round_list[f'{self.symbol}'])
            print(f'{df.symbol}: {df.time} {df.bid} {df.ask}')
            self.db_ticker = df.symbol.str.lower().iloc[0]
            df.to_sql(name=f'{self.db_ticker}', con=ENGINE, if_exists='append', index=False)
        except KeyError:
            pass
    

    def place_buy_limit(self, price: float):
        asset_balance = CLIENT.get_asset_balance('USDT')
        balance_free = float(asset_balance.get('free'))
        qnty = balance_free / 10
        order_buy_limit = CLIENT.order_limit_buy(
            symbol=self.symbol,
            quantity=qnty,
            price=price
        )
        print(json.dumps(order_buy_limit, indent=4, sort_keys=True))


    def plase_sell_limit(self, price: float):
        ticker = self.symbol.replace('')
        asset_balance = CLIENT.get_asset_balance(ticker)
        balance_free = float(asset_balance.get('free'))
        qnty = balance_free / 10
        order_sell_limit = CLIENT.order_limit_buy(
            symbol=self.symbol,
            quantity=qnty,
            price=price
        )
        print(json.dumps(order_sell_limit, indent=4, sort_keys=True))


    def create_grid(self, start_price: float):
        for i in range(self.depth_grid):
            buy_price = start_price * (1 - self.price_step_percent/100 * (i+1))
            self.place_buy_limit(buy_price)

        for i in range(self.depth_grid):
            sell_price = start_price * (1 + self.price_step_percent/100 * (i+1))
            self.place_sell_limit(sell_price)


    async def socket_stream(self):
        bm = BinanceSocketManager(client=CLIENT)
        ts = bm.symbol_ticker_socket(self.symbol)
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                if res:
                    try:
                        self.create_frame(res)
                    except bae:
                        print('Binance API Exception')
                        time.sleep(5)
                        self.create_frame(res)
                await asyncio.sleep(0)
                