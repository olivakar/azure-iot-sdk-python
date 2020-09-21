# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import os
import msrest
from azure.iot.hub import IoTHubDigitalTwinManager, IoTHubRegistryManager


iothub_connection_str = os.getenv("IOTHUB_CONNECTION_STRING")
device_id = os.getenv("IOTHUB_DEVICE_ID")
component_name = os.getenv(
    "IOTHUB_COMPONENT_NAME"
)  # for the TemperatureController, try thermostat1
command_name = os.getenv("IOTHUB_COMMAND_NAME")  # for the thermostat you can try getMaxMinReport
payload = os.getenv("IOTHUB_COMMAND_PAYLOAD")  # it really doesn't matter, any string will do.
# Optional parameters
connect_timeout_in_seconds = 3
response_timeout_in_seconds = 7  # Must be within 5-300

try:
    # Create IoTHubDigitalTwinManager
    iothub_digital_twin_manager = IoTHubDigitalTwinManager(iothub_connection_str)

    # Invoke component command
    invoke_component_command_result = iothub_digital_twin_manager.invoke_component_command(
        device_id,
        component_name,
        command_name,
        payload,
        connect_timeout_in_seconds,
        response_timeout_in_seconds,
    )
    if invoke_component_command_result:
        print(invoke_component_command_result)
    else:
        print("No invoke_component_command_result found")

    iothub_registry_manager = IoTHubRegistryManager(iothub_connection_str)
    twin = iothub_registry_manager.get_twin(device_id)

    additional_props = twin.additional_properties
    if "modelId" in additional_props:
        print("Model id for digital twin is")
        print("ModelId:" + additional_props["modelId"])

except msrest.exceptions.HttpOperationError as ex:
    print("HttpOperationError error {0}".format(ex.response.text))
except Exception as exc:
    print("Unexpected error {0}".format(exc))
except KeyboardInterrupt:
    print("Sample stopped")
