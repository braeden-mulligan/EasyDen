# EasyDen

An IoT smart-home system.

**Table of Contents**
- [Overview](#overview)
- [Architecture](#architecture)
    - [Server](#server)
    - [Modules](#modules)
- [Devices](#devices)
    - [Thermostat](#thermostat)
    - [Power Outlet](#power-outlet)
    - [Irrigation](#irrigation)
- [Roadmap](#roadmap)


## Overview

**Note: This is a work-in-progress.**

This project contains a collection of custom WiFi-capable devices for home automation tasks and centralized control.
Primary goals for automation are autonomous device operation (where applicable), and to provide event scheduling when user input would otherwise be repeatedly required.
Another goal for the project was to offer a high degree of extensibility for adding new types of devices to the system. The devices are meant to have a consistent user interface and all be accessible from within the same application.

## Architecture

At a high level, the system is composed of two major components; a server and one or more embedded devices.

On the server side, there is a device management component to which the devices connect with directly, and a web application for the UI.
The device manager is responsible for a number of tasks including keeping track of device states, firing scheduled events (device commands), and translating and routing messages from the web app to devices.

A device must simply be able to make a TCP connection to the server and implement a bespoke messaging protocol used by the system.
Details for currently existing device applications can be found in [this section](#devices). All current implementations are built with an Arduino nano for application logic coupled with an Espressif esp8266 for WiFi capability. Although any hardware setup capable of the aforementioned requirements can be used.  

The device messaging protocol in its current form requires devices to respond to two main types of messages, "get" and "set", to interact with attributes of a device, similar to read/write of Bluetooth low energy or I<sup>2</sup>C. All messages are transmitted as a single packet with a 4-tuple of numbers and exchanges are always initiated by the server. An exchange will consist of the server sending a request and receiving a response; this is either a get or set, with the exception of a special request during initial handshake/device discovery.
Each device will have a set of application-specific attributes such as current state, sensor readings, configurations etc. These have an associated value that can be fetched, and in some cases set to control device behaviour. One of the numbers in the message tuple is an address to specify which attribute is being queried, and one is a value used when setting an attribute. The device should then respond with the current value for that attribute.


## Devices 
### Thermostat
This is a basic digital thermostat that uses one or more Maxim Integrated ds18b20 sensors to read ambient air temperature. It uses a simple feedback loop to determine when to toggle a relay with 5V input to switch high voltage electric baseboard heaters. Each thermostat switches a single circuit and could easily be applied in similar situations such as a typical 24V-controlled central heating system.

### Power Outlet
Each power outlet unit extends a regular 120V residential power outlet to provide sockets controllable with the smart-home system.
The sockets of each unit can be toggled on or off individually, either manually or via scheduled events.

### Irrigation

**Note: Features in development.**

This device is intended for monitoring soil moisture of multiple potted plants and automatically watering each when necessary.
There is a significant amount of ad hoc plumbing to be set up requiring a water reservoir, pump, valves, and appropriate routing of pipes. The pump and valves are controlled with a relay which affords flexibility in plumbing hardware choices. The current implementation allows for hardware configurations of up to three separate plant pots.
The system can simply be used for monitoring soil moisture, but application logic can provide fully autonomous operation.

## Roadmap

- Automated window blinds
- Data collection, visualization, insights
- Motion-detection security camera

