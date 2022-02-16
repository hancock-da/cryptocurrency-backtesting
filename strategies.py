from statistics import mean
import backtrader

                             
class ADXStrategy(backtrader.Strategy):
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datavol = self.datas[0].volume
        
        self.adx = backtrader.indicators.AverageDirectionalMovementIndex(self.data, period=14)
        self.adxplus = backtrader.indicators.PlusDirectionalIndicator(self.data, period=14)
        self.adxminus = backtrader.indicators.MinusDirectionalIndicator(self.data, period=14)
        self.obv = backtrader.talib.OBV(self.dataclose, self.datavol)
        self.obv_avg = backtrader.talib.SMA(self.obv, timeperiod=100)

    def next(self):
        
        if not self.position:
            if self.obv > self.obv_avg and self.adx > 25 and self.adxplus > self.adxminus:
                print('OBV is {} and SMA_OBV is {}'.format(self.obv[0], self.obv_avg[0]))
                self.buy()

        if self.position:
            if self.adx < 25 or self.adxplus < self.adxminus or self.obv < self.obv_avg:
                self.close()

class RSIStrategy(backtrader.Strategy):
    def __init__(self):
        self.rsi = backtrader.talib.RSI(self.data, period=14)

    def next(self):
        if self.rsi > 55 and not self.position:
            self.buy()

        if self.rsi < 45 and self.position:
            self.close()

class KeltnerChannel(backtrader.Indicator):
    lines = ('mid', 'upper', 'lower')
    params = dict(
                ema=20,
                atr=2
                )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        mid=dict(ls='--'),  # dashed line
        upper=dict(_samecolor=True),  # use same color as prev line (mid)
        lower=dict(_samecolor=True),  # use same color as prev line (upper)
    )

    def __init__(self):
        self.l.mid = backtrader.ind.EMA(period=self.p.ema)
        self.l.upper = self.l.mid + backtrader.ind.ATR(period=self.p.ema) * self.p.atr
        self.l.lower = self.l.mid - backtrader.ind.ATR(period=self.p.ema) * self.p.atr
                 
class KCStrategy(backtrader.Strategy):
    params = (
        ("period", 20),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
        )
    
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries        
        self.kc = KeltnerChannel()
        self.bb = backtrader.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)

    def next(self):
        # calculate size - in this example we go all in by taking all our cash and dividing 
        # by the price of the asset to get our size
        # size = int(self.broker.getcash() / self.close[0])
        if not self.position:
            if self.bb.lines.bot[-5] > self.kc.l.lower[-5] and \
                self.bb.lines.bot[-4] > self.kc.l.lower[-4] and \
                self.bb.lines.bot[-3] > self.kc.l.lower[-3] and \
                self.bb.lines.bot[-2] > self.kc.l.lower[-2] and \
                self.bb.lines.bot[-1] > self.kc.l.lower[-1] and \
                self.bb.lines.bot[0] < self.kc.l.lower[0]:
                self.buy()
                #self.buy(size=size)
        
        elif self.position:
            if self.data[0] <= self.kc.l.mid[0]:
                self.close()
                

class CandleStrategy(backtrader.Strategy):
    
    params = (
        ('fastsma', 7),
        ('slowsma', 20),
        ('tp_mult', 2),
        ('atr_period', 14),
        ('atr_mult', 2),
        ('printlog', False)
    )
    
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint: # Add if statement to only log if printlog or doprint is True
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
            
    def __init__(self):
        # Keep a reference to the lines in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close
        
        self.threelinestrike = backtrader.talib.CDL3LINESTRIKE(self.data.open,self.data.high,self.data.low, self.data.close, penetration=0.3)
        self.fastma = backtrader.indicators.SMA(period=self.p.fastsma)
        self.slowma = backtrader.indicators.SMA(period=self.p.slowsma)
        self.atr = backtrader.indicators.ATR(period=self.p.atr_period)
        
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.log('BUY EXECUTED, Price: {}, Cost: {}, Comm: {}'.format(order.executed.price,
                                                  order.executed.value,
                                                  order.executed.comm))

            elif order.issell():
                self.log('SELL EXECUTED, Price: {}, Cost: {}, Comm: {}'.format(order.executed.price,
                                                   order.executed.value,
                                                   order.executed.comm))
            
            self.bar_executed = len(self)
        self.order=None
    
    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return
        
        if not self.position:
            if self.threelinestrike == -100 and self.fastma[0] < self.slowma[0]:
                # if candle is a three line strike
                
                self.order = self.buy()
                self.buyprice = self.dataclose[0]
                #self.stoploss = min(self.datalow[-3], self.datalow[-2], self.datalow[-1])
                if self.buyprice - self.p.atr_mult*self.atr[0] <= 0:
                    self.stoploss = self.buyprice - self.atr[0]
                else:
                    self.stoploss = self.buyprice - self.p.atr_mult*self.atr[0]
                
                self.log('BUY CREATED {}, stoploss: {}'.format(self.dataclose[0], self.stoploss))
                
        elif self.position.size > 0 and self.dataclose[0] >= (self.buyprice + self.p.tp_mult*(self.buyprice - self.stoploss)):
            self.log('PROFIT TARGET HIT - SELL CREATED {}'.format(self.dataclose[0]))
            self.order = self.close()
        elif self.position.size > 0 and self.dataclose[0] < self.stoploss: 
            self.log('STOPLOSS HIT - SELL CREATED {}'.format(self.dataclose[0]))
            self.order = self.close()
    
    def stop(self):
        self.log('fast sma: {}, slow sma: {}, take profit multiplier: {}, final portfolio value: {}'.format(
            self.params.fastsma, 
            self.params.slowsma,
            self.params.tp_mult,
            self.broker.getvalue()),
                doprint=True)
        
