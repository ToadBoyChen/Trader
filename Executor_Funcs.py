import matplotlib.pyplot as plt
from colorama import Fore
import pandas as pd
import numpy as np

def MACD(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, min_periods=1, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, min_periods=1, adjust=False).mean()
    MACDLine = short_ema - long_ema
    signalLine = MACDLine.ewm(span=signal_window, min_periods=1, adjust=False).mean()
    MACDHist = MACDLine - signalLine
    return MACDLine, signalLine, MACDHist

def movingAverage(data, period):
    movingAverages = []

    for i in range(0, len(data)):
        if ((len(data)-1) % period == 0):
            window = data[i : i + period]
            currentAverage = sum(window) / period
            movingAverages.append(currentAverage)
        else:
            for x in range(1, period):
                if ((len(data)-x) % period == 0):
                    window = data[i-x : i-x + period]
                    currentAverage = sum(window) / period
                    movingAverages.append(currentAverage)
                    break
                else:
                    continue

    return movingAverages

def strictCrossover(data, dates, STM_period, LTM_period, threshold):
    # Calculate Moving Averages
    STM = movingAverage(data, STM_period)
    LTM = movingAverage(data, LTM_period)

    signals = []
    for i in range(0, len(dates)):
        price_change = (data[i] - data[i-1]) / data[i-1] if data[i-1] != 0 else 0  # Calculate percentage price change
        if STM[i-1] < LTM[i-1] and STM[i] > LTM[i] and price_change > threshold:
            signals.append((dates[i], 'buy'))  # Buy signal (STM crosses above LTM with sufficient price change)
        elif STM[i-1] > LTM[i-1] and STM[i] < LTM[i] and price_change > threshold:
            signals.append((dates[i], 'sell'))  # Sell signal (STM crosses below LTM with sufficient price change)
        else:
            signals.append((dates[i], 'hold'))  # No signal

    return signals

def MACDSignals(dates, MACDLine, signalLine, MACDHist):
    signals = []
    position = None
    for i in range(len(MACDLine)):
        # If MACD histogram is positive and MACD line crosses above signal line
        if MACDHist.iloc[i] > 0 and MACDLine.iloc[i] > signalLine.iloc[i] and MACDLine.iloc[i] > 0:
            if position != 'buy':  # If not already in 'Buy' position
                signals.append((dates[i], 'buy'))
                position = 'buy'
            else:
                signals.append((dates[i], 'hold'))
        
        # If MACD histogram is negative and MACD line crosses below signal line
        elif MACDHist.iloc[i] < 0 and MACDLine.iloc[i] < signalLine.iloc[i] and MACDLine.iloc[i] < 0:
            if position != 'sell':  # If not already in 'Sell' position
                signals.append((dates[i], 'sell'))
                position = 'sell'
            else:
                signals.append((dates[i], 'hold'))
        
        else:
            signals.append((dates[i], 'hold'))  # If no signal, hold current position
        
    return signals

def wordToInt(signals):
    converted_signals = []
    for signal in signals:
        if signal == 'buy':
            converted_signals.append(1)
        elif signal == 'sell':
            converted_signals.append(-1)
        else:
            converted_signals.append(0)
    return converted_signals

def plotSignalCrossover(dates, signals, priceClose, STM, LTM):
    _signals = []

    for i in signals:
        _signals.append(i[1])

    _signals = wordToInt(_signals)

    buy_dates = [dates[i] for i, signal in enumerate(_signals) if signal == 1]
    sell_dates = [dates[i] for i, signal in enumerate(_signals) if signal == -1]
    hold_dates = [dates[i] for i, signal in enumerate(_signals) if signal == 0]
    
    plt.figure(figsize=(12, 6))
    
    plt.scatter(buy_dates, [priceClose[i] for i, signal in enumerate(_signals) if signal == 1], color='green', label='Buy Signal', marker='^', s=35)
    plt.scatter(sell_dates, [priceClose[i] for i, signal in enumerate(_signals) if signal == -1], color='red', label='Sell Signal', marker='v', s=35)
    #plt.scatter(hold_dates, [priceClose[i] for i, signal in enumerate(_signals) if signal == 0], color='blue', label='Hold Signal', marker='o', s=5)
    
    plt.plot(dates[-len(STM):], STM, label='Short-term Moving Average (STM)')
    plt.plot(dates[-len(LTM):], LTM, label='Long-term Moving Average (LTM)')
    
    #plt.plot(dates[-len(priceClose):], priceClose, label='Close Price', color='black')  # Plot close price
    
    plt.title('Short-term vs Long-term Moving Averages with Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

def plotMACD(dates, data, MACDLine, signalLine, MACDHist, symbol, signals):
    _signals = [i[1] for i in signals]
    _signals = wordToInt(_signals)

    buy_dates = [dates[i] for i, signal in enumerate(_signals) if signal == 1]
    sell_dates = [dates[i] for i, signal in enumerate(_signals) if signal == -1]

    plt.figure(figsize=(12, 6))
    plt.plot(data.index, MACDLine, label='MACD Line', color='blue')
    plt.plot(data.index, signalLine, label='Signal Line', color='red')
    plt.bar(data.index, MACDHist, label='MACD Histogram', color='gray')
    plt.scatter(buy_dates, [-9] * len(buy_dates), color='green', label='Buy Signal', marker='^', s=20)
    plt.scatter(sell_dates, [-9] * len(sell_dates), color='red', label='Sell Signal', marker='v', s=20)
    plt.title('MACD Indicator for ' + symbol)
    plt.xlabel('Date')
    plt.ylabel('MACD')
    plt.yscale('linear')
    plt.legend()
    plt.show()
    
def plotTrade(dates, priceClose):    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, priceClose, label='Close Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Trade Day')
    plt.legend()
    plt.show()
    
