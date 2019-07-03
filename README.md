# Task-Manager Anomaly Detector and Predictor
Javier Bermejo Razquin Internship Prototype

## How to install
First we need to create an app in our Slack workspace. For doing so we go
[here](https://api.slack.com/apps?new_app=1). Then we have to click in Bots and
add a bot user. After that, we will install the app by clicking in
`<Install your app to your workspace>`. If we not click in `<Permissions>` we
will be able to get the `<Bot User OAuth Access Token>`. Take note of it as we
will need it for next step. Now we have the bot created, but we have to connect
it to the program.

For doing so, we have to access the configuration file
(`<predictor/configuration.yaml>`) and modify the parameters `<slack:channel>`
and `<slack:token>`. The token information we just found it in the previous step.
The channel value we can find it by left clicking the name of the channel in the
Slack app and clicking the option `<Copy Link>` and getting the ID from it
(something similar to C81CGBPZ6)

Finally we only have to run the program by typing `<python3 app.py>`

## How to use
Once installed we only have to wait for alarms or type commands.

The command `<help>` will send a message that will inform of all possible
options. These are:
* Alarms:
  * You can stop all alarms by typing: `<stop alarms>`
  * You can resume all alarms by typing: `<resume alarms>`
  * You can pause all alarms by typing: `<pause alarms X minutes>`
* Resetting regression alarms: In case that you want to reset a regression alarm
(because it has already been fixed) you just have to type:
`<resetregression [metric name]>`.
* Visualize charts:
  * To visualise actual values you only have to type `<actual [metric name]>`
  * To visualise forecast values you only have to type `<forecast [metric name]>`
  * To visualise regression values you only have to type
  `<regression [metric name]>`
  * You can mix any of these 3 as you want to see them in the same graph. Per
  example: `<actual forecast regression [metric name]>`


## Configuration
### Configuration File
The configuration file has to be called `<configuration.yaml>` and use this schema

```
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
  token: [SLACK TOKEN - STRING]>
```

### Configuration parameters
