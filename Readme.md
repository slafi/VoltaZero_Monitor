# Project Description

As part of an end-to-end cloud-based Internet-of-Things (IoT) solution, this project implements a Python application to acquire, process, store and display the [VoltaZero Sensing Unit (VSU)](https://github.com/slafi/VoltaZero_Sensing_Unit) telemetry data. For this purpose, the application, namely VoltaZero Monitor, takes advantage of Python multiprocessing capabilities and the [Eclipse Paho MQTT Python client library](https://pypi.org/project/paho-mqtt/) to demonstrate the ability of developing software tools consuming the VSU telemetry data.

# System Overview

## Data Flow

The VoltaZero Sensing Unit (VSU) wirelessly relays data to the Helium Atom at regular time intervals. The latter publishes the relayed data to the public Helium MQTT server. Any software application can use a [MQTT](https://en.wikipedia.org/wiki/MQTT) client and the relevant authentication credentials in order to subscribe to the appropriate topic to which telemetry data is published. The VoltaZero Monitor uses the [Eclipse Paho-MQTT client](https://pypi.org/project/paho-mqtt/) in order to retrieve the data published by the VSU/Helium Atom.

![Data Flow](./resources/data_flow.png)
*The VoltaZero Monitor retrieves and processes the telemetry messages published to the Helium MQTT server*

## Telemetry Data Structure

The payload of each telemetry message published by the VSU/Helium Atom to the MQTT server's relevant topic is composed of seven distinct fields:

* Field #1: Device unique identifier (i.e., `id`)
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

## MQTT Server Credentials

For the VSU to flawlessly operate as intended, both the attached Helium Atom and Element should be activated and setup using the user's dashboard in the [Helium website](https://legacy.helium.com/). The VSU should also be configured to use the MQTT channel (see [VoltaZero Sensing Unit Configuration](https://github.com/slafi/VoltaZero_Sensing_Unit/blob/master/source/vzero_102/config.h)).

The authentication credentials are provided by the Helium MQTT server connection string which can be retrieved from the MQTT channel page in the user's dashboard (see screenshot below). This connection string is typically formatted as follows: 

```
mqtts://username:password@mqtt.helium.com:28103
```

**NOTICE:** The port *28103* is dedicated to SSL-based connections. To be able to get connected to the MQTT server without providing a SSL certificate, the port *18103* is used instead.

![MQTT Authentication Credentials](./resources/mqtt_settings.png)\
*The MQTT server credentials can be found in the [Helium dashboard](https://legacy.helium.com/channels) (Channels >> Helium MQTT >> MQTT Settings)*

In addition to the username, password, MQTT hostname and connection port, the topic full name (including the the Atom's MAC address) is also required.

# Getting Started

## VoltaZero Monitor Features

VoltaZero Monitor provides the following main features:

* Simple JSON-based configuration
* Automatic database creation and setup
* Concurrent operation
* Silent mode (no viewer)
* Verbose logging

## Application Structure

The VoltaZero Monitor is designed with separation of concerns (SoC) and concurrency in mind. Thus, the application is subdivided into few distinct modules:

| Module           | Purpose / Task            | Operation           |
| :--------------: |:------------------------  | :-----------------: |
| config        | <ul><li> Loads and parses the application configuration  </li></ul> | Main Thread         |
| monitor          | <ul><li> Connects to the MQTT server </li><li> Subscribes to the appropriate topic </li><li> Listens to the topic's events and retrieves the telemetry messages </li><li> Decodes, parses and saves the telemetry messages in a shared queue</li><ul> | Independent Process |
| recorder         | <ul><li> Retrieves telemetry data from the queue at regular time intervals </li><li> Saves retrieved data to the database </li></ul> | Seperate Thread     |
| viewer           | <ul><li> Retrieves telemetry data from the database at regular time intervals </li><li> Shows the telemetry data as a time series using matplotlib library </li></ul> | Independent Process |
| database         | <ul><li> Handles all the database queries </li></ul> | -                   |

The `database`, `utils`, `telemetry` and `logger` modules provide helper functions and objects that are used by the Monitor, Recorder and Viewer classes.

## Application Configuration

The VoltaZero Monitor is configured through a [JSON file](./core/config_template.json). The configuration parameters include the MQTT server properties and authentication credentials, the database properties and the attributes attached to the Monitor, Recorder and Viewer classes. The complete list of the available parameters is given in the table below:

| Parameter        | Description               | Default Value  |
| :-------------:  |:-------------             | :-----:        |
| host             | The MQTT broker hostname  | mqtt.helium.com |
| port             | The MQTT broker connection port |   18103 |
| username         | The MQTT username attached to the Helium account |     |
| secret           | The MQTT password attached to the Helium account |     |
| mac_address      | The Helium Atom MAC address |     |
| topic            | The MQTT topic attached to the Helium Atom |     |
| database         | The name of the SQLite database | voltazero_database.db |
| table_name       | The data table name where the telemetry data is stored |    data |
| recorder_batch_size | The maximum number of telemetry records saved simultaneously (Recorder property) |   100 |
| recorder_interval   | The recorder's time interval (in seconds) to insert data in the database (Recorder property) |   15 |
| time_window      | The time span (in seconds) over which the telemetry data is retrieved from the database (Viewer property) |   300 |
| viewer_interval      | The viewer's time interval (in seconds) to display telemetry plots (Viewer property) |   5 |
| no_viewer      | A flag which indicates whether the viewer is disabled (if set to `true`, the viewer's time series plots are not shown) |   false |

## Run VoltaZero Monitor

### Prerequisites

Prior to running the VoltaZero Monitor, one should go through this short checklist:

1. The VSU/Helium Atom should be up and running (see details in [VoltaZero Sensing Unit](https://github.com/slafi/VoltaZero_Sensing_Unit) project)
2. Copy the JSON file [`config_template.json`](./core/config_template.json) and rename it as `config.json`
3. Edit the file `config.json` to add the authentication information and configure the recorder and viewer parameters as desired
4. Install the required dependencies listed in the requirements file by issuing the command: `pip install -r requirements.txt`

### Running the Application

Once the configuration file is amended properly, the application can be launched using the following command:

```bash
python app.py
```

## Troubleshooting

1. How to make sure that the VSU is working?

* If the VSU is connected to the computer, use a serial console to check the microcontroller's serial output.
* If not, check visually the Arduino LED state (if it blinks once per second, this means that the Atom is in range and telemetry is being sent successfully).

2. How to check that the Helium Atom is working as required?

* **Internet Connectivity:** if the Atom's orange LED is solid, this means it is connected to Internet.
* **VSU/Atom Communication:** if the Atom's blue and red LEDs are blinking intermittently, this means that the VSU and Atom are talking to each other.
* **Data Debug:** check the Atom's dashboard page for live packets and messages log.

3. How to make sure that VoltaZero Monitor is working?

* By default, VoltaZero Monitor logs several debug messages. Check the console output (or log file) to make sure that the application is not complaining.
* VoltaZero Monitor may require to create two files (i.e., the SQLite database and a log file). If the writing permission to the local folder is not granted to the application, it will exit with an IO error.

## Dependencies

* [Paho-MQTT](https://pypi.org/project/paho-mqtt/) - The Eclipse Paho MQTT Python client library
* [WXPython](https://wxpython.org/) - WXPython matplotlib backend, an alternative to TkAgg

## Built With

* [Python 3](https://www.python.org/)

# Case Study: Using VoltaZero Sensing Unit to Monitor a Garage Light

## Usecase Overview

In this scenario, the VSU was installed in a car garage. When the lights in the garage are switched on, the VSU light sensor voltage drops close to zero. Below a threshold of 2.5V, the VSU passive buzzer is triggered at regular intervals until the light sensor reading goes back above the designated threshold. In this experiment, the darkness threshold is considered above to 2.5V.

## Telemetry Data

In the following accelerated video, the data collected by VoltaZero Monitor is shown. This data spans over 38 minutes (from ~7:17 AM to ~7:56 AM).

[![VoltaZero Monitor](https://img.youtube.com/vi/3MmOaOdgpnQ/0.jpg)](https://www.youtube.com/watch?v=3MmOaOdgpnQ)\
*Real-time telemetry data remotely retrieved from the VSU*

## Data interpretation

Around the second 57 of the previous video (which corresponds to ~07:47 AM in the actual timestamps), the light sensor voltage dropped close to 0 for several minutes. Simulatenously, the buzzer state jumped to 1 (ON state) which triggered local a sound alarm. This indicates that the light was turned on in the garage. When the light was turned off less than three minutes later the light sensor voltage increased above the predefined darkness threshold and the passive buzzer stopped its warnings. The combination of the readings from the light sensor and buzzer state can remotely instruct us on what was *likely* happening between 7:47 and 7:50 in the garage. A light was switched on for few minutes later and the light sensor voltage progressively dropping (increasing respectively) at the event beginning (end respectively) may indicate that the garage door was opened, an individual entered and three minutes later switched off the lights (and *likely* left the place). A software tool can implement a set of rules that analyze the sensors data and automatically notify the people of such events.

![Case Study](./resources/case_study.png)
*The VSU triggers the buzzer sound if the garage is lit*

## What's Next?

The VoltaZero Monitor is a small-scale simple demonstrator that is intended to showcase how to close the end-to-end IoT loop by remotely consuming the VSU telemetry messages. So, one can imagine various possible scenarios for the next development steps:

* Multiple VSUs, multiple monitors
* A permenant cloud-based monitor for multiple VSUs (or/and multpile VSU usecases)
* Constrained sensor readings with (near) real-time notifications (e.g., if a sensor reading goes above or below a given threshold, send email / SMS or/and push notification)
* Remote VSU configuration
* Remote VSU actions (e.g., open a door, turn on a cooling fan, trigger a sound/visual alarm, switch on/off a light, etc.)

# Miscellaneous

## Authors

* **Sabeur Lafi** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

* [VoltaZero Sensing Unit](https://github.com/slafi/VoltaZero_Sensing_Unit)
