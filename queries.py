# Последняя котировка
current_price = "SELECT price FROM market_stream ORDER BY time DESC LIMIT 1"

# Первая котировка, инициализирующая сетку при старте алгоритма
start_process = "SELECT price FROM market_stream LIMIT 1"

# Получение статуса ордеров
order_status = "SELECT status FROM orders"

# Ближайший к текущей цене лимитный ордер на покупку
order_buy_price = f"SELECT price FROM orders WHERE side = 'BUY' ORDER BY ABS(price - {current_price})"

# Ближайший к текущей цене лимитный ордер на продажу
order_sell_price = f"SELECT price FROM orders WHERE side = 'SELL' ORDER BY ABS(price - {current_price})"

open_orders = "SELECT order_id FROM orders WHERE status = 'NEW'"
