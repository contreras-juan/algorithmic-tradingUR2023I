import pandas as pd
import MetaTrader5 as mt5
import time

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

def extraer_datos(simbolo,num_periodos,timeframe):
    rates = mt5.copy_rates_from_pos(simbolo,timeframe,0,num_periodos) # Traer el diccionario con los últimos N datos desde MT5
    tabla = pd.DataFrame(rates) #Convertir el diccionario en un Dataframe
    tabla['time'] = pd.to_datetime(tabla['time'], unit = 's') # Convertir la columna tiempo en timestamp

    return tabla

def enviar_operaciones(simbolo,tipo_operacion,volumen_op):
    orden_martin = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202404,
                "comment": 'Martin2024',
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_martin) 

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

simbolo = 'EURUSD'
marco_tiempo = mt5.TIMEFRAME_M1

while True:

    datos_simbolo = extraer_datos(simbolo,300,marco_tiempo)
    datos_simbolo['media_movil'] = datos_simbolo['close'].rolling(20).mean()
    datos_simbolo['lim_sup'] = datos_simbolo['media_movil'] + datos_simbolo['close'].rolling(20).std()
    datos_simbolo['lim_inf'] = datos_simbolo['media_movil'] - datos_simbolo['close'].rolling(20).std()

    ultimo_precio = datos_simbolo['close'].iloc[-1]
    ultimo_lim_sup = datos_simbolo['lim_sup'].iloc[-1]*0.1
    ultimo_lim_inf = datos_simbolo['lim_inf'].iloc[-1]*0.1
    vol_inicial = 0.5

    num_operaciones = len(calcular_operaciones_abiertas())


    if ultimo_precio >= ultimo_lim_sup:
        if num_operaciones == 0:
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL,vol_inicial)
        elif num_operaciones > 0:
            df_operaciones = calcular_operaciones_abiertas()
            ultimo_profit = df_operaciones['profit'].iloc[-1]
            suma_profit = df_operaciones['profit'].sum()
            if ultimo_profit < 0:
                enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL,vol_inicial*num_operaciones)
            elif suma_profit >= 50:
                close_all_open_operations(df_operaciones)
            else:
                print('Pasó algo raro o el profit es menor a 50')
        else:
            print('Pasó algo raro')

    elif ultimo_precio <= ultimo_lim_inf:
        if num_operaciones == 0:
            enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY,vol_inicial)
        elif num_operaciones > 0:
            df_operaciones = calcular_operaciones_abiertas()
            ultimo_profit = df_operaciones['profit'].iloc[-1]
            suma_profit = df_operaciones['profit'].sum()
            if ultimo_profit < 0:
                enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY,vol_inicial*num_operaciones)
            elif suma_profit >= 50:
                close_all_open_operations(df_operaciones)
            else:
                print('Pasó algo raro o el profit es menor a 50')
        else:
            print('Pasó algo raro')

    else:
        print('No se cumplieron las condiciones')

    time.sleep(10)



