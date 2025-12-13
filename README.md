# EasyDen

An IoT smart-home system.

**Table of Contents**
- [Overview](#overview)
- [Architecture](#architecture)
- [Devices](#devices)
    - [Thermostat](#thermostat)
    - [Power Outlet](#power-outlet)
    - [Irrigation](#irrigation)
- [Roadmap](#roadmap)


## Overview

**Note: This project is a work in progress.**

This project contains a collection of custom built WiFi-capable devices for home automation tasks and centralized control. Primary goals are autonomous device operation (where applicable) and event scheduling.
Additionally, it should maintain a high degree of extensibility making it easy to add new types of devices to the system. The various devices are meant to share a reasonably consistent and mobile-friendly user interface.
![Dashboard screenshot](https://github.com/user-attachments/assets/38e4d9e6-d8dc-4ed4-bfd2-53cb6fea6a93 "Main dashboard page")
[More screenshots here.](https://github.com/braeden-mulligan/EasyDen/issues/1)



## Architecture

At a high level, the system is composed of two major components; a central server for coordination, and a collection of one or more devices.

The server hosts a web application for user interaction and a device management process to which devices will connect.
The device manager is responsible for a number of tasks including keeping track of device states, firing scheduled events, and translating/routing messages between the web app and devices.

A device must simply be able to make a TCP connection to the server and implement a custom messaging protocol used by the system.
Most [device implementations](#devices) are built on an ATMega328p for application logic and coupled with an esp8266 for WiFi capability.

#### Device messaging protocol
The device messaging protocol requires devices to respond to two main types of messages, "get" and "set", to interact with attributes of a device, similar to read/write of Bluetooth Low Energy or I<sup>2</sup>C. All messages are transmitted as a single packet with a 4-tuple of numbers, and exchanges are always initiated by the server. An exchange will consist of the server sending one message (either a get or set, with the exception of a special request during initial handshake/device discovery) and receiving a corresponding response.

Each device has some set of application-specific attributes such as current state, sensor readings, configurations etc. These have an associated value that can be fetched, and in some cases set to modify device behaviour. 
The [packet structure](https://github.com/braeden-mulligan/EasyDen/blob/main/device-firmware/libraries/common/protocol.h) contains 4 items of data totalling 8 bytes. The items must be transmitted as a string of comma-separated hexadecimal integers which should appear in order of a 2 byte sequence number/packet id, followed by a 1 byte command specifier, then followed by a 1 byte attribute identifier. The last 4 bytes contain the attribute value **represented as a hex integer**, or a bogus value if not required. The device should always respond with its current value of that attribute.

#### Voice commands
A limited set of commands for some device types can be issued via speech to supplement user interaction; uses the same API as the web app client. Run [this (work-in-progress) tool](https://github.com/braeden-mulligan/EasyDen/blob/main/voice-command/speech_recognition.py) on a device with a microphone and speakers to provide speech recognition capability in convenient locations.


## Devices 
### Thermostat
This is a basic digital thermostat that uses one or more Maxim Integrated ds18b20 sensors to read ambient air temperature. It uses a simple feedback loop to determine when to toggle a single channel relay to switch the heater on and can therefore be used, for example, with typical 24V-controlled central heating system, or electric baseboard heating up to 240V. The existing [mechanical design](https://github.com/braeden-mulligan/EasyDen/blob/main/mechanical/Thermostat%20Case.stl) supports both a [lower current](https://www.pcbway.com/project/gifts_detail/1_Channel_Relay_Module_5V_with_optocoupler_Support_High_and_Low_Level_Trigger.html) and [higher current](https://www.sparkfun.com/sparkfun-beefcake-relay-control-kit-ver-2-0.html) relay module that can be chosen depending on application requirements.

### Power Outlet
Each power outlet unit extends a regular 120V residential power outlet to provide control with the smart-home system.
The plug sockets of each unit can be toggled on or off individually (or in groups depending on hardware configuraion for that unit).

### Irrigation

**Note: In development.**

This device is intended for monitoring soil moisture of multiple potted plants and automatically watering each when necessary.
There is a significant amount of ad hoc plumbing to be set up based on application needs; requiring a water reservoir, pump, valves, and appropriate routing of pipes. The pump and valves are controlled via relay which affords flexibility in plumbing hardware choices. The current implementation allows for configurations of up to three separate plant pots. The system can be set to simply monitor soil moisture, but application logic does provide autonomous operation capability.

### Video Camera

**Note: Prototype stage.**

A basic Raspberry Pi-powered video camera with motion detection and video streaming functionality. Upon motion detection (or optionally active streaming) video data will begin recording. The camera can also be configured to send notifications upon events such as motion detection.



## Roadmap

In no particular order:

- Automated window blinds/curtains
- Data visualization 
- Motion-detection video camera
- Front door intercom

