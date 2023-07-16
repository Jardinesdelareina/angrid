import time
import asyncio
import pandas as pd
from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException as bae
from config import CLIENT, ENGINE, DEBUG
from utils import round_list, send_message


class Angrid:
    """ Алгоритм, представляющий стратегию "сеточной торговли".
        Основная идея стратегии заключается в том, чтобы стараться извлекать прибыль из рыночных
        колебаний вне зависимости от направления движения цены. Так как большую часть времени статистически 
        цена находится в боковом движении, упор на спекуляции сделан именно во флете.

        Риски: при сильных движениях за пределы сетки есть риск либо недополучить прибыль,
        либо закупить криптовалюту на все оставшиеся стейблкоины с уходом цены далеко ниже крайнего лимитного 
        SELL-ордера, что автоматически переквалифицирует стратегию в `buy and hold`.
    """

    INIT = False    # Инициализация алгоритма


    def __init__(self, symbol: str, price_step_percent: float = 1.0, depth_grid: int = 5):
        """ symbol (str): Криптовалютный тикер
            price_step_percent (float): Дистанция между лимитными ордерами в сетке ордеров (в процентах)
            depth_grid (int): Глубина сетки, количество ордеров (как Buy, так и Sell)
        """
        self.symbol = symbol
        self.price_step_percent = price_step_percent
        self.depth_grid = depth_grid


    def place_order(self, order_side: str, price: float):
        """ Размещение лимитного ордера

            order_side (str): BUY или SELL направление ордера
            price (float): Цена размещения ордера
        """
        if order_side == 'BUY_LIMIT':
            asset_balance = CLIENT.get_asset_balance('USDT')
        if order_side == 'SELL_LIMIT':
            ticker = self.symbol.replace('USDT', '')
            asset_balance = CLIENT.get_asset_balance(ticker)

        balance_free = float(asset_balance.get('free'))
        try:
            qnty = balance_free / (self.depth_grid * 2)
            order = CLIENT.create_order(
                symbol=self.symbol,
                side=order_side,
                type='LIMIT',
                timeInForce='GTC',
                quantity=qnty,
                price=price
            )
            df_order = pd.DataFrame(order)
            df_order = df_order.rename(columns={
                'orderId': 'order_id',
                'clientOrderId': 'client_order_id',
                'origQty': 'orig_qty',
                'executedQty': 'executed_qty',
                'cummulativeQuoteQty': 'cummulative_quote_qty',
                'timeInForce': 'time_in_force',
                'isWorking': 'is_working'
            })
            df_order.time = pd.Series(pd.to_datetime(df_order.time, unit='ms', utc=True))\
                .dt.strftime('%Y-%m-%d %H:%M:%S')
            df_order.price = round(df_order.price.astype(float), round_list[f'{self.symbol}'])
            df_order.orig_qty = df_order.orig_qty.astype(float)
            df_order.execute_qty = df_order.execute_qty.astype(float)
            df_order.to_sql(name='orders', con=ENGINE, if_exists='append', index=False)
        except bae:
            message = 'Для размещения ордера недостаточно средств'
            print(message)
            send_message(message)
        except KeyError:
            pass


    def create_grid(self, start_price: float):
        """ Создание сетки лимитных ордеров

            start_price (float): Стартовая цена, эпицентр сетки, 
                                от которой будет отталкиваться диапазон price_step_percent
        """
        buy_list = []
        sell_list = []

        for i in range(self.depth_grid):
            buy_price = float(start_price * (1 - self.price_step_percent/100 * (i+1)))
            buy_list.append(buy_price)
            if not DEBUG:
                self.place_order('BUY_LIMIT', buy_price)
            else:
                print(f'{self.symbol} BUY LIMIT {buy_price}')

        for i in range(self.depth_grid):
            sell_price = float(start_price * (1 + self.price_step_percent/100 * (i+1)))
            sell_list.append(sell_price)
            if not DEBUG:
                self.place_order('SELL_LIMIT', sell_price)
            else:
                print(f'{self.symbol} SELL LIMIT {sell_price}')

        message = f'BUY: {[buy for buy in buy_list]} \n SELL: {[sell for sell in sell_list]}'
        send_message(message)        


    def create_frame(self, stream):
        """ Обработка и сохранение в базу данных текущей рыночной информации
        """
        try:
            df = pd.DataFrame([stream])
            df = df.loc[:,['s', 'E', 'b', 'a']]
            df.columns = ['symbol', 'time', 'bid', 'ask']
            df.time = pd.Series(pd.to_datetime(df.time, unit='ms', utc=True)).dt.strftime('%Y-%m-%d %H:%M:%S')
            for column in ['bid', 'ask']:
                df[column] = round(df[column].astype(float), round_list[f'{self.symbol}'])
            df.to_sql(name='market_stream', con=ENGINE, if_exists='append', index=False)
        except KeyError:
            pass


    async def socket_stream(self):
        """ Подключение к вебсокетам биржи Binance
        """
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
                