def threshold(priceClose, factor):
    priceChange = np.diff(priceClose) / priceClose[:-1]
    averagePriceChange = np.mean(priceChange)
    return factor * averagePriceChange

def TRADE(action):
    if (action == 'buy'):
        return 1
    elif (action == 'sell'):
        return -1
    else:
        return action
    
def getVolumeConfirmation(data, tradeDate):
    df = pd.DataFrame(data)
    average_volume = df['Volume'].mean()
    
    todayVolume = df.loc[tradeDate, 'Volume']
    
    if todayVolume > average_volume * 1.8:
        return "very strong positive"
    elif todayVolume > average_volume * 1.6:
        return "strong positive"
    elif todayVolume > average_volume * 1.2:
        return "positive"
    elif todayVolume < average_volume * 0.8:
        return "negative"
    elif todayVolume < average_volume * 0.4:
        return "strong negative"
    elif todayVolume < average_volume * 0.2:
        return "very strong negative"
    else:
        return "average"

def calcTradeWeight(signals_Crossover, signals_MACD, tradeDay, volumeFactor):
    _tradeDayMACD = []  
    for i in range(0, len(signals_MACD)):
        tempStr = str(signals_MACD[i])
        if tempStr.__contains__(tradeDay):
            _tradeDayMACD = signals_MACD[i]         
    _tradeDayCrossover = []  
    for i in range(0, len(signals_Crossover)):
        tempStr = str(signals_Crossover[i])
        if tempStr.__contains__(tradeDay):
            _tradeDayCrossover = signals_Crossover[i]
    if volumeFactor == "positive":
        volumeFactor = 1.2
    elif volumeFactor == "strong positive":
        volumeFactor = 1.4
    elif volumeFactor == "very strong positive":
        volumeFactor = 1.5
    elif volumeFactor == "negative":
        volumeFactor = 0.8
    elif volumeFactor == "strong negative":
        volumeFactor = 0.6
    elif volumeFactor == "very strong negative":
        volumeFactor = 0.5
    else:
        volumeFactor = 1
        
    tradeWeight = 0.0
    if str(_tradeDayCrossover).__contains__("buy"):
        tradeWeight = tradeWeight + 0.5
    elif str(_tradeDayCrossover).__contains__("sell"):
        tradeWeight = tradeWeight - 0.5
    else:
        tradeWeight = tradeWeight * 0.9
        
    if str(_tradeDayMACD).__contains__("buy"):
        tradeWeight = tradeWeight + 0.5
    elif str(_tradeDayMACD).__contains__("sell"):
        tradeWeight = tradeWeight - 0.5
    else:
        tradeWeight = tradeWeight * 0.9

    return tradeWeight * volumeFactor


def removeJunk(signal):     
    return signal[1]

def SIMULATE(signals_Crossover, signals_MACD, data, dates):
    result_list = []
    for date in dates:
        tradeWeight = calcTradeWeight(signals_Crossover, signals_MACD, str(date), getVolumeConfirmation(data, str(date)))
        volumeConfirmation = getVolumeConfirmation(data, str(date))
        signals_c = getSignals_Crossover(signals_Crossover, str(date))
        signals_c = removeJunk(signals_c)
        signals_m = getSignals_MACD(signals_MACD, str(date))
        signals_m = removeJunk(signals_m)
        result_list.append((tradeWeight, volumeConfirmation, signals_c, signals_m))
        
    return result_list

def getSignals_Crossover(signals_Crossover, tradeDay):
    for i in range(0, len(signals_Crossover)):
        tempStr = str(signals_Crossover[i])
        if tempStr.__contains__(tradeDay):
            return signals_Crossover[i]
        
def getSignals_MACD(signals_MACD, tradeDay):
    for i in range(0, len(signals_MACD)):
        tempStr = str(signals_MACD[i])
        if tempStr.__contains__(tradeDay):
            return signals_MACD[i]  
            
