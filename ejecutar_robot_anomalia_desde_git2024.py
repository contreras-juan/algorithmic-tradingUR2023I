import urllib.request


code = 'https://raw.githubusercontent.com/ELOSPO/algorithmic-tradingUR2023I/clases/productivazacion_anomaly_2024.py'

response = urllib.request.urlopen(code)

data = response.read()

exec(data)