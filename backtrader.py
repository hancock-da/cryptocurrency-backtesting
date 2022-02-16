import backtrader
import backtrader.feeds as btfeeds
from strategies import CandleStrategy, ADXStrategy, KCStrategy, RSIStrategy
import os
import pandas as pd


results = pd.DataFrame(columns=['symbol', 'final_value'])

for filename in os.listdir('datasets/1d_datasets'):   
    data = btfeeds.GenericCSVData(
        dataname='datasets/1d_datasets/{}'.format(filename),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
        , dtformat = '%Y-%m-%d')
        #,fromdate=datetime.datetime(2020, 1, 20))

    cerebro = backtrader.Cerebro()

    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.00025)
    
    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.adddata(data)
    cerebro.addsizer(backtrader.sizers.PercentSizer, percents=10)
    #cerebro.addsizer(backtrader.sizers.FixedSize, stake=1)

    cerebro.addstrategy(CandleStrategy, fastsma=15, slowsma=50, tp_mult=3, printlog=False)
    
    # if __name__ == '__main__':
    #     strats = cerebro.optstrategy(
    #         CandleStrategy,
    #         fastsma=[7,9,15],
    #         slowsma=[20,50,99],
    #         tp_mult=[2,3],
    #         printlog=False)
                
    cerebro.run(runonce=False)

    symbol = filename.replace('.csv','')
    
    final_val = cerebro.broker.getvalue()


    #print('Final Portfolio Value for {}: %.2f'.format(symbol) % final_val)

    if final_val != 1000000:
        to_append = [symbol,cerebro.broker.getvalue()]
        a_series = pd.Series(to_append, index=results.columns)
        results = results.append(a_series, ignore_index=True)

    #cerebro.plot()

stats = print('{} successes out of {} with an average return of {}'.format((results.final_value > 1000000).sum(), results.final_value.count(),results.final_value.mean()))

#results.to_csv('backtesting/results/three_line_1d.csv')