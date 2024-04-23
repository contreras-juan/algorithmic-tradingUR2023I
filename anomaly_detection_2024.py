import pandas_ta as pt
import pandas as pd
import MetaTrader5 as mt5
import time

#https://github.com/twopirllc/pandas-ta

df = pd.DataFrame()

# Help about this, 'ta', extension
help(df.ta)

# List of all indicators
df.ta.indicators()

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "sl": precio_sl,
                "tp": precio_tp,
                "magic": 202309,
                "comment": 'Martingala',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

data = extraer_datos('XAUUSD',9999,mt5.TIMEFRAME_H1)
data['ema_25'] = pt.ema(data['close'],12)
data['desv_mean'] = data['close'] - data['ema_25']

data['desv_mean'].plot()
data['desv_mean'].hist(bins = 40)

import statistics as stat

mu = data['desv_mean'].mean()
moda = stat.mode(data['desv_mean'].dropna())
ds_std = data['desv_mean'].std()

upper_sigma2 = mu + 2*ds_std
lower_sigma2 = mu - 2*ds_std

upper_sigma3 = mu + 3*ds_std
lower_sigma3 = mu - 3*ds_std

data['upper_sigma3'] = upper_sigma3
data['lower_sigma3'] = lower_sigma3

data2 = data.copy()
data2 = data2[(data2['desv_mean'] > data2['upper_sigma3']) | (data2['desv_mean'] < data2['lower_sigma3'])]