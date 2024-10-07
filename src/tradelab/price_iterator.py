import os
import copy
import pandas as pd
from datetime import timedelta


def add_timedelta(increment):
    if increment == '1sec':
        return timedelta(seconds=1)
    if increment == '1min':
        return timedelta(minutes=1)
    if increment == '5min':
        return timedelta(minutes=5)
    if increment == '1hour':
        return timedelta(hours=1)
    if increment == 'daily':
        return timedelta(days=1)

class PriceIterator:
    def __init__(self, data):
        self.data = data
        self.simulation_data = copy.deepcopy(self.data)
        self.intervals = {'1sec': '1S', '10sec': '10S', '1min': '1T', '5min': '5T', '30min': '30T', '1hour': '1H', 'daily': 'D'}
        self.orders = {tf: i for i, tf in enumerate(self.data.keys())}
        self.resolutions = list(self.data.keys())
        self.n_bar_in_day = {tf: self.data[tf]['DateTime'].dt.date.value_counts().iloc[0] for tf in self.resolutions}
        self.increment = self.resolutions[0]
        self.current_indices = {tf: 0 for tf in self.data}
        self.current_time = self.data[self.increment].loc[self.current_indices[self.increment], 'DateTime']
        self.initialize_simulation_data()

    def initialize_simulation_data(self):
        initial_prices = self.simulation_data[self.increment].loc[0, ['Open', 'High', 'Low', 'Close']]
        for tf in self.simulation_data.keys():
            self.simulation_data[tf].loc[0, ['Open', 'High', 'Low', 'Close']] = initial_prices

    def next(self):
        self.current_indices[self.increment] += 1
        self.current_time = self.update_current_time('ceil', self.increment)
        new_price = self.simulation_data[self.increment].loc[self.current_indices[self.increment], ['Open', 'High', 'Low', 'Close']]        
        for tf in self.resolutions:
            if self.orders[tf] > self.orders[self.increment]:
                current_tf_time = self.simulation_data[tf].loc[self.current_indices[tf], 'DateTime']
                increment_time = self.simulation_data[self.increment].loc[self.current_indices[self.increment], 'DateTime'].floor(self.intervals[tf])
                if current_tf_time != increment_time:
                    self.current_indices[tf] += 1
                    self.simulation_data[tf].loc[self.current_indices[tf], ['Open', 'High', 'Low', 'Close']] = new_price
                else:
                    self._update_high_low_close(tf, new_price)
            elif self.orders[tf] < self.orders[self.increment]:
                self.current_indices[tf] = self.simulation_data[tf][self.simulation_data[tf]['DateTime'] <= self.current_time].index.max()

    def change_increment(self, new_increment):
        self.increment = new_increment
        new_time = self.update_current_time('floor', new_increment)
        if self.current_time != new_time:
            self.current_time = new_time
            for tf in self.resolutions:
                if self.orders[tf] <= self.orders[self.increment]:
                    self._reset_current_data(tf)
                else:
                    self._update_high_low_close(tf, self.simulation_data[self.increment].loc[self.current_indices[self.increment], ['High', 'Low', 'Close']])
    
    def _update_high_low_close(self, tf, new_price):
        current_index = self.current_indices[tf]
        self.simulation_data[tf].loc[current_index, 'High'] = max(new_price['High'], self.simulation_data[tf].loc[current_index, 'High'])
        self.simulation_data[tf].loc[current_index, 'Low'] = min(new_price['Low'], self.simulation_data[tf].loc[current_index, 'Low'])
        self.simulation_data[tf].loc[current_index, 'Close'] = new_price['Close']

    def update_current_time(self, mode, increment):
        if mode == 'floor':
            return self._get_floored_time(increment)
        elif mode == 'ceil':
            return self._get_ceiled_time(increment)
        
    def _reset_current_data(self, tf):
        self.simulation_data[tf].loc[self.current_indices[tf], ['Open', 'High', 'Low', 'Close']] = \
            self.data[tf].loc[self.current_indices[tf], ['Open', 'High', 'Low', 'Close']]
        self.current_indices[tf] = self.simulation_data[tf][self.simulation_data[tf]['DateTime'] <= self.current_time].index.max()

    def _get_floored_time(self, increment):
        interval_delta = {
            '5min': timedelta(minutes=4, seconds=59),
            '1min': timedelta(seconds=59),
            '10sec': timedelta(seconds=9),
            '1sec': timedelta(milliseconds=999)
        }

        return self.simulation_data[self.increment].loc[self.current_indices[self.increment],'DateTime'] + interval_delta.get(increment, timedelta())

    def _get_ceiled_time(self, increment):
        interval_delta = {
            '5min': timedelta(minutes=4, seconds=59),
            '1min': timedelta(seconds=59),
            '10sec': timedelta(seconds=9),
            '1sec': timedelta(milliseconds=999)
        }
        return self.simulation_data[self.increment].loc[self.current_indices[self.increment],'DateTime'] + interval_delta.get(increment, timedelta())

    def is_next(self):
        return self.current_indices[self.resolutions[0]] < len(self.data[self.resolutions[0]]) - 1