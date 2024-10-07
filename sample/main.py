from tradelab.backtester import BackTester
from my_indicators import mav
from my_strategies import my_strat_1
from tradelab.new_gui import ChartsApp

def main():
    market_config = {
    'date_range': ('2024-08-22', '2024-09-05'),
    'time_range': ('08:00:00', '10:00:00'),
    'market': 'dax',
    'timeframes': ['1sec', '1min', '5min']
    }


    app = ChartsApp(market_config)
    app.run()

    bt = BackTester(market_config, my_strat_1, [(mav,)])
    bt.run()
    bt.trades
    
    
if __name__ == '__main__':
    main()