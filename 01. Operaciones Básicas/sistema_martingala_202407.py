import pandas as pd
import MetaTrader5 as mt5
import time
# Clase Septiembre 6 del 2023

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

def enviar_operaciones(simbolo,tipo_operacion,take_profit,stop_loss,lot_size):
    orden_sl = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : lot_size,
                "type" : tipo_operacion,
                "sl": stop_loss,
                "tp": take_profit,
                "magic": 202309,
                "comment": 'Martingala',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK
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

while True:
    df_datos = extraer_datos('XAUUSD', 300,mt5.TIMEFRAME_M1)
    media = df_datos['close'].rolling(12).mean().iloc[-1]
    desv_est = df_datos['close'].rolling(12).std().iloc[-1]
    precio_actual = df_datos['close'].iloc[-1]
    lim_sup = media + 0.15*desv_est
    lim_inf = media - 0.15*desv_est

    op_abiertas = calcular_operaciones_abiertas()
    num_operaciones = len(op_abiertas)

    if num_operaciones == 0:
        if precio_actual > lim_sup:
            tp = mt5.symbol_info_tick('XAUUSD').ask - 1.5
            sl = mt5.symbol_info_tick('XAUUSD').ask + 0.5
            enviar_operaciones('XAUUSD',mt5.ORDER_TYPE_SELL,tp,sl,0.01)
        elif precio_actual < lim_inf:
            tp = mt5.symbol_info_tick('XAUUSD').bid + 1.5
            sl = mt5.symbol_info_tick('XAUUSD').bid - 0.5
            enviar_operaciones('XAUUSD',mt5.ORDER_TYPE_BUY,tp,sl,0.01)

    elif num_operaciones > 0:
        last_df = op_abiertas.tail(1)
        tipo_op = last_df['type'].item()
        profit = last_df['profit'].item()
        last_size = last_df['volume'].item()

        if (profit <0) and (precio_actual > lim_sup):
            tp = mt5.symbol_info_tick('XAUUSD').ask - 1.5
            sl = mt5.symbol_info_tick('XAUUSD').ask + 0.5
            enviar_operaciones('XAUUSD',mt5.ORDER_TYPE_SELL,tp,sl,last_size*2)
        elif (profit <0) and (precio_actual < lim_inf):
            tp = mt5.symbol_info_tick('XAUUSD').bid + 1.5
            sl = mt5.symbol_info_tick('XAUUSD').bid - 0.5
            enviar_operaciones('XAUUSD',mt5.ORDER_TYPE_BUY,tp,sl,last_size*2)

    time.sleep(60)






