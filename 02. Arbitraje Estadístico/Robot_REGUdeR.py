import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression

nombre = 67106046
clave = 'Sebas.123'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

mt5.initialize(login = nombre, password = clave, server = servidor, path = path)

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
                #"price": mt5.symbol_info_tick(simbolo).ask,
                "volume" : volumen_op,
                "type" : tipo_operacion,
                "magic": 202304,
                "comment": 'Reg',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
                }

    mt5.order_send(orden_sl)

def calculate_position_size(symbol, tradeinfo, per_to_risk):
    print(symbol)

    mt5.symbol_select(symbol, True)
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)
    current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2
    sl = tradeinfo
    tick_size = symbol_info.trade_tick_size
    balance = mt5.account_info().balance
    risk_per_trade = per_to_risk
    ticks_at_risk = abs(current_price - sl) / tick_size
    tick_value = symbol_info.trade_tick_value
    position_size = round((balance * risk_per_trade) / (ticks_at_risk * tick_value),2)
    
    return position_size
    
simbolo = 'EURUSD'

while True:
    datos = extraer_datos(simbolo,10,mt5.TIMEFRAME_M1)

    y = datos[['close']]
    datos['minutos'] = range(10)
    X = datos[['minutos']]

    modelo = LinearRegression().fit(X,y)

    pendiente = modelo.coef_

    params = np.append(modelo.intercept_,modelo.coef_)
    predictions = modelo.predict(X)

    # stats.coef_pval(modelo,X,y)

    newX = pd.DataFrame({"Constant":np.ones(len(X))}).join(pd.DataFrame(X))
    MSE = (np.sum((y-predictions)**2))/(len(newX)-len(newX.columns))
    var_b = MSE[0]*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
    sd_b = np.sqrt(var_b)
    ts_b = params/ sd_b

    p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-len(newX.columns)))) for i in ts_b]

    sd_b = np.round(sd_b,3)
    ts_b = np.round(ts_b,3)
    p_values = np.round(p_values,3)

    print(p_values[1])
    print(pendiente)
    tradeinfo = 0.003


    if pendiente > 0 and p_values[1] < 0.9:
        lotaje = 0.05
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_BUY, 0,0,lotaje)
    if pendiente < 0 and p_values[1] < 0.9:
        lotaje = 0.05
        enviar_operaciones(simbolo,mt5.ORDER_TYPE_SELL, 0,0,lotaje)

    time.sleep(60)

nombre = 67043467
clave = 'Genttly.2022'
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\MetaTrader 5\terminal64.exe'

