from tradelab.strategy import Strategy

class my_strat_1(Strategy):
    def __init__(self, data_iterator, broker, indicators = None):
        super().__init__(data_iterator, broker)
        self.indicators = indicators
        self.CumulateOrders = False
        self.TradeIntraday = True
        self.step = 0
        self.data_iterator.change_increment('5min')
        for _ in range(3):
            self.data_iterator.next()
        
    def entry_conditions(self):
        self.current_increment = '5min'
        if self.step == 0:
            if (self.close('5min', 0) > self.open('5min', 0)) and (self.close('5min', 1) > self.open('5min', 1)):
                self.step = 1
                self.current_increment = '1sec'
        elif self.step == 1:
            if self.open('5min', 0) < self.indicators['mav'].data['5min'].loc[self.data_iterator.current_indices['5min'], 'mav']:
                self.current_increment = '5min'
                self.step = 0 
            else:
                self.buy(self.close('5min', 0))

    def exit_conditions(self):
        for _, trade in self.broker.open_trades.iterrows():
            self.current_increment = '1sec'
            if trade['profit'] > 10:
                self.sell(self.close('1sec', 0), trade_id=trade['id'])
                self.current_increment = '5min'
                self.step = 0

            if trade['profit'] < -10:
                self.sell(self.close('1sec', 0), trade_id=trade['id'])
                self.current_increment = '5min'
                self.step = 0