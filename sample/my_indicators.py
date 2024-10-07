from tradelab.indicator import ValueBasedIndicators

class mav(ValueBasedIndicators):
    def __init__(self, data_iterator):
        super().__init__(data_iterator)
        self.period = 3
        self.timeframes = ['5min']
        self.column_names = ['mav']
        self.initialize_df()

    def update(self):
        mav = (self.open('5min', 3) + self.open('5min', 2) + self.open('5min', 1))/3
        return mav, 
