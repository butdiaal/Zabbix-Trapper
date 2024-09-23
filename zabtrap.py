import time
import psutil
import uvicorn
import argparse
from fastapi import FastAPI
from pyzabbix import ZabbixMetric, ZabbixSender


def metric_send():
    metric_send = []
    cpu_loads = psutil.cpu_percent(percpu=True)

    # Получение загрузки ядер CPU и создание метрик для каждого ядра
    for i, cpu_load in enumerate(cpu_loads):
        name_metric = f"trap[cpu_load_{i}]"
        metric_cpu_load = ZabbixMetric('Trapper.host', name_metric, cpu_load)
        metric_send.append(metric_cpu_load)

    # Получение общей нагрузки ядер CPU и создание метрик для общей нагрузки всех ядер
    metric_avr = ZabbixMetric('Trapper.host', 'trap[cpu_load_avr]', cpu_load)
    metric_send.append(metric_avr)

    # Отправка метрики
    zabbix_sender = ZabbixSender(zabbix_server='127.0.0.1', zabbix_port=10051)
    result = zabbix_sender.send(metric_send)
    print(result)

app = FastAPI()

@app.get("/metrics")
def metric_get():
    metric_get = []
    cpu_loads = psutil.cpu_percent(percpu=True)

    # Получение загрузки ядер CPU
    for i, cpu_load in enumerate(cpu_loads):
        metric_get.append(f'cpu_load(cpu={i}) {cpu_load}')

    # Получение общей нагрузки ядер CPU
    metric_get.append(f'cpu_load_avr {cpu_load}')

    response = "\n".join(metric_get)
    print(response)
    return response

def metric(send_interval):
    # Отправка метрик и получение их значений
    try:
        while True:
            metric_send()
            metric_get()
            time.sleep(send_interval)
    except KeyboardInterrupt:
        print("Программа завершена")

def argparse_metric():
    parser = argparse.ArgumentParser(description="Отправка метрик в Zabbix через командную строку")
    parser.add_argument("--send-interval", type=int, default=1, help="Интервал отправки метрик в секундах")
    args = parser.parse_args()

    metric(args.send_interval)
    uvicorn.run(app, host='127.0.0.1', port=8080)

argparse_metric()
