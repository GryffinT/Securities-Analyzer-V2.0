import yfinance as yf

def calc_moving_averages(ticker, period="1y"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        sma = hist["Close"].rolling(window=200).mean()
        ema = hist["Close"].ewm(span=21, adjust=False).mean()
        return [sma.iloc[-1], ema.iloc[-1]]
    except Exception as e:
        return (f"Error, could not calculate moving averages: {e}")