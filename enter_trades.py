import mysql.connector
from dotenv import load_dotenv

import os

load_dotenv()

local_DB_KEY = os.getenv('local_DB_KEY')

# insert ticker and entry price
trades = [('NVDA', 140), ('AAPL', 222), ('MSFT', 415)]


conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='Trades',
    user='root',
    password=local_DB_KEY,
)


for ticker in trades:

    update_query = """UPDATE Ticker SET holding = %s, price = %s WHERE ticker = %s;"""
    values = (1, ticker[1], ticker[0])

    cur = conn.cursor(dictionary=True)
    cur.execute(update_query, values)
    conn.commit()
    cur.close()