import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import MetaTrader5 as mt5
from Easy_Trading import Basic_funcs
import pandas_ta as ta

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre, clave, servidor, path)

class Estrategia_simple(Strategy):

    def init(self):
        self.prices_close = self.data.Close
        self.prices_open = self.data.Open
    
    def next(self):

        self.delta = self.prices_close - self.prices_open

        if self.delta > 0:
            self.position.close()
            self.buy(size = 0.01)

        elif self.delta < 0:
            self.position.close()
            self.sell(size = 0.01)

data = bfs._get_data_for_bt(mt5.TIMEFRAME_H1,'EURUSD',9000)
data = bfs.get_data_from_dates(2008,7,21,2024,4,26,'EURUSD',mt5.TIMEFRAME_D1,True)

backtestin_1 = Backtest(data,Estrategia_simple,cash=10_000, exclusive_orders= True)

stats_bt1 = backtestin_1.run()
backtestin_1.plot()

data_1 = bfs.get_data_from_dates(2022,1,1,2022,3,1,'GBPUSD',mt5.TIMEFRAME_H1,True)

data_3 = bfs.get_data_from_dates(2020,3,15,2020,5,15,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_4 = bfs.get_data_from_dates(2015,1,1,2015,3,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_5 = bfs.get_data_from_dates(2023,7,1,2023,9,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_6 = bfs.get_data_from_dates(2024,2,1,2024,4,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_7 = bfs.get_data_from_dates(2021,10,1,2021,12,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_8 = bfs.get_data_from_dates(2021,10,1,2021,12,1,'GBPUSD',mt5.TIMEFRAME_H1,True)
data_9 = bfs.get_data_from_dates(2019,7,21,2019,9,26,'GBPUSD',mt5.TIMEFRAME_H1,True)

lista_datos = [data_1,data_3,data_6,data_5,data_7,data_8]


for data in lista_datos:
    backtestin_1 = Backtest(data,Estrategia_simple,cash=10_000, exclusive_orders= True)
    stats_bt1 = backtestin_1.run()

    print(stats_bt1['Sharpe Ratio'])


class Estrategia_simple_rsi(Strategy):
    lim_sup_rsi = 95
    lim_inf_rsi = 10
    rsi_period = 14

    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)

    def next(self):
        if len(self.price_close) > self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.position.close()
                self.sell(size = 0.01)
            elif self.rsi < self.lim_inf_rsi:
                self.position.close()
                self.buy(size = 0.01)

backtesting_rsi = Backtest(data_3,Estrategia_simple_rsi,cash=10_000, exclusive_orders= True)
results_rsi = backtesting_rsi.run()

stats_rsi_opt, hm = backtesting_rsi.optimize(lim_sup_rsi = [70,75,80,85,95],
                                             lim_inf_rsi = [30,25,20,10,5],
                                             rsi_period = [12,14,16,20],
                                             maximize='Sharpe Ratio', return_heatmap=True)

class Estrategia_simple_rsi(Strategy):
    lim_sup_rsi = 75
    lim_inf_rsi = 25
    rsi_period = 14

    def init(self):
        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)

    def next(self):
        if len(self.price_close) > self.rsi_period:
            if self.rsi > self.lim_sup_rsi:
                self.position.close()
                self.sell(size = 0.01)
            elif self.rsi < self.lim_inf_rsi:
                self.position.close()
                self.buy(size = 0.01)

for data in lista_datos:
    backtesting_rsi_opt = Backtest(data,Estrategia_simple_rsi,cash=10_000, exclusive_orders= True)
    stats_bt_opt = backtesting_rsi_opt.run()

    print(stats_bt_opt['Sharpe Ratio'])

##################################################################################################
##################################################################################################

class Estrategia_ema_rsi(Strategy):
    rsi_period = 14
    ema_period = 100    
    umbral_sup_dif_rsi = 9.758204257059345
    umbral_inf_dif_rsi = -9.760399719788046
    rango_tp = 0.0015
    rango_sl = 0.0005

    def init(self):

        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
        self.ema = self.I(ta.ema,pd.Series(self.price_close),self.ema_period)

    def next(self):
        if len(self.price_close) > self.ema_period:
            self.dif_rsi = self.rsi[-1] -self.rsi[-2]
            self.pend_ema = self.ema[-1] -self.ema[-2]
            if (self.dif_rsi > self.umbral_sup_dif_rsi) and (self.pend_ema > 0):
                # self.buy(size = 0.01)
                self.buy(size = 0.01, tp = self.price_close[-1] + self.rango_tp, sl= self.price_close[-1] - self.rango_sl, limit  = self.price_close[-1])
            elif (self.dif_rsi < self.umbral_inf_dif_rsi) and (self.pend_ema <0):
                
                # self.sell(size = 0.01)
                self.sell(size = 0.01, sl = self.price_close[-1] + self.rango_sl, tp= self.price_close[-1] - self.rango_tp, limit  = self.price_close[-1])

backtesting_rsi_ema = Backtest(data_8,Estrategia_ema_rsi,cash=10_000, exclusive_orders= True)
stats_rsi_opt, hm = backtesting_rsi_ema.optimize(rsi_period = [6,12,14,24],
                                             ema_period = [100,200,300],
                                             maximize='Sharpe Ratio', return_heatmap=True)

class Estrategia_ema_rsi(Strategy):
    rsi_period = 14
    ema_period = 300    
    umbral_sup_dif_rsi = 9.758204257059345
    umbral_inf_dif_rsi = -9.760399719788046
    rango_tp = 0.0015
    rango_sl = 0.0005

    def init(self):

        self.price_close = self.data.Close
        self.rsi = self.I(ta.rsi,pd.Series(self.price_close),self.rsi_period)
        self.ema = self.I(ta.ema,pd.Series(self.price_close),self.ema_period)

    def next(self):
        if len(self.price_close) > self.ema_period:
            self.dif_rsi = self.rsi[-1] -self.rsi[-2]
            self.pend_ema = self.ema[-1] -self.ema[-2]
            if (self.dif_rsi > self.umbral_sup_dif_rsi) and (self.pend_ema > 0):
                # self.buy(size = 0.01)
                self.buy(size = 0.01, tp = self.price_close[-1] + self.rango_tp, sl= self.price_close[-1] - self.rango_sl)
            elif (self.dif_rsi < self.umbral_inf_dif_rsi) and (self.pend_ema <0):
                
                # self.sell(size = 0.01)
                self.sell(size = 0.01, sl = self.price_close[-1] + self.rango_sl, tp= self.price_close[-1] - self.rango_tp)

for data in lista_datos:
    backtesting_rsi_opt = Backtest(data,Estrategia_simple_rsi,cash=10_000, exclusive_orders= True)
    stats_bt_opt = backtesting_rsi_opt.run()

    print(stats_bt_opt['Sharpe Ratio'])