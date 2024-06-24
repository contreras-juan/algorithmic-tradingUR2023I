import pandas_ta as pt
import pandas as pd
import MetaTrader5 as mt5
import time
import numpy as np
import datetime
from datetime import timedelta


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

def enviar_operaciones2(simbolo,tipo_operacion,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202405,
                "comment": 'Anom_D',
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

def close_all_open_operations(data:pd.DataFrame) -> None:
        '''
        Cierra todas las operaciones que estén contenidas en un dataframe.

        # Parámetros

        - par: Símbolo 
        '''
        
        df_open_positions = data.copy()
        lista_ops = df_open_positions['ticket'].unique().tolist()
            

        for operacion in lista_ops:
            df_operacion = df_open_positions[df_open_positions['ticket'] == operacion]
            price_close = df_operacion['price_current']
            tipo_operacion = df_operacion['type'].item()
            simbolo_operacion = df_operacion['symbol'].item()
            volumen_operacion = df_operacion['volume'].item() 
            # 1 Sell / 0 Buy
            if tipo_operacion == 1:
                tip_op = mt5.ORDER_TYPE_BUY
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)
            if tipo_operacion == 0:
                tip_op = mt5.ORDER_TYPE_SELL
                close_request = {
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol':simbolo_operacion,
                    'volume':volumen_operacion,
                    'type': tip_op,
                    'position': operacion,
                    # 'price': price_close,
                    'comment':'Cerrar posiciones',
                    'type_filling': mt5.ORDER_FILLING_FOK
                }
                mt5.order_send(close_request)

data = extraer_datos('GBPUSD',9999,mt5.TIMEFRAME_H1)
data['ema_25'] = pt.ema(data['close'],12)
data['desv_mean'] = data['close'] - data['ema_25']

data['desv_mean'].plot()
data['desv_mean'].hist(bins = 40)

import statistics as stat

mu = data['desv_mean'].mean()
moda = stat.mode(data['desv_mean'].dropna())
ds_std = data['desv_mean'].std()

# lista_per_std = [3,2,4,5,6,10,11,12]

# for vlr_std in lista_per_std:

data['std_20'] = pt.stdev(data['close'],15)
data['exit_price'] = data['close'].shift(-6)
upper_sigma2 = mu + 2*ds_std
lower_sigma2 = mu - 2*ds_std
upper_sigma3 = mu + 3*ds_std
lower_sigma3 = mu - 3*ds_std
data['upper_sigma3'] = upper_sigma3
data['lower_sigma3'] = lower_sigma3
data2 = data.copy()
data2 = data2[(data2['desv_mean'] > data2['upper_sigma3']) | (data2['desv_mean'] < data2['lower_sigma3'])]
data2['buy'] = np.where((data2['desv_mean'] < data2['lower_sigma3']),1,0)
data2['sell'] = np.where((data2['desv_mean'] > data2['upper_sigma3']),1,0)
data2['price_gap'] = data2['exit_price'] - data2['open']

buy = data2.copy()
buy = buy[buy['buy'] == 1]
buy['win'] = np.where(buy['price_gap'] > 0,1,0)
sell = data2.copy()
sell = sell[sell['sell'] == 1]
sell['win'] = np.where(sell['price_gap'] < 0,1,0)
# print('Este es el acumulado de ganancias de las compras',buy['price_gap'].sum())
# print('Este es el acumulado de ganancias de las ventas',sell['price_gap'].sum()*-1)
# print('Este es el proporción de ganadoras de las compras',buy['win'].mean())
# print('Este es el proporción de ganadoras de las ventas',sell['win'].mean())
buy['avg_std_losers'] = buy[buy['win'] == 0 ]['std_20'].mean()
buy['avg_std_winners'] = buy[buy['win'] == 1 ]['std_20'].mean()
buy_filtered = buy.copy()
len(buy_filtered)
buy_filtered = buy_filtered[buy['std_20'] >= buy['avg_std_winners'] ]
print('Este es el proporción de ganadoras de las compras filtradas ',buy_filtered['win'].mean())
print('Este es el acumulado de ganancias de las compras',buy_filtered['price_gap'].sum())
# data2['std_20'] = data2['close'].rolling.std(20)
buy['avg_std_losers'] = buy[buy['win'] == 0 ]['std_20'].mean()
buy['avg_std_winners'] = buy[buy['win'] == 1 ]['std_20'].mean()
sell['avg_std_losers'] = sell[sell['win'] == 0 ]['std_20'].mean()
sell['avg_std_winners'] = sell[sell['win'] == 1 ]['std_20'].mean()
sell_filtered = sell.copy()
sell_filtered = sell_filtered[sell['std_20'] >= sell['avg_std_winners'] ]
print('Este es el proporción de ganadoras de las ventas filtradas ',sell_filtered['win'].mean())
print('Este es el acumulado de ganancias de las ventas',sell_filtered['price_gap'].sum()*-1)

def anomaly_detection(symbol,timeframe,vlr_dif_inf,vlr_crit_std):
    
    data = extraer_datos(symbol,100,timeframe)
    data['ema_25'] = pt.ema(data['close'],12)
    data['desv_mean'] = data['close'] - data['ema_25']
    data['std_20'] = pt.stdev(data['close'],15)

    ultima_dif_ema = data['desv_mean'].iloc[-1]
    ultima_desv_std = data['std_20'].iloc[-1]
    

    if (ultima_dif_ema <= vlr_dif_inf) and (ultima_desv_std >= vlr_crit_std):
        enviar_operaciones2(symbol,mt5.ORDER_TYPE_BUY, 1.0)
    else:
        print('No se cumplen las condiciones')

    data_ops = calcular_operaciones_abiertas()

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
                close_all_open_operations(df_pos3)

while True:
    anomaly_detection('EURUSD',mt5.TIMEFRAME_H1,-0.005253,0.006012)
    anomaly_detection('GBPUSD',mt5.TIMEFRAME_H1,-0.007520,0.008946)

    time.sleep(60*60)








