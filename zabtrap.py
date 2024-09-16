import psutil
from pyzabbix import ZabbixMetric, ZabbixSender

# Получение загрузки нулевого ядра CPU
cpu_load = psutil.cpu_percent(interval=1, percpu=True)[0]

# Создание пакета метрик
metric = [ ZabbixMetric('Trapper.host', 'trap[cpu_load]', cpu_load)
           ]

# Отправка метрики
zabbix_sender = ZabbixSender(zabbix_server = '127.0.0.1' , zabbix_port=10051)
result = zabbix_sender.send(metric)
print(result)