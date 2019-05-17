import requests, sys

# Variables
server = sys.argv[1]
tasks = ["'BASIC_PREPARATION'", "'CREATE_JPEGS'"]
app = "'task-manager'"
datacenter = "'atlas-xcms-eu-west1'"
time = '[2m]'

for task in tasks:
    IECT_Started = 'incoming_event_count_total{app=' + app + \
        ',datacenter=' + datacenter + ', task_type=' + task + \
        ',event_type="STARTED"}'
    IECT_Finished = 'incoming_event_count_total{app=' + app + \
        ',datacenter=' + datacenter + ', task_type=' + task + \
        ',event_type="FINISHED"}'
    IECT_Terminated = 'incoming_event_count_total{app=' + app + \
        ',datacenter=' + datacenter + ', task_type=' + task + \
        ',event_type="TERMINATED"}'
    ITCT = 'incoming_task_count_total{app=' + app + \
        ',datacenter=' + datacenter + ', task_type=' + task + \
        ',force="false"}'

    metrics = [IECT_Started, IECT_Finished, IECT_Terminated, ITCT]

    for metric in metrics:
        response = requests.get(server+'/api/v1/query'.format(sys.argv[1]) \
            , params={'query': metric+time})
        metric = response.json()['data']['result'][0]['values']
        print(metric)

    print(metrics)
