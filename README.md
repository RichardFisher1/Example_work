# TradeLab

**Trading Python Package**: For developing, backtesting, and live trading models.

This `README.md` provides instructions for both Linux/macOS and Windows users, detailing how to clone, install, and set up the project. It also includes a usage example and information about contributing and licensing.

## Installation and Setup

Follow the instructions below to set up the project on your local machine. This will guide you through setting up a Python virtual environment, installing dependencies, and configuring the project.

### Prerequisites

- **Python 3.10+** installed.
- **Git** (optional but recommended).

---

### 1. Clone the Repository

First, clone the repository from GitHub:

```bash
git clone https://github.com/yourusername/tradepy.git
cd tradepy
```

### 2. Installation (Linux / macOS)
For Linux and macOS users, you can set up the project using the provided shell script:

Steps:
Run the setup script to create a virtual environment, install dependencies, and set up the project:

```bash
./setup.sh
```
What the Script Does:
-  Creates a virtual environment in venv/tradepy.
-  Activates the virtual environment. 
-  Upgrades pip, setuptools, and wheel.
-  Installs dependencies from requirements.txt.
-  Installs the project as an editable package using either setup.py or pyproject.toml.

### 3. Installation (Windows)
For Windows users, follow these steps to set up the project:

Steps:
Run the batch script to create a virtual environment, install dependencies, and set up the project:

```bat
.\setup.bat
```
What the Script Does:
-   Creates a virtual environment in venv\tradepy.
-   Activates the virtual environment.
-   Upgrades pip, setuptools, and wheel.
-   Installs dependencies from requirements.txt.
-   Installs the project as an editable package using either setup.py or pyproject.toml.

## Example and Usage
Once the environment is set up, you can run the provided example.py as a test to verify the setup. A trading model is now implemented. First, an Indicator is defined, followed by a Strategy. Finally, the main backtesting class is run, producing the results.

```python
from tradelab.indicator import ValueBasedIndicators, FunctionBasedIndicators

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
```
```python
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

```
```python
from tradelab.backtester import BackTester
from my_indicators import mav
from my_strategies import my_strat_1

market_config = {
'date_range': ('2024-08-22', '2024-09-05'),
'time_range': ('08:00:00', '10:00:00'),
'market': 'dax',
'timeframes': ['1sec', '5min']
}

bt = BackTester(market_config, my_strat_1, [(mav,)])
bt.run()
bt.trades

```

Results - 

| id   | Entry_time              | entry_price   | exit_price   | Exit_time               | dir   | number_of_contracts   | profit   |
|:-----|:------------------------|:--------------|:-------------|:------------------------|:------|:----------------------|:---------|
| 0.0  | 2024-08-22 08:50:00.999 | 18493.2       | 18485.7      | 2024-08-22 08:54:39.999 | long  | 1.0                   | -9.9     |
| 1.0  | 2024-08-22 09:20:00.999 | 18507.2       | 18498.7      | 2024-08-22 09:23:41.999 | long  | 1.0                   | -10.9    |
| 2.0  | 2024-08-22 09:40:05.999 | 18500.7       | 18514.7      | 2024-08-22 09:43:38.999 | long  | 1.0                   | 11.6     |
| ...  | ...                     | ...           | ...          | ...                     | ...   | ...                   | ...      |
| 67.0 | 2024-09-05 08:35:00.999 | 18623.9       | 18634.9      | 2024-09-05 08:37:32.999 | long  | 1.0                   | 8.6      |
| 68.0 | 2024-09-05 08:40:00.999 | 18641.4       | 18631.9      | 2024-09-05 08:43:44.999 | long  | 1.0                   | -11.9    |
| 69.0 | 2024-09-05 09:45:00.999 | 18613.9       | 18607.9      | 2024-09-05 09:47:08.999 | long  | 1.0                   | -8.4     |

The video below demonstrates the old gui visual backtest of a stratgey.

[![Watch the video](https://img.youtube.com/vi/yEn3D8xwkRA/maxresdefault.jpg)](https://youtu.be/yEn3D8xwkRA)

The video below demonstrates the new gui. 

[![Watch the video](https://img.youtube.com/vi/n13-qVpFOng/maxresdefault.jpg)](https://youtu.be/n13-qVpFOng)

## Activating and Deactivating the Virtual Environment
Once the virtual environment is activated, you can deactivate it when you're done working. Here’s how to deactivate and reactivate it when coming back to the project.

### Deactivating the Virtual Environment
After working within the virtual environment, you can deactivate it using the following command:

For Linux/macOS:

```bash
deactivate
```

For Windows:

```bat
deactivate
```
This will exit the virtual environment and return you to your system's default Python environment.

## Reactivating the Virtual Environment
When you return to the project, you'll need to reactivate the virtual environment before running the code. Follow the instructions for your operating system:

For Linux/macOS:

To reactivate the virtual environment, run:

```bash
source venv/tradepy/bin/activate
```

For Windows:

To reactivate the virtual environment, run:

```bat
venv\tradepy\Scripts\activate
```
Once reactivated, you can run your Python scripts or continue development.

