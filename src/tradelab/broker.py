import pandas as pd
import numpy as np
import itertools

class Broker:
    def __init__(self, data_iterator):
        self.spread = 2.4
        self.data_iterator = data_iterator
        self.trade_id = itertools.count(start=0, step=1)
         
        self.open_trades = pd.DataFrame({
            'id': [],
            'Entry_time': [],
            'entry_price': [],
            'dir': 'long',
            'number_of_contracts' : [],
            'profit' : [],
        })

        self.closed_trades = pd.DataFrame({
            'id': [],
            'Entry_time': [],
            'entry_price': [],
            'exit_price' : [],
            'Exit_time': [],
            'dir': 'long',
            'number_of_contracts' : [],
            'profit' : [],
        })
                
        self.entry_signals = {(tf, direction): pd.DataFrame(columns=['DateTime', 'entry_price', 'number_of_contracts']) for tf in self.data_iterator.data for direction in ['long', 'short']}
        self.exit_signals = {(tf, direction): pd.DataFrame(columns=['DateTime', 'exit_price', 'number_of_contracts']) for tf in self.data_iterator.data for direction in ['long', 'short']}

    def open_position(self, dir, price, number_of_contracts):
        new_instance = pd.DataFrame({
            'id' : [next(self.trade_id)],
            'Entry_time': [self.data_iterator.current_time],
            'entry_price' : [price],
            'dir' : [dir],
            'number_of_contracts' : [number_of_contracts],
            'profit' : [-self.spread]
            })
        self.open_trades = pd.concat([self.open_trades, new_instance])
        self.open_trades.reset_index(inplace=True, drop=True)
        self.update_signals('entry', new_instance)
        del new_instance
        
    def close_position(self, trade_id, price, number_of_contracts):
        trade = self.open_trades[self.open_trades['id'] == trade_id].squeeze()
        entry_time = trade['Entry_time']
        entry_price = trade['entry_price']
        dir = trade['dir']
        if dir == 'long':
            profit = price - entry_price - self.spread
        elif dir == 'short':
            profit = entry_price - price + self.spread
        new_instance = pd.DataFrame({
            'id': [trade_id],
            'Entry_time': [entry_time],
            'entry_price' : [entry_price],
            'exit_price' : [price],
            'Exit_time': [self.data_iterator.current_time],
            'dir' : [dir],
            'number_of_contracts' : [number_of_contracts],
            'profit' : [profit]
        })
        self.closed_trades = pd.concat([self.closed_trades, new_instance])
        self.closed_trades.reset_index(inplace=True, drop=True)
        self.open_trades.drop(0, inplace=True)
        self.open_trades.reset_index(inplace=True, drop=True)
        self.update_signals('exit', new_instance)
        del new_instance

    def update(self):
        self.update_open_trades()
        
    def update_open_trades(self):
        for index, trade in self.open_trades.iterrows():
            if trade['dir'] == 'long':
                self.open_trades.loc[index, 'profit'] = self.data_iterator.simulation_data[self.data_iterator.resolutions[0]].iloc[self.data_iterator.current_indices[self.data_iterator.resolutions[0]],4] - trade['entry_price'] - self.spread 
            if trade['dir'] == 'short':
                self.open_trades.loc[index, 'profit'] = trade['entry_price'] - self.data_iterator.simulation_data[self.data_iterator.resolutions[0]].iloc[self.data_iterator.current_indices[self.data_iterator.resolutions[0]],4] + self.spread 

    def update_signals(self, type, instance):

        if type == 'entry':
            
            instance.rename(columns={'Entry_time': 'DateTime', 'id':'trade_id'}, inplace=True)
            dir = instance.loc[0, 'dir']
            for tf in set(tf for tf, dir in self.entry_signals.keys()):
                instance.loc[0, 'DateTime'] = self.data_iterator.simulation_data[tf].iloc[self.data_iterator.current_indices[tf],0]
                self.entry_signals[tf, dir] = pd.concat([self.entry_signals[tf, dir], instance[['DateTime', 'entry_price', 'number_of_contracts']]])
        
        elif type == 'exit':
            instance.rename(columns={'Exit_time': 'DateTime', 'id':'trade_id'}, inplace=True)
            dir = instance.loc[0, 'dir']
            for tf in set(tf for tf, dir in self.exit_signals.keys()):
                instance.loc[0, 'DateTime'] = self.data_iterator.simulation_data[tf].iloc[self.data_iterator.current_indices[tf],0]
                self.exit_signals[tf, dir] = pd.concat([self.exit_signals[tf, dir], instance[['DateTime', 'exit_price', 'number_of_contracts']]])
