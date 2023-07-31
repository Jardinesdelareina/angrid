DROP DATABASE IF EXISTS angrid;
CREATE DATABASE angrid;

/* Поток рыночных данных */
CREATE TABLE IF NOT EXISTS market_stream
(
    symbol VARCHAR(10) NOT NULL,
    time DATETIME UNIQUE NOT NULL,
    price FLOAT NOT NULL
);

/* 
Лимитный ордер:
symbol - символ торговой пары,
order_id - идентификатор ордера,
client_order_id - пользовательский идентификатор ордера,
price - цена ордера,
orig_qty - начальное количество актива,
executed_qty - количество актива, которое уже исполнено,
cummulative_quote_qty - суммарное количество котируемой валюты,
status - статус ордера,
    Возможные статусы лимитных ордеров:
        NEW: Ордер создан и ожидает выполнения
        PARTIALLY_FILLED: Ордер частично выполнен
        FILLED: Ордер полностью выполнен
        CANCELED: Ордер отменен пользователем
        PENDING_CANCEL: Ордер находится в процессе отмены
        REJECTED: Ордер отклонен
        EXPIRED: Ордер истек (не был выполнен в определенный срок)
time_in_force - тип срока действия ордера, по-умолчанию "GTC" (Good Till Cancelled),
type - тип ордера, по-умолчанию "LIMIT" (лимитный),
side - направление ордера, "BUY" (покупка) или "SELL" (продажа),
time - время создания ордера,
is_working - флаг, указывающий, активен ли ордер
*/
CREATE TABLE IF NOT EXISTS orders
(
    symbol VARCHAR(10) NOT NULL,
    order_id INT UNIQUE NOT NULL,
    client_order_id VARCHAR(100) UNIQUE NOT NULL,
    price FLOAT NOT NULL,
    orig_qty FLOAT NOT NULL,
    executed_qty FLOAT NOT NULL,
    cummulative_quote_qty FLOAT NOT NULL,
    status VARCHAR CHECK (status IN (
        'NEW', 
        'PARTIALLY_FILLED',
        'FILLED',
        'CANCELED',
        'PENDING_CANCEL',
        'REJECTED',
        'EXPIRED'
    )),
    time_in_force VARCHAR(3) DEFAULT 'GTC',
    type VARCHAR(5) DEFAULT 'LIMIT',
    side VARCHAR CHECK (side IN ('BUY', 'SELL')),
    time DATETIME UNIQUE NOT NULL,
    is_working BOLL NOT NULL
) 