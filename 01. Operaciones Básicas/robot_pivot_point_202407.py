import pandas as pd
import MetaTrader5 as mt5
import time
# Clase Septiembre 6 del 2023
from datetime import timedelta
import datetime

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'


# realizar conexión con MT5
mt5.initialize(login = nombre, password = clave, server = servidor, path = path)


def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario des MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def obtener_ordenes_pendientes():
    try:
        ordenes = mt5.orders_get()
        df = pd.DataFrame(list(ordenes), columns = ordenes[0]._asdict().keys())
    except:
        df = pd.DataFrame()

    return df

def remover_operacion_pendiente():
    df = obtener_ordenes_pendientes()
    df_estrategia = df.copy()
    ticket_list = df_estrategia['ticket'].unique().tolist()
    for ticket in ticket_list:
        close_pend_request = {
                                "action": mt5.TRADE_ACTION_REMOVE,
                                "order": ticket,
                                "type_filling": mt5.ORDER_FILLING_IOC
        }

        resultado = mt5.order_send(close_pend_request)
        return resultado

def enviar_operaciones(simbolo,tipo_operacion,precio, precio_tp,precio_sl,volumen_op,exp_int):
    orden_sl = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": simbolo,
                "price": precio,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "sl": precio_sl,
                "tp": precio_tp,
                "magic": 2024071,
                "comment": 'PP',
                "type_filling": mt5.ORDER_FILLING_IOC,
                "type_time": mt5.ORDER_TIME_SPECIFIED,
                "expiration": exp_int
                }

    resultado = mt5.order_send(orden_sl)

    return resultado

def calculate_pivot_points(df):

    high = df['high'].iloc[0]
    low = df['low'].iloc[0]
    close = df['close'].iloc[0]

    pivot = (high + low + close)/3

    f_support = 2*pivot -high
    s_support = pivot - (high-low)
    t_support = low - 2*(high - pivot)

    f_resistance = 2*pivot -low
    s_resistance = pivot + (high-low)
    t_resistance = high + 2*(pivot - low)


    return f_support, s_support, t_support, f_resistance, s_resistance, t_resistance

# hoy = datetime.datetime.now() + timedelta(hours=8)
# hora_expiracion = hoy + timedelta(days = 1)
# tiempo_exp = int(hora_expiracion.timestamp())

while True:
    for simbolo in ['EURUSD','GBPUSD','USDJPY','GBPAUD','CHFJPY','XAUUSD']:
        if (datetime.datetime.now().hour > 7) and (datetime.datetime.now().hour < 12):
            remover_operacion_pendiente()
            data = extraer_datos(simbolo,2,mt5.TIMEFRAME_D1)
            data = data.head(1)
            f_support, s_support, t_support, f_resistance, s_resistance, t_resistance = calculate_pivot_points(data)
            hoy = datetime.datetime.now() + timedelta(hours=8)
            hora_expiracion = hoy + timedelta(days = 1)
            tiempo_exp = int(hora_expiracion.timestamp())
            # Estrategia de reversión a la media
            print('Primer Soporte: ', f_support)
            print('Segundo Soporte: ', s_support)
            print('Primer Resistencia: ', f_resistance)
            print('Segundo Resistencia: ', s_resistance)

            tiempo_exp = int(hora_expiracion.timestamp())
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY_LIMIT,f_support,f_support + 3*(f_support-s_support),s_support,0.5,tiempo_exp)
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL_LIMIT,f_resistance,f_resistance - 3*(s_resistance - f_resistance),s_resistance,0.5,tiempo_exp)

            # Estrategia de Momentum

            enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY_STOP,s_resistance,s_resistance + 3*(s_resistance-f_resistance),f_resistance,0.5,tiempo_exp)
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL_STOP,s_support,s_support - 3*(f_support - s_support),s_support,0.5,tiempo_exp)
        else:
            print('Fuera de horario')
    time.sleep(60*60*24)