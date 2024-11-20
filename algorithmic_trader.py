import pandas as pd
import numpy as np

from ticker_alert import Ticker 


class AlgorithmicTrader(Ticker):
    def __init__(self, ticker: pd.DataFrame):
        
        self.data = ticker.data


    def calculate_indicators(self, RSI_period_main: int, RSI_period_short: int, RSI_period_long: int, MFI_period: int, BB_period: int, BB_smoothing: str, KC_period: int, CH_period: int, ATR_multiplier: float,
                             MACD_short: int, MACD_long: int, MACD_signal: int, MACD_smoothing: str, DI_period: int, ADX_smoothing: int):
        
        self.data['RSI_main'] = self.calculate_rsi(RSI_period_main)
        self.data['RSI_short'] = self.calculate_rsi(RSI_period_short)
        self.data['RSI_long'] = self.calculate_rsi(RSI_period_long)
        self.data['MFI'] = self.calculate_MFI(MFI_period)

        self.data['ema_50'] = self.data.Close.ewm(span=50, adjust=False).mean()
        
        MA_bollinger, BB_upper, BB_lower, BBW = self.calculate_bollinger_bands(BB_period, BB_smoothing)
        self.data['MA_bollinger'] = MA_bollinger
        self.data['BB_upper'] = BB_upper
        self.data['BB_lower'] = BB_lower
        self.data['BBW'] = BBW

        KC_upper, KC_lower = self.calculate_KC(KC_period)
        self.data['KC_upper'] = KC_upper
        self.data['KC_lower'] = KC_lower

        MACD, _, MACD_histogram = self.calculate_MACD(MACD_short, MACD_long, MACD_signal, MACD_smoothing)
        self.data['MACD'] = MACD
        self.data['MACD_histogram'] = MACD_histogram

        ADX, trend_direction = self.calculate_adx(DI_period, ADX_smoothing)
        self.data['ADX'] = ADX
        self.data['trend_direction'] = trend_direction

        self.data['chandelier_long'] = self.chandelier_exit_long(CH_period, ATR_multiplier)


    def trading_signal(self, entry_indicators_side: list, entry_indicators_trend: list, exit_indicators: list, BBW_lag: int, BBW_tresh: float, ADX_tresh: int, RSI_tresh: int, MFI_tresh: int, stopp_loss_n: int, rrr: float):
        stop_rrrs = []
        stop_losses = []
        entry_signal = []
        entry_market = []
        exit_signal = []
        candle_size = abs(self.data.Close - self.data.Open).mean()
        
        for i in range(len(self.data)):
           
            if (pd.isna(self.data.BB_upper.iloc[i]) or 
                pd.isna(self.data.KC_upper.iloc[i]) or 
                pd.isna(self.data.MFI.iloc[i]) or 
                pd.isna(self.data.RSI_long.iloc[i]) or 
                pd.isna(self.data.MACD.iloc[i]) or 
                pd.isna(self.data.ADX.iloc[i]) or 
                pd.isna(self.data.chandelier_long.iloc[i])):
                entry_signal.append(np.nan)
                entry_market.append(np.nan)

            # ENTRY
            # sideway market
            elif self.data.BB_upper.iloc[i] < self.data.KC_upper.iloc[i] and self.data.BB_lower.iloc[i] > self.data.KC_lower.iloc[i]:
                BBW_increase = (self.data.BBW.iloc[i] - self.data.BBW.shift(BBW_lag).iloc[i]) / self.data.BBW.shift(BBW_lag).iloc[i]
                BBW_trend = BBW_increase > BBW_tresh
                MFI_breakout = self.data.MFI.shift(1).iloc[i] < MFI_tresh and self.data.MFI.iloc[i] > MFI_tresh
                MFI_breakout_y = self.data.MFI.shift(2).iloc[i] < 50 and self.data.MFI.shift(1).iloc[i] > 50
                Candle_BB_breakout = self.data.Close.iloc[i] > self.data.BB_upper.iloc[i]
                Bullish_candle = (self.data.Close.iloc[i] > self.data.Open.iloc[i]) and (abs(self.data.Close.iloc[i] > self.data.Open.iloc[i]) >= candle_size)

                if 'MFI_breakout' not in entry_indicators_side and 'MFI_breakout_y' not in entry_indicators_side:
                    MFI_breakout = True

                if 'BBW_trend' not in entry_indicators_side:
                    BBW_trend = True

                if 'Candle_BB_breakout' not in entry_indicators_side:
                    Candle_BB_breakout = True

                if 'Bullish_candle' not in entry_indicators_side:
                    Bullish_candle = True

                # relaxed MFI crossover condition
                if MFI_breakout_y in entry_indicators_side:
                    MFI_brkt = MFI_breakout == True or MFI_breakout_y == True
                else:
                    MFI_brkt = MFI_breakout == True


                # signal conditions
                if BBW_trend == True and MFI_brkt == True and Candle_BB_breakout == True and Bullish_candle == True:
                    entry_signal.append(1)
                    entry_market.append('sideway')

                else:
                    entry_signal.append(0)
                    entry_market.append(np.nan)

            # trending market
            else:
                ADX_crossover = (self.data.ADX.shift(1).iloc[i] < ADX_tresh and self.data.ADX.iloc[i] > ADX_tresh) and (self.data.trend_direction.iloc[i] == 1)
                ADX_crossover_y = (self.data.ADX.shift(2).iloc[i] < ADX_tresh and self.data.ADX.shift(1).iloc[i] > ADX_tresh) and (self.data.trend_direction.shift(1).iloc[i] == 1)
                ADX_trending = (self.data.ADX.iloc[i] > ADX_tresh and self.data.trend_direction.iloc[i] == 1)
                MACD_crossover = self.data.MACD_histogram.shift(1).iloc[i] < 0 and self.data.MACD_histogram.iloc[i] > 0 
                MACD_crossover_y = self.data.MACD_histogram.shift(2).iloc[i] < 0 and self.data.MACD_histogram.shift(1).iloc[i] > 0
                MACD_zero_crossover = self.data.MACD.shift(1).iloc[i] < 0 and self.data.MACD.iloc[i] > 0
                MACD_zero_crossover_y = self.data.MACD.shift(2).iloc[i] < 0 and self.data.MACD.shift(1).iloc[i] > 0
                RSI_breakout = self.data.RSI_main.iloc[i] < RSI_tresh
                RSI_breakout_y = self.data.RSI_main.shift(1).iloc[i] < RSI_tresh
                RSI_crossover = ((self.data.RSI_main.shift(1).iloc[i] < self.data.RSI_long.shift(1).iloc[i]) and
                                 (self.data.RSI_main.iloc[i] > self.data.RSI_long.iloc[i]) and
                                 (self.data.RSI_short.iloc[i] > self.data.RSI_main.iloc[i] and self.data.RSI_short.iloc[i] > self.data.RSI_long.iloc[i]) and
                                 (self.data.RSI_short.iloc[i] > 50 and self.data.RSI_main.iloc[i] > 50 and self.data.RSI_long.iloc[i] > 50))
                RSI_crossover_y = ((self.data.RSI_main.shift(2).iloc[i] < self.data.RSI_long.shift(2).iloc[i]) and
                                   (self.data.RSI_main.shift(1).iloc[i] > self.data.RSI_long.shift(1).iloc[i]) and
                                   (self.data.RSI_short.shift(1).iloc[i] > self.data.RSI_main.shift(1).iloc[i] and self.data.RSI_short.shift(1).iloc[i] > self.data.RSI_long.shift(1).iloc[i]) and
                                   (self.data.RSI_short.shift(1).iloc[i] > 50 and self.data.RSI_main.shift(1).iloc[i] > 50 and self.data.RSI_long.shift(1).iloc[i] > 50))
                EMA_50_breakout = (self.data.Close.shift(1).iloc[i] < self.data.ema_50.iloc[i]) and (self.data.Close.iloc[i] > self.data.ema_50.iloc[i])
                MFI_breakout = self.data.MFI.iloc[i] < MFI_tresh
                Candle_BB_breakout = self.data.Low.iloc[i] < self.data.BB_lower.iloc[i]
                Bullish_candle = (self.data.Close.iloc[i] > self.data.Open.iloc[i]) and (abs(self.data.Close.iloc[i] - self.data.Open.iloc[i]) >= candle_size)

                if 'ADX_crossover' not in entry_indicators_trend and 'ADX_crossover_y' not in entry_indicators_trend:
                    ADX_crossover = True

                if 'MACD_crossover' not in entry_indicators_trend and 'MACD_crossover_y' not in entry_indicators_trend:
                    MACD_crossover = True

                if 'MACD_zero_crossover' not in entry_indicators_trend and 'MACD_zero_crossover_y' not in entry_indicators_trend:
                    MACD_zero_crossover = True

                if 'RSI_breakout' not in entry_indicators_trend and 'RSI_breakout_y' not in entry_indicators_trend:
                    RSI_breakout = True

                if 'RSI_crossover' not in entry_indicators_trend and 'RSI_crossover_y' not in entry_indicators_trend:
                    RSI_crossover = True

                if 'MFI_breakout' not in entry_indicators_trend:
                    MFI_breakout = True

                if 'EMA_50_breakout' not in entry_indicators_trend:
                    EMA_50_breakout = True

                if 'ADX_trending' not in entry_indicators_trend:
                    ADX_trending = True

                if 'Candle_BB_breakout' not in entry_indicators_trend:
                    Candle_BB_breakout = True

                if 'Bullish_candle' not in entry_indicators_trend:
                    Bullish_candle = True

                # relaxed ADX crossover condition
                if ADX_crossover_y in entry_indicators_trend:
                    ADX_crssvr = ADX_crossover == True or ADX_crossover_y == True
                else:
                    ADX_crssvr = ADX_crossover == True


                # relaxed MACD crossover condition
                if MACD_crossover_y in entry_indicators_trend:
                    MACD_crssvr = MACD_crossover == True or MACD_crossover_y == True
                else:
                    MACD_crssvr = MACD_crossover == True


                # relaxed MACD zero crossover condition
                if MACD_zero_crossover_y in entry_indicators_trend:
                    MACD_zero_crssvr = MACD_zero_crossover == True or MACD_zero_crossover_y == True
                else:
                    MACD_zero_crssvr = MACD_zero_crossover == True


                # relaxed RSI condition
                if RSI_breakout_y in entry_indicators_trend:
                    RSI_brkt = RSI_breakout == True or RSI_breakout_y == True
                else:
                    RSI_brkt = RSI_breakout == True


                # relaxed RSI crossover condition
                if RSI_crossover_y in entry_indicators_trend:
                    RSI_crssvr = RSI_crossover == True or RSI_crossover_y == True
                else:
                    RSI_crssvr = RSI_crossover == True


                # signal conditions
                if (ADX_crssvr == True and MACD_crssvr == True and MACD_zero_crssvr == True and RSI_brkt == True and RSI_crssvr == True and
                    MFI_breakout == True and Candle_BB_breakout == True and Bullish_candle == True and EMA_50_breakout == True and ADX_trending == True):
                    entry_signal.append(1)
                    entry_market.append('trending')

                else:
                    entry_signal.append(0)
                    entry_market.append(np.nan)


            # EXIT
            if pd.isna(self.data.MA_bollinger.iloc[i]):
                exit_signal.append(np.nan)
                stop_losses.append(np.nan)
                stop_rrrs.append(np.nan)

            else:
                stop_loss = self.data.Low.iloc[i-stopp_loss_n: i+1].min() - 0.5
                BB_exit = (self.data.Close.shift(1).iloc[i] > self.data.MA_bollinger.iloc[i]) and (self.data.Close.iloc[i] < self.data.MA_bollinger.iloc[i])
                CH_exit = (self.data.Close.shift(1).iloc[i] > self.data.chandelier_long.iloc[i]) and (self.data.Close.iloc[i] < self.data.chandelier_long.iloc[i])
                MACD_exit = self.data.MACD_histogram.shift(1).iloc[i] > 0 and self.data.MACD_histogram.iloc[i] < 0 

                loss = self.data.Close.iloc[i] - stop_loss
                gain = loss * rrr
                stop_rrr = self.data.Close.iloc[i] + gain
                stop_rrrs.append(stop_rrr)
                stop_losses.append(stop_loss)
                    
                if 'BB_exit' in exit_indicators and BB_exit == True:
                    exit_signal.append(1)

                elif 'CH_exit' in exit_indicators and CH_exit == True:
                    exit_signal.append(1)

                elif 'MACD_exit' in exit_indicators and MACD_exit == True:
                    exit_signal.append(1)

                else:
                    exit_signal.append(0)

        self.data['entry_signal'] = entry_signal
        self.data['entry_market'] = entry_market
        self.data['exit_signal'] = exit_signal
        self.data['stop_loss'] = stop_losses
        self.data['stop_rrr'] = stop_rrrs


    def backtesting(self):

        BUY_price = []
        BUY_date = []
        BUY_market = []
        SELL_price = []
        SELL_reason = []
        SELL_date = []
        prices = []
        reasons = []
        dates = []
        stop_loss = 0
        hold = False
        rrr_sell = False



        for i in range(len(self.data)-1):

            # if data is incomplete (~ first 30 days of time series)
            if pd.isna(self.data.entry_signal.iloc[i]):
                continue

            # not holding position
            if hold == False:
                if self.data.entry_signal.iloc[i] == 1:
                    # set stop loss 
                    stop_loss = self.data.stop_loss.iloc[i]
                    stop_rrr = self.data.stop_rrr.iloc[i]
                    # buy at next days open price
                    BUY_price.append(self.data.Open.shift(-1).iloc[i])
                    BUY_date.append(self.data.Date.shift(-1).iloc[i].strftime('%Y-%m-%d'))
                    BUY_market.append(self.data.entry_market.iloc[i])
                    buy_price = self.data.Open.shift(-1).iloc[i]
                    hold = True
                    price = []
                    reason = []
                    date = []

                    
            # holding position
            else:

                # sell due to signal
                if self.data.exit_signal.iloc[i] == 1:
                    # sell at next days open price
                    prices.append(self.data.Open.shift(-1).iloc[i])
                    reasons.append('signal')
                    dates.append(self.data.Date.shift(-1).iloc[i].strftime('%Y-%m-%d'))

                    SELL_price.append(prices)
                    SELL_reason.append(reasons)
                    SELL_date.append(dates)
                    hold = False
                    price = []
                    reason = []
                    date = []

                # sell due to stop loss
                elif self.data.Close.iloc[i] < stop_loss:
                    # sell at next days open price
                    prices.append(self.data.Open.shift(-1).iloc[i])
                    reasons.append('stop_loss')
                    dates.append(self.data.Date.shift(-1).iloc[i].strftime('%Y-%m-%d'))

                    SELL_price.append(prices)
                    SELL_reason.append(reasons)
                    SELL_date.append(dates)
                    hold = False

                # sell proportion due to risk revard ratio
                elif self.data.Close.iloc[i] > stop_rrr and rrr_sell == False:
                    # sell at next days open price
                    price.append(self.data.Open.shift(-1).iloc[i])
                    reason.append('stop_rrr')
                    date.append(self.data.Date.shift(-1).iloc[i].strftime('%Y-%m-%d'))
                    rrr_sell = True
                    stop_loss = buy_price



        if (len(BUY_price) - len(SELL_price)) == 1:
            SELL_price.append([np.nan])
            SELL_reason.append(['holding'])
            SELL_date.append([np.nan])

        self.BUY_price = BUY_price
        self.BUY_market = BUY_market
        self.BUY_date = BUY_date
        self.SELL_price = SELL_price
        self.SELL_reason = SELL_reason
        self.SELL_date = SELL_date



    def calculate_performance(self, investment, ratio: float, investment_type: str = None): 

        investment_value = investment
        investment_returns = 0
        
        if len(self.SELL_price) == 0:
            investment_returns = np.nan

        else:
            for i in range(len(self.BUY_price)):

                # check if rrr stop was triggered 
                if 'stop_rrr' in self.SELL_reason[i]:
                    n_positions =  np.floor(investment_value / self.BUY_price[i])
                    n_positions_rrr = np.floor(n_positions * ratio)
                    n_positions = n_positions - n_positions_rrr
                    returns = ((self.SELL_price[i][0] - self.BUY_price[i]) * n_positions_rrr ) + ((self.SELL_price[i][1] - self.BUY_price[i]) * n_positions)

                # if rrr stop was not triggered
                else:
                    n_positions =  np.floor(investment_value / self.BUY_price[i])
                    returns = (self.SELL_price[i][0] - self.BUY_price[i]) * n_positions

                # if investment is capped to certain amount
                if investment_type == 'capped':
                    if (investment_value + returns) <= investment and not np.isnan(returns):
                        investment_value += returns

                if not np.isnan(returns):
                    investment_returns += returns

        self.investment_value = investment_value
        self.investment_returns = investment_returns