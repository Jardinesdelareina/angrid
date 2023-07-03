import time
import asyncio
import pandas as pd

from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException as bae

from config import CLIENT, ENGINE


class BinanceAPI:

    def __init__(self, symbol):
        self.symbol = symbol


    def create_frame(self, stream):
        try:
            df = pd.DataFrame([stream])
            df = df.loc[:,['s', 'E', 'p']]
            df.columns = ['symbol', 'time', 'price']
            df.time = pd.to_datetime(df.time, unit='ms', utc=True, infer_datetime_format=True)
            df.price = df.price.astype(float)
            self.db_ticker = df.symbol.str.lower().iloc[0]
            df.to_sql(name=f'{self.db_ticker}', con=ENGINE, if_exists='append', index=False)
        except KeyError:
            pass

    
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