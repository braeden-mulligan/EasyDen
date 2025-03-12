from . import device_definitions as defs
from . import utils

import struct

_get = defs.Device_Protocol.CMD_GET
_set = defs.Device_Protocol.CMD_SET
_attr_id = defs.attribute_id

template = "{:02X},{:02X},{:08X}" 

# Where applicapble <attribute_identifier> may be either the attribute label string or the id integer.

def attribute_as_int(attribute_identifier, attributes):
	if isinstance(attribute_identifier, str):
		attribute_identifier = _attr_id(attribute_identifier)

	return attributes.get(str(attribute_identifier), {}).get("value", None)

def attribute_as_float(attribute_identifier, attributes):
	value = attribute_as_int(attribute_identifier, attributes)

	if value is not None:
		value = utils.int32_to_float(value)

	return value

def build_command_from_float(attribute_identifier, value):
	if isinstance(attribute_identifier, str):
		attribute_identifier = _attr_id(attribute_identifier)

	if attribute_identifier is None:
		return None

	packed_float = utils.float_to_int32(value)

	return template.format(_set, attribute_identifier, packed_float)

def build_command_from_int(attribute_identifier, value):
	if isinstance(attribute_identifier, str):
		attribute_identifier = _attr_id(attribute_identifier)

	if attribute_identifier is None:
		return None

	return template.format(_set, attribute_identifier, value)

def generic_request_identity():
	return template.format(defs.Device_Protocol.CMD_IDY, 0, 0)

def generic_ping():
	return template.format(_get, _attr_id("GENERIC_ATTR_PING"), 0)


def poweroutlet_get_count():
	return template.format(_get, _attr_id("POWEROUTLET_ATTR_SOCKET_COUNT"), 0)

def poweroutlet_get_state():
	return template.format(_get, _attr_id("POWEROUTLET_ATTR_STATE"), 0)

# pass a list 
def poweroutlet_set_state(socket_states):
	for i in range(len(socket_states)):
		if socket_states[i] is None:
			socket_states[i] = -1
		socket_states[i] = int(socket_states[i])

	attr_value = utils.list_to_bitmask(socket_states)

	return template.format(_set, _attr_id("POWEROUTLET_ATTR_STATE"), attr_value)

# return list 
def poweroutlet_read_state(attr_value, socket_count):
	if isinstance(attr_value, str):
		attr_value = int(attr_value, 16)

	if isinstance(socket_count, str):
		socket_count = int(socket_count, 16)

	socket_values = utils.bitmask_to_list(attr_value, socket_count)
	socket_selection = utils.bitmask_to_list(attr_value >> 8, socket_count)

	return (socket_values, socket_selection)


def thermostat_get_temperature():
	return template.format(_get, _attr_id("THERMOSTAT_ATTR_TEMPERATURE"), 0)

def thermostat_get_target_temperature():
	return template.format(_get, _attr_id("THERMOSTAT_ATTR_TARGET_TEMPERATURE"), 0)

def thermostat_get_humidity():
	return template.format(_get, _attr_id("THERMOSTAT_ATTR_HUMIDITY"), 0)

def thermostat_set_temperature(value):
	packed_float = utils.float_to_int32(value) 
	return template.format(_set, _attr_id("THERMOSTAT_ATTR_TARGET_TEMPERATURE"), packed_float)


def irrigation_get_moisture(sensor):
	return template.format(_get, _attr_id("IRRIGATION_ATTR_MOISTURE_" + str(sensor)), 0)

def irrigation_get_moisture_raw(sensor):
	return template.format(_get, _attr_id("IRRIGATION_ATTR_SENSOR_RAW_" + str(sensor)), 0)

def irrigation_get_sensor_raw_max(sensor):
	return template.format(_get, _attr_id("IRRIGATION_ATTR_SENSOR_RAW_MAX_" + str(sensor)), 0)

def irrigation_get_sensor_raw_min(sensor):
	return template.format(_get, _attr_id("IRRIGATION_ATTR_SENSOR_RAW_MIN_" + str(sensor)), 0)

def irrigation_get_sensor_recorded_max(sensor):
	return template.format(_get, _attr_id("IRRIGATION_ATTR_SENSOR_RECORDED_MAX_" + str(sensor)), 0)

def irrigation_get_sensor_recorded_min(sensor):
	return template.format(_get, _attr_id("IRRIGATION_ATTR_SENSOR_RECORDED_MIN_" + str(sensor)), 0)

def irrigation_read_plant_enable(reg_value, sensor_count):
	if isinstance(reg_value, str):
		reg_value = int(reg_value, 16)

	if isinstance(sensor_count, str):
		sensor_count = int(sensor_count, 16)

	return utils.bitmask_to_list(reg_value, sensor_count)

def irrigation_set_plant_enable(status_list):
	reg_value = utils.list_to_bitmask(status_list)
	return template.format(_set, _attr_id("IRRIGATION_ATTR_PLANT_ENABLE"), reg_value)

def irrigation_read_calibration_settings(reg_value):
	if isinstance(reg_value, str):
		reg_value = int(reg_value, 16)

	calibration_mode = reg_value & 0X00FF
	plant_select = (reg_value & 0xFF00) >> 8

	return [calibration_mode, plant_select]

def irrigation_set_calibration_settings(mode, plant_select):
	reg_value = int(mode) | (int(plant_select) << 8)
	return template.format(_set, _attr_id("IRRIGATION_ATTR_CALIBRATION_MODE"), reg_value)
