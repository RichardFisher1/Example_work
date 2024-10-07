from tradelab.price_iterator import PriceIterator
from tradelab.broker import Broker
from utils.data_import import import_data


class BackTester:
    def __init__(self, market_config, strategy, indicators=None):
        date_bounds = market_config['date_range']
        time_bounds = market_config['time_range']
        market = market_config['market']
        timeframes = market_config['timeframes']
        data = import_data(date_bounds, time_bounds, market, timeframes)
        price_iterator = PriceIterator(data)
        self.back_test = _BackTester(price_iterator, strategy, indicators)
    
    def run(self):
        self.back_test.run()
        self.create_trades_attribute()

    def create_trades_attribute(self):
        self.trades = self.back_test.broker.closed_trades

class _BackTester:
    def __init__(self, price_iterator, strategy, indicators=None):
        self.price_iterator = price_iterator
        self.broker = Broker(self.price_iterator)
        self.resolutions = list(self.price_iterator.data.keys())
        self.indicators = {}
        self.instantiate_indicators(indicators)
        for indicator in self.indicators.values():
            indicator.update_indicators()

        self.strategy = strategy(self.price_iterator, self.broker, self.indicators)
        
        for indicator in self.indicators.values():
            indicator.update_indicators()

        self.strategy.next()
        self.broker.update()
        if self.price_iterator.increment != self.strategy.current_increment:
            old_length = self.price_iterator.current_indices[self.resolutions[0]]
            self.price_iterator.change_increment(self.strategy.current_increment)
            new_length = self.price_iterator.current_indices[self.resolutions[0]]
            if old_length != new_length:
                for indicator in self.indicators.values():
                    indicator.update_indicators()
                self.strategy.next()
                self.broker.update()

    def instantiate_indicators(self, indicators):
        self.indicators = {}
        for indicator_class, *params in indicators:
            if params:
                kwargs = params[0]
                instance = indicator_class(self.price_iterator, **kwargs)
            else:
                instance = indicator_class(self.price_iterator)

            self.indicators[indicator_class.__name__] = instance

    def next(self):
        if self.price_iterator.increment != self.strategy.current_increment:
            old_length = self.price_iterator.current_indices[self.resolutions[0]]
            self.price_iterator.change_increment(self.strategy.current_increment)
            new_length = self.price_iterator.current_indices[self.resolutions[0]]
            if old_length != new_length:
                for indicator in self.indicators.values():
                    indicator.update_indicators()
                self.strategy.next()
                self.broker.update()
        else:
            self.price_iterator.next()
            for indicator in self.indicators.values():
                indicator.update_indicators()
            self.strategy.next()
            self.broker.update()

    def run(self):
        while self.price_iterator.is_next():
            self.next()
            print(self.price_iterator.current_indices[self.price_iterator.resolutions[0]]/len(self.price_iterator.data[self.price_iterator.resolutions[0]]))

    