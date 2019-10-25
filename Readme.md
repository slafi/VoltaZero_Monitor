# Project Description

One Paragraph of project description goes here

[VoltaZero Shield](https://github.com/slafi/VoltaZero)

## System Overview

### Data Flow

The VoltaZero Sensing Unit (VSU) wirelessly relays data to the Helium Atom at regular time intervals. The latter publishes the relayed data to the public Helium MQTT server. Any software application can use a MQTT client and the relevant authentication credentials in order to subscribe to the appropriate topic to which telemetry data is published. The VoltaZero Monitor uses the [paho-mqtt](https://pypi.org/project/paho-mqtt/) client in order to retrieve the data published by the VSU/Helium Atom.

![Data Flow](./resources/data_flow.png)
*The VoltaZero Monitor retrieves and processes the telemetry messages published to the Helium MQTT server*

### Telemetry Data Structure

Each telemetry message published by the VSU/Helium Atom to the MQTT server is composed of seven distinct fields:

* Field #1: Device unique identifier `id`
* Fields #2-7: Sensors' readings (i.e., `t0`, `t1`, `th`, `ir`, `bz` and `lg`)

All these fields are presented in JSON format as follows:

```json
{
    "id":"102",
    "t0":23.566,
    "t1":"null",
    "th":"null",
    "ir":"null",
    "bz":0,
    "lg":4.194
}
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Application Configuration

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

| Parameter        | Description               | Default Value  |
| :-------------:  |:-------------             | :-----:        |
| host             | The MQTT broker hostname  | mqtt.helium.com |
| port             | The MQTT broker host port |   18103 |
| username         | The username attached to the Helium account |     |
| secret           | The password attached to the Helium account |     |
| mac_address      | The Helium atom MAC address |     |
| topic            | The MQTT topic attached to the Helium atom |     |
| database         | The name of the SQLite database | voltazero_database.db |
| table_name       | The data table name where the telemetry data is stored |    data |
| recorder_batch_size | the maximum number of telemetry records saved at once (used by the Recorder) |   100 |
| recorder_interval   | The recorder's time interval to insert data in the database (in seconds) |   15 |
| time_window      | The time span on which the telemetry data is retrieved from the database (in seconds) |   300 |
| viewer_interval      | The viewer's time interval to show telemetry (in seconds) |   5 |
| no_viewer      | A flag which indicates whether the viewer is disabled |   false |

### MQTT Server Credentials

Connection string: mqtts://*username*:*password*@mqtt.helium.com:28103

**NOTICE:** The port 28103 is dedicated to SSL-based connections. To be able to get connected to the MQTT server without providing a SSL certificate, the port 18103 is used instead.

![MQTT Credentials](./resources/mqtt_settings.png)
*The MQTT server credentials can be found in the [Helium dashboard](https://legacy.helium.com/channels) (Channels >> Helium MQTT >> MQTT settings section)*

### Running the Application

Once the configuration file is amended properly, the application can be run as follows:

```
Give examples
```

## Project Modules


### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

## Case Study: Using VoltaZero Shield to monitor a garage

### Telemetry Data

[![VoltaZero Monitor](https://img.youtube.com/vi/3MmOaOdgpnQ/0.jpg)](https://www.youtube.com/watch?v=3MmOaOdgpnQ)\
*Real-time telemetry data remotely retrieved from the VSU*

## Data interpretation

Explain what these tests test and why

![Case Study](./resources/case_study.png)
*The VSU triggers the buzzer sound if the garage is lit*

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Known Limitations

Tkinter does not offer a thread-safe backend for matplotlib. Thus, an exception might be raised when stopping the application due to running the Viewer instance on a distinct thread. As a workaround, other backends may be used (e.g., wxAgg).

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Deployment

Add additional notes about how to deploy this on a live system

## Dependencies

* [Paho-MQTT](https://pypi.org/project/paho-mqtt/) - The Eclipse Paho MQTT Python client library
* [WXPython](https://wxpython.org/) - WXPython matplotlib backend, an alternative to TkAgg

## Built With

* [Python 3](https://www.python.org/)

## Authors

* **Sabeur Lafi** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

* [VoltaZero Shield](https://github.com/slafi/VoltaZero)
