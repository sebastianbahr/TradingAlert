import mysql.connector
from dotenv import load_dotenv

import os

load_dotenv()

local_DB_KEY = os.getenv('local_DB_KEY')


tickers = ['NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOG', 'META', 'AVGO', 'TSLA', 'LLY', 'BRK-A',
           'WMT', 'JPM', 'V', 'XOM', 'UNH', 'ORCL', 'MA', 'HD', 'COST', 'PG',
           'JNJ', 'ABBV', 'NFLX', 'BAC', 'CRM', 'KO', 'CVX', 'TMUS', 'MRK', 'PEP',
           'AMD', 'CSCO', 'LIN', 'ACN', 'TMO', 'ADBE', 'WFC', 'MCD', 'BX', 'PM',
           'ABT', 'NOW', 'AXP', 'IBM', 'MS', 'GE', 'CAT', 'QCOM', 'TXN', 'ISRG',
           'DHR', 'DIS', 'VZ', 'GS', 'INTU', 'AMGN', 'CMCSA', 'BKNG', 'NEE', 'PFE',
           'RTX', 'T', 'UBER', 'AMAT', 'LOW', 'SPGI', 'BLK', 'UNP', 'SYK', 'HON',
           'ETN', 'SCHW', 'LMT', 'VRTX', 'TJX', 'ANET', 'BSX', 'COP', 'KKR', 'C',
           'PANW', 'ADP', 'MU', 'NKE', 'FI', 'MDT', 'UPS', 'PLTR', 'BMY', 'BA',
           'SO', 'CB', 'SBUX', 'DE', 'MMC', 'ADI', 'PLD', 'INTC', 'AMT', 'LRCX',
           'GILD', 'ELV', 'SHW', 'DELL', 'HCA', 'MDLZ', 'MO', 'ICE', 'KLAC', 'REGN',
           'CI', 'DUK', 'TT', 'EQIX', 'ABNB', 'GEV', 'WM', 'CTAS', 'WELL', 'PH',
           'APH', 'MCO', 'GD', 'CME', 'SNPS', 'CDNS', 'AON', 'PYPL', 'ZTS', 'ITW',
           'MSI', 'CL', 'CMG', 'TDG', 'PNC', 'NOC', 'USB', 'CEG', 'MAR', 'ECL',
           'CVS', 'TGT', 'EOG', 'MMM', 'BDX', 'MCK', 'APD', 'FCX', 'EMR', 'FDX',
           'J', 'RSG', 'ADSK', 'AJG', 'CHTR', 'OKE', 'DLR', 'NSC', 'GM', 'SLB',
           'ROP', 'RCL', 'HLT', 'AFL', 'TFC', 'PCAR', 'KMI', 'PSA', 'NXPI', 'GWW',
           'TRV', 'SRE', 'URI', 'FICO', 'JCI', 'MET', 'BK', 'DHI', 'CPRT', 'AMP',
           'PAYX', 'FANG', 'MNST', 'AZO', 'PSX', 'ALL', 'AEP', 'NEM', 'O', 'LHX',
           'RIVN', 'MSCI', 'KMB', 'F', 'VRSK', 'LULU', 'HPE', 'EXPE', 'WBD', 'NCLH',
           'ENPH', 'FSLR', 'DAY', 'BEPC', 'FLNC', 'HASI', 'GRMN', 'AME', 'PCG', 'DFS',
           'HES', 'PRU', 'KR', 'VLO', 'PEG', 'BKR', 'STZ', 'IT', 'TRGP', 'GLW', 'EA',
           'IR', 'CBRE', 'CTVA', 'OTIS', 'KHC', 'CTSH', 'IQV', 'A', 'GEHC', 'DAL', 'MCHP',
           'EW', 'VMC', 'EXC', 'YUM', 'ACGL', 'SYY', 'MLM', 'NUE', 'MPWR', 'RMD',
           'NESN.SW', 'ADEN.SW', 'UBSG.SW', 'NOVN.SW', 'ABBN.SW', 'SGSN.SW', 'SWON.SW',
           'SDZ.SW', 'HOLN.SW', 'ROG.SW', 'CLN.SW', 'CFR.SW', 'SIGN.SW', 'SSREY', 'LOGN.SW',
           '0A0D.IL', 'NOVNEE.SW', 'STMN.SW', 'BAER.SW', 'ZURN.SW', 'AVOLZ.XC', 'KNIN.SW',
           'GF.SW', '0Z4C.IL', 'GALDZ.XC', '0QOA.IL', 'CMBNZ.XC', 'SPSNZ.XC', 'SOON.SW',
           'SRAIL.SW',
           'AIR.PA', 'ADS.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'CBK.DE', 'SY1.DE', '0H3Q.IL',
           'CON.DE', 'DTG.DE', 'DBK.DE', 'DTE.DE', 'FME.HM', 'HNR1.DE', 'HEI.DE',
           'IFX.DE', 'MBG.DE', 'MRK.DE', 'PAH3.DE', 'RHM.DE', 'RWE.DE', 'SAP.DE', 'SIE.DE',
           'SHL.DE', 'VNA.DE', 'ZAL.DE', 'VOW3.DE']


conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='Trades',
    user='root',
    password=local_DB_KEY,
)

# create Ticker table
cur = conn.cursor(dictionary=True)
cur.execute("CREATE TABLE Ticker (ticker CHAR(255) PRIMARY KEY, holding BOOL NOT NULL, price FLOAT)")
conn.commit()
cur.close()


# Insert tickers into Ticker table
for ticker in tickers:

    insert_query = """INSERT INTO Ticker (ticker, holding, price) VALUES (%s, %s, %s);"""
    values = (ticker, False, 0.0)
    cur = conn.cursor(dictionary=True)
    cur.execute(insert_query, values)
    conn.commit()
    cur.close()


print('Ticker table successfully populated')