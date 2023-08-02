import asyncio
from concurrent.futures import ThreadPoolExecutor
from core import Angrid
from utils import symbol_list


def start_single_bot(symbol):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(Angrid(symbol).socket_stream())


def start_all_bots():
    bots = [Angrid(symbol) for symbol in symbol_list]
    with ThreadPoolExecutor() as executor:
        return executor.map(asyncio.run, [bot.socket_stream() for bot in bots])


start_single_bot('XRPUSDT')
#start_all_bots()
