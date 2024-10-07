from tradelab.backtester import BackTester
from tradelab.charts import Charts

import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mplfinance as mpf
from tradelab.price_iterator import PriceIterator
from tradelab.broker import Broker
from utils.data_import import import_data
from tradelab.indicator import ValueBasedIndicators, FunctionBasedIndicators



def visual_backtest(market_config, display_config, strategy, indicators=None, ):
    date_bounds = market_config['date_range']
    time_bounds = market_config['time_range']
    market = market_config['market']
    timeframes = market_config['timeframes']
    data = import_data(date_bounds, time_bounds, market, timeframes)
    price_iterator = PriceIterator(data)
    def on_closing():
        root.quit()
    root = tk.Tk()
    root.title("Stock Price Plot")
    VisualBackTester(root, price_iterator, display_config, strategy, indicators)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

class VisualBackTester:
    def __init__(self, root, price_iterator, display_config, strategy, indicators=None):
        self.root = root
        self.price_iterator = price_iterator
        self.broker = Broker(self.price_iterator)
        self.resolutions = list(self.price_iterator.data.keys())

        self.window_config = display_config['window_config']
        self.view_config = display_config['view_config']
        
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

        self.figures = []
        self.axes = []
        self.canvases = []
        self.toolbars = []
        self.create_canvases()
        self.create_buttons()
        self.plot()


    #MAKE THIS A HELPER FUNCTION IN UTILS/or maybe in INIDICTOR CLASS
    def x_drawing_frame_to_x_plotting_frame(self, tf, x_drawing_frame, x_0):
        if x_0 == 'current_bar':
            current_index = self.price_iterator.current_indices[tf]
            x_ploting_frame = [current_index + value for value in x_drawing_frame]
            return x_ploting_frame


    def instantiate_indicators(self, indicators):
        self.indicators = {}
        for indicator_class, *params in indicators:
            if params:
                kwargs = params[0]
                instance = indicator_class(self.price_iterator, **kwargs)
            else:
                instance = indicator_class(self.price_iterator)

            self.indicators[indicator_class.__name__] = instance

    def create_canvases(self):
        plt.style.use('seaborn-v0_8')
        for idx, window in enumerate(self.window_config):
            if idx == 0:
                parent_window = self.root
            else:
                parent_window = tk.Toplevel(self.root)
                parent_window.title(f"Window {idx + 1}")

            fig, ax = plt.subplots(len(window), 1, figsize=(8, 6))
            fig.patch.set_facecolor('#e6e6e6')
            fig.subplots_adjust(left=0.02, bottom=0.086, right=0.898, top=0.976, wspace=0.2, hspace=0.2)

            canvas = FigureCanvasTkAgg(fig, master=parent_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, parent_window)
            toolbar.mode = 'pan'
            toolbar.update()

            if type(ax) == np.ndarray:
                self.figures.append(fig)
                self.axes.append(ax)
            else:
                self.figures.append(np.array([fig]))
                self.axes.append(np.array([ax]))

            self.canvases.append(canvas)
            self.toolbars.append(toolbar)

    def create_buttons(self):
        next_iteration = tk.Button(self.root, text="Next Iteration", command=self.next)
        next_iteration.pack(side='left')
        start_button = tk.Button(self.root, text="Start", command=self.start)
        start_button.pack(side='left')
        stop_button = tk.Button(self.root, text="Stop", command=self.stop)
        stop_button.pack(side='left')

    def plot(self):
        for idx, window in enumerate(self.window_config):
            self.clear_axes(idx)
            for index, tf in enumerate(window):
                apd = []  
                
                self.append_indicatos_to_drawings(apd, tf, idx, index)

                # # Entry signals
                entry_df = pd.merge(
                    self.price_iterator.simulation_data[tf]['DateTime'],
                    self.broker.entry_signals[tf, 'long'][['DateTime', 'entry_price']].set_index('DateTime'),
                    on='DateTime', how='left'
                )
                entry_df["TradeDate_count"] = entry_df.groupby("DateTime").cumcount() + 1
                entry_df = entry_df.pivot(index='DateTime', columns='TradeDate_count', values="entry_price").rename(
                    columns="entry_price{}".format
                )
                entry_df.columns.name = None
                for i in range(entry_df.shape[1]):
                    apd.append(mpf.make_addplot(entry_df.iloc[:, i:i + 1], type='scatter', marker='^', markersize=50,
                                                ax=self.axes[idx][index]))
                # # Exit signals
                exit_df = pd.merge(
                    self.price_iterator.simulation_data[tf]['DateTime'],
                    self.broker.exit_signals[tf, 'long'][['DateTime', 'exit_price']].set_index('DateTime'),
                    on='DateTime', how='left'
                )
                exit_df["TradeDate_count"] = exit_df.groupby("DateTime").cumcount() + 1
                exit_df = exit_df.pivot(index='DateTime', columns='TradeDate_count', values="exit_price").rename(
                    columns="exit_price{}".format
                )
                exit_df.columns.name = None
                for i in range(exit_df.shape[1]):
                    apd.append(mpf.make_addplot(exit_df.iloc[:, i:i + 1], type='scatter', marker='v', markersize=50,
                                                ax=self.axes[idx][index]))
                            
                        
                mpf.plot(self.price_iterator.simulation_data[tf].set_index('DateTime', inplace=False),
                         ax=self.axes[idx][index], type='ohlc', addplot=apd, returnfig=True, style='charles',
                         width_adjuster_version='v1', datetime_format='%H:%M:%S')

                self.customize_axes(tf, idx, index)
                self.set_axis_limits(tf, idx, index)

        self.root.title(f'{self.price_iterator.current_time} - increment: {self.price_iterator.increment}')
        for canvas in self.canvases:
            canvas.draw()
    
    def clear_axes(self, index):
        if isinstance(self.axes[index], np.ndarray):
            for ax in self.axes[index]:
                ax.cla()
        else:
            self.axes[index][0].cla()
    
    def append_indicatos_to_drawings(self, apd, tf, idx, index):
        for indicator in self.indicators.values():
            if tf in indicator.timeframes:
                if issubclass(type(indicator), ValueBasedIndicators):
                    apd.append(mpf.make_addplot(
                        indicator.data[tf].set_index('DateTime', inplace=False), type='line',
                        ax=self.axes[idx][index]
                    ))

                elif issubclass(type(indicator), FunctionBasedIndicators):
                    coefficents = indicator.data[tf].iloc[self.price_iterator.current_indices[tf], 1:]
                    if not coefficents.isna().values.any():
                        coefficents = coefficents.to_numpy()
                        p = indicator.function(coefficents)
                        y = p(np.linspace(indicator.x_veiw[0], indicator.x_veiw[-1], 100))
                        x_veiw_plotting_frame = self.x_drawing_frame_to_x_plotting_frame(tf, indicator.x_veiw, indicator.x_0)
                        x = np.linspace(x_veiw_plotting_frame[0], x_veiw_plotting_frame[-1], 100)
                        self.axes[idx][index].plot(x, y)
    
    def customize_axes(self, tf, idx, index):
        self.axes[idx][index].set_title(f'{tf}', fontweight='bold')
        self.axes[idx][index].xaxis.grid(color='tab:blue', linestyle='-.', linewidth=0.4)
        self.axes[idx][index].yaxis.grid(color='tab:blue', linestyle='-.', linewidth=0.4)
    
    def set_axis_limits(self, tf, idx, index):
        MultipleLocator_values = {'5min': 10, 'daily': 100}
        view = self.view_config[index]
        if view == 'v1':
            xmin, xmax, ymin, ymax = v1(self.price_iterator, tf)
            self.axes[idx][index].set_xlim(xmin, xmax)
            self.axes[idx][index].set_ylim(ymin, ymax)
            self.axes[idx][index].yaxis.set_major_locator(plt.MultipleLocator(6.2))
        if view == 'v2':
            xmin, xmax, ymin, ymax = v2(self.price_iterator, tf)
            self.axes[idx][index].set_xlim(xmin, xmax)
            self.axes[idx][index].set_ylim(ymin, ymax)
            self.axes[idx][index].yaxis.set_major_locator(plt.MultipleLocator(MultipleLocator_values[tf]))

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

        self.plot()
        for canvas in self.canvases:
            canvas.draw()

    def start(self):
        self.update_flag = True
        self.show_next_point()

    def show_next_point(self):
        if self.update_flag:
            if self.price_iterator.is_next():
                self.next()
                self.root.after(1, self.show_next_point)  # Call after 500 ms (adjust as needed)
            else:
                self.root.quit()

    def stop(self):
        self.update_flag = False


