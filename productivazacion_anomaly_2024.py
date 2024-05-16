import pandas as pd
import pandas_ta as pt
import numpy as np
import MetaTrader5 as mt5
import time
import datetime
from datetime import timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from lib_robots_ur2024 import Lib_Robots

nombre = 67043467
# clave = 'Genttly.2022'
clave = input('Ingrese contraseña: ')
pass_class = input('Autentique la licencia: ')
servidor = 'RoboForex-ECN'
path = r'C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe'

lbr = Lib_Robots(nombre, clave, servidor, path)



while True:
    lbr.anomaly_detection('EURUSD',mt5.TIMEFRAME_H1,0.01165,0.06587,pass_class)
    time.sleep(30)
