# predictor

The configuration file has to be called `configuration.yaml` and use this schema

alerting:
  alerts_paused:
    double_check: [BOOLEAN]
    double_forecast: [BOOLEAN]
    forecast: [BOOLEAN]
    regression: [BOOLEAN]
  forecast_percentage: [FLOAT (0.0 - 1.0)]
  paused: [BOOLEAN]
  paused_time: [FLOAT]
  regression_min_difference: [INT]
  regression_percentage: [FLOAT (0.0 - 1.0)]
arima:
  forecast_time: [INT]
  forecast_training_time: [INT]
  metrics:
  - [METRIC NAME]:
    - constant_yes:
        d: 1
        p: 0
        q: 1
        trend: c
    - constant_no:
        d: 1
        p: 0
        q: 1
        trend: nc
monitoring:
  app: [APP NAME]
  datacenter: [DATACENTER NAME]
  kubernetes_namespace: [KUBERNETES NAMESPACE NAME]
  time_span: [INT]
  time_span_sleep: [INT]
regression:
- [METRIC NAME - DEPENDENT VARIABLE]:
    constant: [FLOAT]
    manual_error: [FLOAT]
    metrics:
    - [METRIC NAME - INDEPENDENT VARIABLE]:
        event_type: [FINISHED - STARTED - TERMINATED - ERROR]
        exp: [INT]
        value: [FLOAT]
    predict: [METRIC NAME IN PROMETHEUS - STRING]
    task_type: [TASK TYPE - STRING]
server:
  url: [SERVER URL - STRING]
slack:
  channel: [SLACK CHANNEL - STRING]
  token: [SLACK TOKEN - STRING]
