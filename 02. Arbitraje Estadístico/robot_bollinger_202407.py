import pandas as pd
import numpy as np
import pandas_ta as ta
import MetaTrader5 as mt5
import time

#https://github.com/twopirllc/pandas-ta

# df = pd.DataFrame()

# # Help about this, 'ta', extension
# help(df.ta)

# # List of all indicators
# df.ta.indicators()


nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos)
    tabla = pd.DataFrame(rates)
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's')
    
    return tabla

def calcular_operaciones_abiertas():
    try:
        open_positions = mt5.positions_get()
        df_positions = pd.DataFrame(list(open_positions), columns = open_positions[0]._asdict().keys())
        df_positions['time'] = pd.to_datetime(df_positions['time'], unit = 's')
    except:
        df_positions = pd.DataFrame()
    
    return df_positions

def enviar_operaciones(simbolo,tipo_operacion, precio_tp,precio_sl,volumen_op):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "sl": precio_sl,
                "tp":precio_tp,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202304,
                "comment": 'Reg',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

# for operacion in lista_ops:
#     df_operacion = df_positions_profit[df_positions_profit['ticket'] == operacion]

#     tipo_operacion = df_operacion['type'].item()
#     simbolo_op = df_operacion['symbol'].item()
#     volumen_op = df_operacion['volume'].item()

#     # Sell 1 / 0 Compra
#     if tipo_operacion == 1:
#         orden_close = {
#             "action": mt5.TRADE_ACTION_DEAL,
#             "symbol": simbolo_op,
#             "volume" : volumen_op,
#             "type" : mt5.ORDER_TYPE_BUY,
#             "position":operacion,
#             "type_time": mt5.ORDER_TIME_GTC,
#             "type_filling": mt5.ORDER_FILLING_IOC
#                         }
        
#         mt5.order_send(orden_close)
    
#     else :
#         orden_close = {
#             "action": mt5.TRADE_ACTION_DEAL,
#             "symbol": simbolo_op,
#             "volume" : volumen_op,
#             "type" : mt5.ORDER_TYPE_SELL,
#             "position":operacion,
#             "type_time": mt5.ORDER_TIME_GTC,
#             "type_filling": mt5.ORDER_FILLING_IOC
#                         }
        
#         mt5.order_send(orden_close)

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


data = extraer_datos('XAUUSD',9999,mt5.TIMEFRAME_H1)
df_bol = ta.bbands(data['close'],25,2)
data['bbl'] = df_bol['BBL_25_2.0']
data['bbu'] = df_bol['BBU_25_2.0']
data['bbm'] = df_bol['BBM_25_2.0']
data['dif_bandas'] = data['bbu'] - data['bbl']
data['dif_bandas'].plot()
data['dif_bandas'].hist(bins = 40)
data['dif_media'] = data['bbm'] - data['bbm'].shift(5)

mediana = data['dif_bandas'].median()
media = data['dif_bandas'].mean()

inicio_volatilidad = 1.5*media

#Código inicial

# if (data['dif_bandas'].iloc[-1] > inicio_volatilidad) and (data['dif_media'].iloc[-1] > 0 ) and (data['close'].iloc[-1] <= data['bbl'].iloc[-1]):
#     enviar_operaciones('XAUUSD',mt5.ORDER_TYPE_BUY,data['close']*(1+0.03),data['close']*(1-0.01),0.05)
# elif (data['dif_bandas'].iloc[-1] > inicio_volatilidad) and (data['dif_media'].iloc[-1] < 0 ) and (data['close'].iloc[-1] >= data['bbu'].iloc[-1]):
#     enviar_operaciones('XAUUSD',mt5.ORDER_TYPE_SELL,data['close']*(1-0.03),data['close']*(1+0.01),0.05)
# else:
#     print('No se cumplieron todas las condiciones')

def robot_bollinger(simbolo,timeframe,porc_tp,porc_sl,escala_vol,lot_size,len_window,sigma:float,len_shift):
    data = extraer_datos(simbolo,9999,timeframe)
    df_bol = ta.bbands(data['close'],len_window,sigma)
    data['bbl'] = df_bol[f'BBL_{len_window}_{sigma}']
    data['bbu'] = df_bol[f'BBU_{len_window}_{sigma}']
    data['bbm'] = df_bol[f'BBM_{len_window}_{sigma}']
    data['dif_bandas'] = data['bbu'] - data['bbl']
    data['dif_media'] = data['bbm'] - data['bbm'].shift(len_shift)

    mediana = data['dif_bandas'].median()
    media = data['dif_bandas'].mean()

    inicio_volatilidad = escala_vol*media

    if (data['dif_bandas'].iloc[-1] > inicio_volatilidad) and (data['dif_media'].iloc[-1] > 0 ) and (data['close'].iloc[-1] <= data['bbl'].iloc[-1]):
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY,data['close']*(1+porc_tp),data['close']*(1-porc_sl),lot_size)
    elif (data['dif_bandas'].iloc[-1] > inicio_volatilidad) and (data['dif_media'].iloc[-1] < 0 ) and (data['close'].iloc[-1] >= data['bbu'].iloc[-1]):
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL,data['close']*(1-porc_tp),data['close']*(1+porc_sl),lot_size)
    else:
        print('No se cumplieron todas las condiciones')

while True:
    robot_bollinger('EURUSD',mt5.TIMEFRAME_M1,0.06,0.02,1.5,0.01,30,2.1,4)
    robot_bollinger('XAUUSD',mt5.TIMEFRAME_M1,0.10,0.03,1.8,0.07,19,2.0,5)

    time.sleep(60)

