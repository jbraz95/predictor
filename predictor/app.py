import sys
from api_calls.general_api_calls import get_actual_value
from prediction.regression import get_prediction


def get_server():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        print("You have to add the server and port to use this tool!")
        print("Ex: python3 -m predictor http://www.server.com:9090")
        sys.exit()


def run():
    # Variables
    server = get_server()
    tasks = ["'BASIC_PREPARATION'", "'CREATE_JPEGS'"]
    # finish, started, terminated
    model_list = [[[- 1.9427715755, 1], [+ 2.8701723231, 1], [- 0.1042482924, 1], [+ 4.9257723939, 1]],
                  [[- 1.1012672705, 1], [+ 2.0970134380, 1], [- 0.5041718980, 2], [+ 1.3642873561, 1]]]
    index = 0
    app = "'task-manager'"
    datacenter = "'atlas-xcms-eu-west1'"

    for task in tasks:
        print("Name of task type: " + task)
        query_list = ['incoming_event_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' +
                      task + ',event_type="STARTED"}',
                      'incoming_event_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' +
                      task + ',event_type="FINISHED"}',
                      'incoming_event_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' +
                      task + ',event_type="TERMINATED"}'
                      ]

        prediction = get_prediction(server=server, query_list=query_list, model_list=model_list[index])
        print("The number of incoming tasks should be: " + str(prediction))

        query = 'incoming_task_count_total{app=' + app + ',datacenter=' + datacenter + ', task_type=' + task + \
                ',force="false"}'
        actual_value = get_actual_value(server=server, query=query)[1]
        print("The number of incoming tasks is: " + str(actual_value))

        index += 1

