import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from backtesting import Backtest, Strategy
from Easy_Trading import Basic_funcs

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave,servidor,path)


class Estrategia_muy_simple(Strategy):
    def init(self):
        self.prices_close = self.data.Close
        self.prices_open = self.data.Open

    def next(self):

        self.delta = self.prices_close - self.prices_open

        if self.delta > 0:
            self.position.close()
            self.buy()
        elif self.delta < 0:
            self.position.close()
            self.sell()

data = bfs._get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',200)
        