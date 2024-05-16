from Easy_Trading import Basic_funcs
import pandas as pd
import pandas_ta as pt
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'


class Lib_Robots():
    
    def __init__(self,nombre, clave, servidor, path) -> None:
        self.nombre = nombre
        self.clave = clave
        self.servidor = servidor
        self.path = path
        self.bfs = Basic_funcs(self.nombre, self.clave, self.servidor, self.path)


        

    def anomaly_detection(self,symbol,timeframe,vlr_dif_inf,vlr_crit_std,auth):
        
        lic = '2024-05-31'
        pass_class = 'AAA'
        data = self.bfs.extract_data(symbol,timeframe,100)
        data['ema_25'] = pt.ema(data['close'],12)
        data['desv_mean'] = data['close'] - data['ema_25']
        data['std_20'] = pt.stdev(data['close'],15)

        ultima_dif_ema = data['desv_mean'].iloc[-1]
        ultima_desv_std = data['std_20'].iloc[-1]


        if (ultima_dif_ema <= vlr_dif_inf) and (ultima_desv_std >= vlr_crit_std) and (datetime.datetime.now() <= lic) and (auth == pass_class):
            self.bfs.buy(symbol,1.0)
        else:
            print('No se cumplen las condiciones')

        data_ops = self.bfs.get_all_positions()

        if len(data_ops) > 0:
            data_ops2 = data_ops[data_ops['symbol'] == symbol]

            if len(data_ops2) > 0:
                data_ops2['time'] = pd.to_datetime(data_ops2['time'], unit='s')
                data_ops2['time_current'] = datetime.datetime.now() + timedelta(hours=8)
                data_ops2['time_update'] = pd.to_datetime(data_ops2['time_update'], unit='s')
                data_ops2['time_delta'] = (data_ops2['time_current'] - data_ops2['time_update'])
                data_ops2['hours_since'] = [x.total_seconds()/3600 for x in data_ops2['time_delta'].tolist()]

                df_pos3 = data_ops2.copy()
                df_pos3 = df_pos3[df_pos3['hours_since'] >= 6]

                if len(df_pos3 > 0):
                    self.bfs.close_all_open_operations(df_pos3)

