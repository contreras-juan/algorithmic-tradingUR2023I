import pandas as pd
import numpy as np
from Easy_Trading import Basic_funcs
import pandas_ta as ta


nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'




class Robot_Bollinger():

    def __init__(self,nombre, clave,servidor,path):
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
        self.bfs = Basic_funcs(self.nombre, self.clave, self.servidor,self.path)

    def calcular_emas(self,periodo_1, periodo_2, periodo_3,data):
        ema1 = ta.ema(data['close'], periodo_1)
        ema2 = ta.ema(data['close'], periodo_2)
        ema3 = ta.ema(data['close'], periodo_3)

        return ema1,ema2,ema3
        

    def robot_bollinger(self,simbolo,timeframe,porc_tp,porc_sl,escala_vol,lot_size,len_window,sigma:float,len_shift):
        
        data = self.bfs.extract_data(simbolo,timeframe,1000)
        df_bol = ta.bbands(data['close'],len_window,sigma)
        data['bbl'] = df_bol[f'BBL_{len_window}_{sigma}']
        data['bbu'] = df_bol[f'BBU_{len_window}_{sigma}']
        data['bbm'] = df_bol[f'BBM_{len_window}_{sigma}']
        data['dif_bandas'] = data['bbu'] - data['bbl']
        data['dif_media'] = data['bbm'] - data['bbm'].shift(len_shift)
        last_price = data['close'].iloc[-1] 
        rsi = ta.rsi(data['close'],14)

        mediana = data['dif_bandas'].median()
        media = data['dif_bandas'].mean()
        # ema1, ema2,ema3 = self.calcular_emas()

        inicio_volatilidad = escala_vol*media

        if (data['dif_bandas'].iloc[-1] > inicio_volatilidad) and (data['dif_media'].iloc[-1] > 0 ) and (data['close'].iloc[-1] <= data['bbl'].iloc[-1]) and (rsi < 50):
            self.bfs.buy(simbolo,lot_size,nom_bot = 'Bollinger',sl = last_price*(1-porc_sl), tp= last_price*(1+porc_tp))
            
        elif (data['dif_bandas'].iloc[-1] > inicio_volatilidad) and (data['dif_media'].iloc[-1] < 0 ) and (data['close'].iloc[-1] >= data['bbu'].iloc[-1]) and (rsi > 50):
            self.bfs.sell(simbolo,lot_size,nom_bot = 'Bollinger',sl = last_price*(1+porc_sl), tp= last_price*(1-porc_tp))

        # if con las condiciones de salida
        else:
            print('No se cumplieron todas las condiciones')