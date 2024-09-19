import psutil
import uvicorn
from fastapi import FastAPI
from pyzabbix import ZabbixMetric, ZabbixSender


def metric_send():

    metric_send = []
    cpu_loads = psutil.cpu_percent(interval=0.5, percpu=True) # Считается нагрузка ядер процессора, интервал = 0.5 сек
                                        # Если интервал = 0, метрики равны = 0, если интервала нет метрики = 0 или 100

    # Получение загрузки ядер CPU и создание метрик для каждого ядра
    for i, cpu_load in enumerate(cpu_loads):
        name_metric = f"trap[cpu_load_{i}]"
        metric_cpu_load = ZabbixMetric('Trapper.host', name_metric, cpu_load)
        metric_send.append(metric_cpu_load)

    # Получение общей нагрузки ядер CPU и создание метрик для общей нагрузки всех ядер
    metric_avr = ZabbixMetric('Trapper.host', 'trap[cpu_load_avr]', cpu_load)
    metric_send.append(metric_avr)

    # Отправка метрики
    zabbix_sender = ZabbixSender(zabbix_server='127.0.0.1' , zabbix_port=10051)
    result = zabbix_sender.send(metric_send)
    print(result)

def metric_get():

    metric_get = []
    cpu_loads = psutil.cpu_percent(interval=0.5, percpu=True) # Второй раз считается нагрузка ядер процессора, интервал = 0.5 сек
                             # Значение метрик, которые возвращаются вычисляются заново, между первым и вторым подсчетом нагрузки 0.5 сек
    # Получение загрузки ядер CPU
    for i, cpu_load in enumerate(cpu_loads):
        metric_get.append(f'cpu_load(cpu={i}) {cpu_load}')

    # Получение общей нагрузки ядер CPU
    metric_get.append(f'cpu_load_avr {cpu_load}')

    response = "\n".join(metric_get)
    print(response)
    return response

def metric():

    app = FastAPI()
    @app.get("/metrics")

    def metric_return():
        return metric_get()

    while True:
        metric_send() 
        metric_return()
    uvicorn.run(app, host="127.0.0.1", port=8080)

metric() # Метрики отправляются раз в 1 секунду