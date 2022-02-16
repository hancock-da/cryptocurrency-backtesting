import datetime
from binance import Client
import pandas as pd
import config

client = Client(config.API_KEY, config.API_SECRET)
today =  datetime.date.today().strftime('%d %b %Y')

prices = client.get_all_tickers()

symbols = []
for price in prices:
    if 'USDT' in price['symbol'][-4:]:
        symbols.append(price['symbol'])

#print(len(symbols))
        

for symbol in symbols:
    #print(symbol)
    
    data = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "1 Jan 2017",today)
    
    df = pd.DataFrame.from_records(data=data, columns=['Date','Open','High','Low','Close','Volume','Close_Time','Quote_Asset_Volume','Num_Trades',
                                                    'Taker_Buy_Base_Vol','Taker_Buy_Quote_Vol','Ignore'])
    
    df = df.iloc[:,0:6]
    df['Date'] = pd.to_datetime(df['Date'],unit='ms')
    
    try:
        df.to_csv('datasets/1d_datasets/{}.csv'.format(symbol), index=False)
    except:
        print("There was an error with {}".format(symbol))