def fullView(list, symbol, dates):
    x = 0
    
    buy_Crossover = 0
    sell_Crossover = 0
    hold_Crossover = 0
    
    buy_MACD = 0
    sell_MACD = 0
    hold_MACD = 0
    
    weakBuy = 0
    weakSell = 0
    strongBuy = 0
    strongSell = 0
    globalHold = 0
    
    positiveVol = 0
    negativeVol = 0
    
    for i in list:
        tempStr = ""
        rounded = round(i[0], 4)
        add = ""
        if len(str(rounded)) == 7:
            add = ""
        elif len(str(rounded)) == 6:
            add = " "
        elif len(str(rounded)) == 5:
            add = "  "
        elif len(str(rounded)) == 4:
            add = "   "    
        elif len(str(rounded)) == 3:
            add = "    "    
            
        if i[0] > 0.6:
            tempStr = "    " + str(dates[x]) + "|" + add + Fore.GREEN + "Weight: " + str(rounded) + Fore.RESET + "  "
            strongBuy = strongBuy + 1
        elif i[0] < -0.6:
            tempStr = "    " + str(dates[x]) + "|" + add + Fore.RED + "Weight: " + str(rounded) + Fore.RESET + "  "
            strongSell = strongSell + 1
        elif i[0] <= 0.6 and i[0] > 0.2:
            tempStr = "    " + str(dates[x]) + "|" + add + Fore.LIGHTGREEN_EX + "Weight: " + str(rounded) + Fore.RESET + "  "
            weakBuy = weakBuy + 1
        elif i[0] < -0.2 and i[0] >= -0.6:
            tempStr = "    " + str(dates[x]) + "|" + add + Fore.LIGHTRED_EX + "Weight: " + str(rounded) + Fore.RESET + "  "
            weakSell = weakSell + 1
        else:
            tempStr = "    " + str(dates[x]) + "|" + add + "Weight: " + str(i[0]) + "  "
            globalHold = globalHold + 1
        
        if i[1] == 'positive':
            tempStr = tempStr + "  "+ Fore.LIGHTGREEN_EX + "Vol: " + "   Pos" + Fore.RESET + "  "
            positiveVol = positiveVol + 1
        elif i[1] == 'negative':
            tempStr = tempStr + "  " + Fore.LIGHTRED_EX + "Vol: " + "   Neg" + Fore.RESET + "  "
            negativeVol = negativeVol + 1
        elif i[1] == 'strong positive':
            tempStr = tempStr + "  " + Fore.GREEN + "Vol: " + "+  Pos" + Fore.RESET + "  "
            positiveVol = positiveVol + 1
        elif i[1] == 'very strong positive':
            tempStr = tempStr + "  " + Fore.CYAN + "Vol: " + "++ Pos" + Fore.RESET + "  "
            positiveVol = positiveVol + 1
        elif i[1] == 'strong negative':
            tempStr = tempStr + "  " + Fore.RED + "Vol: " + "-  Neg" + Fore.RESET + "  "
            negativeVol = negativeVol + 1            
        elif i[1] == 'very strong negative':
            tempStr = tempStr + "  " + Fore.MAGENTA + "Vol: " + "-- Neg" + Fore.RESET + "  "
            negativeVol = negativeVol + 1
        else:
            tempStr = tempStr + "  " + "Vol: " + "   Ave" + "  "
        
        if i[2] == 'buy':
            tempStr = tempStr + "  "+ Fore.GREEN + "c sig: " + "B" + Fore.RESET + "  " 
            buy_Crossover = buy_Crossover + 1
        elif i[2] == 'sell':
            tempStr = tempStr + "  " + Fore.RED  + "c sig: " + "S" + Fore.RESET + "  "
            sell_Crossover = sell_Crossover + 1
        else:
            tempStr = tempStr + "  " + "c sig: " + "H" + "  "
            hold_Crossover = hold_Crossover + 1
        
        if i[3] == 'buy':
            tempStr = tempStr +  "  " + Fore.GREEN + "MACD sig: " + "B" + Fore.RESET
            buy_MACD = buy_MACD + 1
        elif i[3] == 'sell':
            tempStr = tempStr + "  " + Fore.RED + "MACD sig: " +  "S" + Fore.RESET
            sell_MACD = sell_MACD + 1
        else:
            tempStr = tempStr + "  " + "MACD sig: " + "H"
            hold_MACD = hold_MACD + 1
        
        x = x + 1
        if x%2 == 0:
            print(tempStr, end="")
        else:
            print(tempStr)
    
    print("")  
    print("===============================================")
    print("-= Statistics for ", symbol, " =-")
    print("")
    print("-----------------------------------------------")
    print("Suggested Actions")
    print("Strong buy: ", strongBuy)
    print("Weak buy: ", weakBuy)
    print("Strong sell: ", strongSell)
    print("Weak sell: ", weakSell)
    print("Hold: ", globalHold)
    print("-----------------------------------------------")
    print("")
    print("Crossover buy signals: ", buy_Crossover)
    print("Crossover sell signals: ", sell_Crossover)
    print("Crossover hold signals: ", hold_Crossover)
    print("")
    print("MACD buy signals: ", buy_MACD)
    print("MACD sell signals: ", sell_MACD)
    print("MACD hold signals: ", hold_MACD)
    print("")
    print("Volume positive: ", positiveVol)
    print("Volume negative: ", negativeVol)
    print("")  