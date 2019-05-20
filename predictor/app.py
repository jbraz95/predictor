import requests
import sys
from api_calls.general_api_calls import get_actual_value

def getserver():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        print("You have to add the server and port to use this tool!")
        print("Ex: python3 -m predictor http://www.server.com:9090")
        sys.exit()


def run():
    # Variables
    server = getserver()
    tasks = ["'BASIC_PREPARATION'", "'CREATE_JPEGS'"]
    app = "'task-manager'"
    datacenter = "'atlas-xcms-eu-west1'"

    for task in tasks:
        #prediction = getPrediction()
        filters = '{app=' + app + ',datacenter=' + datacenter + ', task_type=' + task + ',force="false"}'
        actualValue = get_actual_value(server=server, metric="incoming_task_count_total", filters=filters)
        print(actualValue)

        ietc_started = 'incoming_event_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' + task + \
                       ',event_type="STARTED"}'
        ietc_finished = 'incoming_event_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' + task \
                        + ',event_type="FINISHED"}'
        ietc_terminated = 'incoming_event_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' + task\
                          + ',event_type="TERMINATED"}'
        itct = 'incoming_task_count_total{app=' + app + \
               ',datacenter=' + datacenter + ', task_type=' + task + \
               ',force="false"}'

        metrics = [ietc_started, ietc_finished, ietc_terminated, itct]


