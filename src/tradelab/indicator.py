import pandas as pd
import numpy as np

class ValueBasedIndicators:
    def __init__(self, data_iterator):
        self.data_iterator = data_iterator
        self.period = None
        self.timeframes = []
        self.column_names = None

    def initialize_df(self):
        self.data = {}
        for tf in self.timeframes:
            df = pd.DataFrame(columns=['DateTime'] + self.column_names)
            df['DateTime'] = self.data_iterator.simulation_data[tf]['DateTime'].copy()
            self.data[tf] = df

    # def indicators_indices_to_update(self):
    #     for tf in self.timeframes:   
    #         latest_updated_indicator_index = self.data[tf].iloc[:, 1:].last_valid_index() or 0
    #         current_index = self.data_iterator.current_indices[tf]
    #         missing_indices = [current_index] + list(self.data[tf].loc[latest_updated_indicator_index+1:current_index].index)

    #         idx = 0
    #         while idx < len(missing_indices):
    #             index = missing_indices[idx]
    #             # Remove index if day's data has less than required period
    #             if idx in range(self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]), self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]) + self.period):
    #                 missing_indices.remove(index)
    #             # Skip iterations based on the condition
    #             if idx == self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]) + self.period:
    #                 idx += self.data_iterator.n_bar_in_day[tf] - self.period  # Skip iterations
    #             else:
    #                 idx += 1  # Otherwise, increment index normally
            
    #         return missing_indices
    def indicators_indices_to_update(self):
        for tf in self.timeframes:   
            latest_updated_indicator_index = self.data[tf].iloc[:, 1:].last_valid_index()
            if latest_updated_indicator_index is not None:
                missing_indices = list(np.arange(latest_updated_indicator_index+1, self.data_iterator.current_indices[tf] + 1))
            else:
                missing_indices = list(np.arange(0, self.data_iterator.current_indices[tf] + 1))
            
            if not missing_indices:
                missing_indices.append(self.data_iterator.current_indices[tf])
            elif missing_indices[-1] != self.data_iterator.current_indices[tf]:
                missing_indices.append(self.data_iterator.current_indices[tf])
            
            missing_indices_copy = missing_indices.copy()
            idx = 0
            while idx < len(missing_indices_copy):
                index = missing_indices_copy[idx]
                # Remove index if day's data has less than required period
                if index in range(self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]), self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]) + self.period):
                    missing_indices.remove(index)
                idx += 1  # Otherwise, increment index normally
            return missing_indices
        
    def update_indicators(self):
        for tf in self.timeframes:
            for index in self.indicators_indices_to_update():
                values = self.update()
                for col_idx in range(len(values)):
                    self.data[tf].iloc[index, col_idx + 1] = values[col_idx]
            
    def update(self):
        raise NotImplementedError("Subclasses should implement this!")
    
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



class FunctionBasedIndicators:
    def __init__(self, data_iterator):
        self.data_iterator = data_iterator
        self.period = None
        self.timeframes = []
        self.column_names = None

    def initialize_df(self):
        self.data = {}
        for tf in self.timeframes:
            df = pd.DataFrame(columns=['DateTime'] + self.column_names)
            df['DateTime'] = self.data_iterator.simulation_data[tf]['DateTime'].copy()
            self.data[tf] = df

    def indicators_indices_to_update(self):
        for tf in self.timeframes:   
            latest_updated_indicator_index = self.data[tf].iloc[:, 1:].last_valid_index()
            if latest_updated_indicator_index is not None:
                missing_indices = list(np.arange(latest_updated_indicator_index+1, self.data_iterator.current_indices[tf] + 1))
            else:
                missing_indices = list(np.arange(0, self.data_iterator.current_indices[tf] + 1))
            
            if not missing_indices:
                missing_indices.append(self.data_iterator.current_indices[tf])
            elif missing_indices[-1] != self.data_iterator.current_indices[tf]:
                missing_indices.append(self.data_iterator.current_indices[tf])
            
            missing_indices_copy = missing_indices.copy()
            idx = 0
            while idx < len(missing_indices_copy):
                index = missing_indices_copy[idx]
                # Remove index if day's data has less than required period
                if index in range(self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]), self.data_iterator.n_bar_in_day[tf] * (index // self.data_iterator.n_bar_in_day[tf]) + self.period):
                    missing_indices.remove(index)
                idx += 1  # Otherwise, increment index normally
            return missing_indices
        
    def update_indicators(self):
        for tf in self.timeframes:
            for index in self.indicators_indices_to_update():
                values = self.update()
                for col_idx in range(len(values)):
                    self.data[tf].iloc[index, col_idx + 1] = values[col_idx]
            
    def update(self):
        raise NotImplementedError("Subclasses should implement this!")
    
    def function(self):
        raise NotImplementedError("Subclasses should implement this!")
    
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
    
    

       