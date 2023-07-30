# Последняя котировка
current_price = "SELECT bid FROM market_stream ORDER BY time DESC LIMIT 1"

# Первая котировка, инициализирующая сетку при старте алгоритма
start_process = "SELECT bid FROM market_stream LIMIT 1"

# Ближайший к текущей цене лимитный ордер на покупку
order_buy_price = f"SELECT price from orders WHERE side = 'BUY' ORDER BY ABS(price - {current_price})"

# Ближайший к текущей цене лимитный ордер на продажу
order_sell_price = f"SELECT price from orders WHERE side = 'SELL' ORDER BY ABS(price - {current_price})"

# Удаление данных из таблицы
drop_data = "DELETE FROM orders"