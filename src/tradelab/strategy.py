
class Strategy:
    def __init__(self, data_iterator, broker):
        self.data_iterator = data_iterator
        self.broker = broker
        self.CumulateOrders = False
        self.TradeIntraday = False
        self.step = 0

    def entry_conditions(self): 
        raise NotImplementedError("Subclasses must implement entry_conditions method.")
    
    def exit_conditions(self): 
        raise NotImplementedError("Subclasses must implement exit_conditions method.")

    def intraday(self):
        if self.TradeIntraday is True:
            n_bars_in_day = self.data_iterator.data[self.data_iterator.increment]['DateTime'].dt.date.value_counts().sort_index()[0]
            end_of_day_index = n_bars_in_day * ((self.data_iterator.current_indices[self.data_iterator.increment] // n_bars_in_day) + 1) - 1
            if self.data_iterator.current_indices[self.data_iterator.increment] == end_of_day_index:
                for _, trade in self.broker.open_trades.iterrows():
                    self.sell(self.close(self.data_iterator.increment, 0), trade_id=trade['id'])
                return True
        return False

    def next(self):
        # Run Entries
        if self.CumulateOrders is False:
            if self.broker.open_trades.empty:
                self.entry_conditions()
        else:
            self.entry_conditions()
        
        self.exit_conditions()

    def buy(self, price, number_of_contracts = 1, trade_id = None):
        if trade_id == None:
            self.broker.open_position('long', price, number_of_contracts)
        else:
            ...
            
    def sell(self, price, number_of_contracts = 1, trade_id = None):
        if trade_id == None:
            self.broker.open_position('short', price, number_of_contracts)
        else:
            self.broker.close_position(trade_id, price, number_of_contracts)

    def open(self, tf, index):
        flipped_data = self.data_iterator.simulation_data[tf].iloc[:self.data_iterator.current_indices[tf]+1].reset_index(drop=True)
        flipped_data = flipped_data.iloc[::-1].reset_index(drop=True)
        return flipped_data.loc[index, 'Open'] 
    
    def close(self, tf, index):
        flipped_data = self.data_iterator.simulation_data[tf].iloc[:self.data_iterator.current_indices[tf]+1].reset_index(drop=True)
        flipped_data = flipped_data.iloc[::-1].reset_index(drop=True)
        return flipped_data.loc[index, 'Close'] 
    
    def high(self, tf, index):
        flipped_data = self.data_iterator.simulation_data[tf].iloc[:self.data_iterator.current_indices[tf]+1].reset_index(drop=True)
        flipped_data = flipped_data.iloc[::-1].reset_index(drop=True)
        return flipped_data.loc[index, 'High'] 
    
    def low(self, tf, index):
        flipped_data = self.data_iterator.simulation_data[tf].iloc[:self.data_iterator.current_indices[tf]+1].reset_index(drop=True)
        flipped_data = flipped_data.iloc[::-1].reset_index(drop=True)
        return flipped_data.loc[index, 'Low'] 
    
    def datetime(self):
        return self.data_iterator.current_time
