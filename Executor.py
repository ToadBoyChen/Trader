import yfinance as yf
from tradingview_ta import TA_Handler, Exchange, Interval
import Executor_Funcs as ef
from datetime import datetime, timedelta
from colorama import Fore

symbol = 'TSLA'
today = datetime.now().strftime('%Y-%m-%d')
tradeDay = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
data = yf.download(symbol, start='2021-01-01', end=today, interval='1d')
dates = data.index
priceClose = data['Close'].tolist()

STM_period = 10
LTM_period = 50

threshold = ef.threshold(priceClose, 0.5)

MACDLine, signalLine, MACDHist = ef.MACD(data)

signals_Crossover = ef.strictCrossover(priceClose, dates, STM_period, LTM_period, threshold)
signals_MACD = ef.MACDSignals(dates, MACDLine, signalLine, MACDHist)

volumeFactor = ef.getVolumeConfirmation(data, tradeDay)

#ef.TRADE(tradeWeight)

ef.fullView(ef.SIMULATE(signals_Crossover, signals_MACD, data, dates), symbol, dates)

tradeWeight = ef.calcTradeWeight(signals_Crossover, signals_MACD, tradeDay, volumeFactor)
sig_cross = ef.getSignals_Crossover(signals_Crossover, tradeDay)
sig_macd = ef.getSignals_MACD(signals_MACD, tradeDay)
vol = ef.getVolumeConfirmation(data, tradeDay)

print(tradeWeight, sig_cross, sig_macd, vol)