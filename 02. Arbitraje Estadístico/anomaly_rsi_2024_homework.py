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

data['rsi'] = pt.rsi(data['close'],14)

data['rsi'].hist(bins = 40)
data['dif_rsi'] = data['rsi'] - data['rsi'].shift()
data['dif_rsi'].hist(bins = 40)
data['ema100'] = pt.ema(data['close'],100)
data['pendiente_ema'] = data['ema100'] - data['ema100'].shift()
umbral_inf_dif_rsi = data['dif_rsi'].mean() - 2*data['dif_rsi'].std()
umbral_sup_dif_rsi = data['dif_rsi'].mean() + 2*data['dif_rsi'].std()

data['signal'] = np.where( ((data['dif_rsi']>umbral_sup_dif_rsi) & (data['pendiente_ema'] > 0)) |
                           ((data['dif_rsi'] <umbral_inf_dif_rsi) & (data['pendiente_ema'] < 0)), 1,0 )

# Descargar datos a excel #
# data.to_excel(r'C:\Users\Admin\Documents\data_gbpusd.xlsx')

def anomaly_rsi_(symbol,timeframe,vlr_rsi_inf,vlr_rsi_sup,rsi_period):
    
    data = extraer_datos(symbol,100,timeframe)
    data['rsi'] = pt.rsi(data['close'],rsi_period)
    ultimo_rsi = data['rsi'].iloc[-1]
    
    if ultimo_rsi > vlr_rsi_sup:
        enviar_operaciones2(symbol,mt5.ORDER_TYPE_SELL,1.0)
    elif ultimo_rsi < vlr_rsi_inf:
        enviar_operaciones2(symbol,mt5.ORDER_TYPE_BUY,1.0)


anomaly_rsi_('EURSUD',mt5.TIMEFRAME_H1,90,30,22)    
