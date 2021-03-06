

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

import backtrader as bt

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

         # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

          # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

        # 获取股票的收盘价

    # close_data = get_bars(security, count=5, unit='1d', fields=['close'])
    # # 取得过去五天的平均价格
    # MA5 = close_data['close'].mean()
    # # 取得上一时间点价格
    # current_price = close_data['close'][-1]
    # # 取得当前的现金
    # cash = context.portfolio.available_cash
    #
    # # 如果上一时间点价格高出五天平均价1%, 则全仓买入
    # if (current_price > 1.01 * MA5) and (cash > 0):
    #     # 记录这次买入
    #     log.info("价格高于均价 1%%, 买入 %s" % (security))
    #     print("当前可用资金为{0}, position_value为{0}".format(cash, context.portfolio.positions_value))
    #     # 用所有 cash 买入股票
    #     order_value(security, cash)
    # # 如果上一时间点价格低于五天平均价, 则空仓卖出
    # elif current_price < MA5 and context.portfolio.positions[security].closeable_amount > 0:
    #     # 记录这次卖出
    #     log.info("价格低于均价, 卖出 %s" % (security))
    #     # 卖出所有股票,使这只股票的最终持有量为0
    #     order_target(security, 0)




    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, '../datas/orcl-1995-2014.txt')
    datapath = os.path.join(modpath, '../datas_hk/hk00001.csv')

    # Create a Data Feed
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname=datapath,
    #     # Do not pass values before this date
    #     fromdate=datetime.datetime(2000, 1, 1),
    #     # Do not pass values after this date
    #     todate=datetime.datetime(2000, 12, 31),
    #     reverse=False)

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat='%Y-%m-%d',
        datetime=1,
        open=2,
        high=3,
        low=4,
        close=5,
        volumn=6,
        volumnAmount=7,
        # Do not pass values before this date
        fromdate=datetime.datetime(2019, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2019, 12, 31),
        reverse=False
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    # cerebro.plot()


