import psutil
from pyzabbix import ZabbixMetric, ZabbixSender

def metric_send():

    metric_send = []

    # Получение загрузки ядер CPU и создание метрик для каждого ядра
    cpu_loads = psutil.cpu_percent(interval=1, percpu=True)
    for i, cpu_load in enumerate(cpu_loads):
        name_metric = f"trap[cpu_load_{i}]"
        metric_cpu_load = ZabbixMetric('Trapper.host', name_metric, cpu_load)
        metric_send.append(metric_cpu_load)

    # Получение общей нагрузки ядер CPU и создание метрик для общей нагрузки всех ядер
    cpu_load_avr = sum(cpu_loads) / len(cpu_loads)
    metric_avr = ZabbixMetric('Trapper.host', 'trap[cpu_load_avr]', cpu_load_avr)
    metric_send.append(metric_avr)

    # Отправка метрики
    zabbix_sender = ZabbixSender(zabbix_server='127.0.0.1' , zabbix_port=10051)
    result = zabbix_sender.send(metric_send)
    print(result)

from fastapi import FastAPI
app = FastAPI()

def metric_get():

    metric_get = []

    # Получение загрузки ядер CPU
    cpu_loads = psutil.cpu_percent(interval=1, percpu=True)
    for i, cpu_load in enumerate(cpu_loads):
        metric_get.append(f'cpu_load(cpu={i}) {cpu_load}')

    # Получение общей нагрузки ядер CPU
    cpu_load_avr = sum(cpu_loads) / len(cpu_loads)
    metric_get.append(f'cpu_load_avr {cpu_load_avr}')

    response = "\n".join(metric_get)
    print(response)
    return response

@app.get("/metrics")
def metric_return():
    return metric_get()

import uvicorn
while True:
    metric_send()
    metric_return()
uvicorn.run(app, host="127.0.0.1", port=8080)