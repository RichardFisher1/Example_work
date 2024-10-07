import os
import copy
import pandas as pd
from datetime import timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
rd = os.path.dirname(os.path.dirname(current_dir))

def import_data(dates, times, market, resolutions):
    data = {tf: pd.DataFrame({}) for tf in resolutions}

    start_time_dates = pd.date_range(start=dates[0] + ' ' + times[0], end=dates[1] + ' ' + times[0], freq='B')
    end_time_dates = pd.date_range(start=dates[0] + ' ' + times[1], end=dates[1] + ' ' + times[1], freq='B')

    for resolution in data.keys():
        for i, value in enumerate(start_time_dates):
            file_path = os.path.join(rd, 'data', market, resolution, f'{value.date()}.csv')

            if os.path.exists(file_path):
                df = pd.read_csv(file_path)

                if resolution == 'daily':
                    df['DateTime'] = pd.to_datetime(df['DateTime'])
                    df.reset_index(inplace=True, drop=True)
                if resolution != 'daily':
                    df['DateTime'] = pd.to_datetime(df['DateTime'])
                    df = df[(df['DateTime'].dt.time >= pd.to_datetime(times[0]).time())
                            & (df['DateTime'].dt.time < pd.to_datetime(times[1]).time())]
                    df.reset_index(inplace=True, drop=True)
                data[resolution] = pd.concat([data[resolution], df], ignore_index=True)
    return data