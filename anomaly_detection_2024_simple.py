import pandas_ta as pt
import pandas as pd
import MetaTrader5 as mt5
import time
import numpy as np
import datetime
from datetime import timedelta
from Easy_Trading import Basic_funcs

import statistics as stat

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

bfs = Basic_funcs(nombre,clave,servidor,path)

def anomaly_detection(symbol,timeframe,vlr_dif_inf,vlr_crit_std):
    
    data = bfs.extract_data(symbol,timeframe,100)
    data['ema_25'] = pt.ema(data['close'],12)
    data['desv_mean'] = data['close'] - data['ema_25']
    data['std_20'] = pt.stdev(data['close'],15)

    ultima_dif_ema = data['desv_mean'].iloc[-1]
    ultima_desv_std = data['std_20'].iloc[-1]
    

    if (ultima_dif_ema <= vlr_dif_inf) and (ultima_desv_std >= vlr_crit_std):
        bfs.buy(symbol, 1.0)
    else:
        print('No se cumplen las condiciones')

    num_ops, data_ops = bfs.get_opened_positions(symbol)

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
                bfs.close_all_open_operations(df_pos3)
