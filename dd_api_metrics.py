import requests
import json
import time
from datetime import datetime
from datadog_api_client.v1 import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.model.metrics_payload import MetricsPayload
from datadog_api_client.v1.model.point import Point
from datadog_api_client.v1.model.series import Series


def get_status():
    response = requests.get("http://reddevil.local/printer/objects/query?heater_bed&extruder&print_stats")
    response_dict = json.loads(response.text)
    print(response_dict)
    bed_temp = (response_dict['result']['status']['heater_bed']['temperature'])
    bed_power = (response_dict['result']['status']['heater_bed']['power'])
    bed_target = (response_dict['result']['status']['heater_bed']['target'])
    printer_status = (response_dict['result']['status']['print_stats']['state'])
    return bed_temp, bed_target, int(float('%.2g' % bed_power)*100), printer_status


def create_dd_metric(dd_metric, dd_type, value):
    body = MetricsPayload(
        series=[
            Series(
                metric=dd_metric,
                type=dd_type,
                points=[
                    Point(
                        [
                            datetime.now().timestamp(),
                            value,
                        ]
                    ),
                ],
                tags=[
                    "env:prod",
                ],
            ),
        ],
    )

    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        response = api_instance.submit_metrics(body=body)

        print(response)


if __name__ == '__main__':

    for x in range(300):
        current_temp, target, pwm_power, status = (get_status())
        print(current_temp, target, pwm_power, status)
        create_dd_metric('system.printer.hotbed', 'timeseries', current_temp)
        create_dd_metric('system.printer.target', 'timeseries', target)
        create_dd_metric('system.printer.power', 'timeseries', pwm_power)
        time.sleep(2)