# Helper functions for setting axis limits
def v1(data_iterator, tf):
    n_bars_in_day = data_iterator.n_bar_in_day[tf]
    open_of_day_index = data_iterator.current_indices[tf] // (n_bars_in_day) * n_bars_in_day
    open_of_day = data_iterator.simulation_data[tf].iloc[open_of_day_index, 1]
    xmin = open_of_day_index - 0.5
    xmax = open_of_day_index - 0.5 + n_bars_in_day
    ymax = max(open_of_day + 50, max(data_iterator.simulation_data[tf].iloc[open_of_day_index:open_of_day_index+n_bars_in_day, 2])) + 5
    ymin = min(open_of_day - 50, min(data_iterator.simulation_data[tf].iloc[open_of_day_index:open_of_day_index+n_bars_in_day, 3])) - 5
    return xmin, xmax, ymin, ymax

def v2(data_iterator, tf):
    if tf == '1sec':
        window = 50
        horizon = 10
        ylimt_range = 60
    elif tf == '10sec':
        window = 50
        horizon = 10
        ylimt_range = 60
    elif tf == '1min':
        window = 30
        horizon = 10
        ylimt_range = 250
    elif tf == '5min':
        window = 5
        horizon = 5
        ylimt_range = 60
    elif tf == '1hour':
        window = 50
        horizon = 10
        ylimt_range = 60
    elif tf == 'daily':
        window = 0
        horizon = 1
        ylimt_range = 600

    xmin = data_iterator.current_indices[tf] - window
    xmax = data_iterator.current_indices[tf] + horizon
    mid = (max(data_iterator.simulation_data[tf].iloc[-window:, 1]) + min(
        data_iterator.simulation_data[tf].iloc[-window:, 1])) / 2
    ymax = max(mid + ylimt_range / 2, max(data_iterator.simulation_data[tf].iloc[-window:, 2])) + 5
    ymin = min(mid - ylimt_range / 2, min(data_iterator.simulation_data[tf].iloc[-window:, 3])) - 5
    return xmin - 0.5, xmax, ymin, ymax