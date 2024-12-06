import mysql.connector
from dotenv import load_dotenv

import os

load_dotenv()

local_DB_KEY = os.getenv('local_DB_KEY')

# insert ticker
trades = [('NVDA', 0), ('AAPL', 0), ('MSFT', 0)]


conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='Trades',
    user='root',
    password=local_DB_KEY,
)


for ticker in trades:

    update_query = """UPDATE Ticker SET holding = %s, price = %s WHERE ticker = %s;"""
    values = (0, ticker[1], ticker[0])

    cur = conn.cursor(dictionary=True)
    cur.execute(update_query, values)
    conn.commit()
    cur.close()