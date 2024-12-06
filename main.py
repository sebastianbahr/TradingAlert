import pandas as pd
import mysql.connector
from dotenv import load_dotenv

import os

from ticker_alert import Ticker
from algorithmic_trader import AlgorithmicTrader
from email_sender import EmailSender

load_dotenv()

local_DB_KEY = os.getenv('local_DB_KEY')
sender = os.getenv('EMAIL_SENDER')
receiver = os.getenv('EMAIL_RECEIVER')
email_pw = os.getenv('EMAIL_APP_PASSWORD')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465



entry_strategies = {'strategy_1': ['Bullish_candle', 'Candle_BB_breakout', 'RSI_breakout_y'],
                    'strategy_7': ['Bullish_candle', 'RSI_crossover_y', 'EMA_50_breakout', 'ADX_trending'],
                    'strategy_8': ['RSI_breakout'],}
exit_strategy = ['BB_exit']

forecast = 5
RSI_period_main = 13
RSI_period_short = 5
RSI_period_long = 50
RSI_tresh = 25
MFI_period = 13
BB_period = 20
BB_smoothing = 'SMA'
KC_period = 20
CH_period = 22
ATR_multiplier = 3
MACD_short = 3 
MACD_long = 10 
MACD_signal = 16 
MACD_smoothing = 'EMA'
DI_period = 14
ADX_period = 14
ADX_tresh = 30
rrr = 2.0



def retrieve_status(data: list, status: bool, conn):
    if len(data) > 0:
        if len(data) == 1:
            tickers = data[0].get('ticker')
            values = f"('{tickers}')"

        else:
            tickers = [x.get('ticker') for x in data]
            values = tuple(tickers)
        
        query = f"SELECT * FROM Ticker WHERE ticker IN {values};"
        cur = conn.cursor(dictionary=True)
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        df = pd.DataFrame(data).merge(pd.DataFrame(result, columns=['ticker', 'holding', 'price']), on='ticker', how='inner')
        df = df[df.holding==status]
        
        # If exit calcualte approximate gain per share
        if status == 1:
            df['approx_gain_ps'] = df.close - df.price

    else:
        df = pd.DataFrame()

    return df


def main():
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


    entries = []
    exits = []

    # connect to MySQL DB
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='Trades',
        user='root',
        password=local_DB_KEY,
    )

    # check tickers for entry or exit signal based on selected strategies
    for ticker in tickers:

        # retrieve ticker data and clean it
        ticker_data = Ticker(ticker, 3, '6mo')
        ticker_data.generate_triangle(0)

        # calculate trading indicators
        indicators = AlgorithmicTrader(ticker_data)
        indicators.calculate_indicators(RSI_period_main, RSI_period_short, RSI_period_long, MFI_period, BB_period, BB_smoothing, KC_period, CH_period,
                                        ATR_multiplier, MACD_short, MACD_long, MACD_signal, MACD_smoothing, DI_period, ADX_period)


        for entry_strategy in list(entry_strategies.values()):
        # check for trading signals based on selected strategy
            indicators.trading_signal(['BBW_trend', 'Bullish_candle', 'Candle_BB_breakout', 'MFI_breakout'],
                                        entry_strategy,
                                        exit_strategy,
                                        BBW_lag=3, BBW_tresh=0.1, ADX_tresh=ADX_tresh, RSI_tresh=RSI_tresh, MFI_tresh=25, stopp_loss_n=5, rrr=rrr)
            
            if 1 in indicators.data.entry_signal.tail(1).to_list():
                data = indicators.data.iloc[-1]

                # adjust entry_strategy if entry was triggered in sideway market
                if data.entry_market == 'sideway':
                    entry_strategy = 'BBW_trend', 'Bullish_candle', 'Candle_BB_breakout', 'MFI_breakout'

                entries.append({'ticker': ticker,
                                'date': data.Date.strftime('%Y-%m-%d'),
                                'strategy': entry_strategy,
                                'open': data.Open,
                                'close': data.Close,
                                'entry_signal': data.entry_signal,
                                'entry_market': data.entry_market,
                                'stop_loss': data.stop_loss,
                                'stop_rrr': data.stop_rrr})
            
        if 1 in indicators.data.exit_signal.tail(1).to_list():
            data = indicators.data.iloc[-1]
            exits.append({'ticker': ticker,
                            'date': data.Date.strftime('%Y-%m-%d'),
                            'open': data.Open,
                            'close': data.Close,
                            'exit_signal': data.exit_signal})


    # check status (0=not holding, 1=holding) of tickers if entry or exit signal was found
    entries_oi = retrieve_status(entries, 0, conn)
    exits_oi = retrieve_status(exits, 1, conn)

    # send daily trading update email
    email = EmailSender(entries_oi, exits_oi, SMTP_SERVER, SMTP_PORT, email_pw, sender, receiver)
    email.send_email()

# run script
if __name__ == "__main__":
    main()