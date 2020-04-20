# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from six.moves import input
import threading
from azure.iot.device import IoTHubDeviceClient
import azure.iot.device as iothub_library_root
import random
import time
import gc
import inspect
import weakref
import logging

logging.basicConfig(level=logging.ERROR)

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
# The client object is used to interact with your Azure IoT hub.

iothub_library_root_path = os.path.dirname(inspect.getsourcefile(iothub_library_root))
iothub_library_root_path_len = len(iothub_library_root_path) + 1


class LeakedObject(object):
    """
    Object holding details on the leak of some IoTHub client object
    """

    def __init__(self, source_file, obj):
        self.source_file = source_file
        self.value = str(obj)
        self.weakref = weakref.ref(obj)

    def __repr__(self):
        return "{}-{}".format(self.source_file, self.value)

    def __eq__(self, obj):
        return self.source_file == obj.source_file and self.weakref == obj.weakref

    def __ne__(self, obj):
        return not self == obj


def _is_paho_object(obj):
    if not isinstance(obj, BaseException):
        try:
            c = obj.__class__
            source_file = inspect.getsourcefile(c)
        except (TypeError, AttributeError):
            pass
        else:
            if source_file and "paho" in source_file:
                return True
    return False


def _is_iothub_object(obj):
    if not isinstance(obj, BaseException):
        try:
            c = obj.__class__
            source_file = inspect.getsourcefile(c)
        except (TypeError, AttributeError):
            pass
        else:
            if source_file and source_file.startswith(iothub_library_root_path):
                return True
    return False


def get_all_iothub_objects():
    """
    Query the garbage collector for a a list of all objects that
    are implemented in an iothub library.
    """
    all = []
    for obj in gc.get_objects():
        if _is_iothub_object(obj) or _is_paho_object(obj):
            source_file = inspect.getsourcefile(obj.__class__)
            if _is_iothub_object(obj):
                source_file = source_file[iothub_library_root_path_len:]
            try:
                all.append(LeakedObject(source_file, obj))
            except TypeError:
                logging.warning(
                    "Could not add {} from {} to leak list".format(obj.__class__, source_file)
                )
    return all


device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

# connect the client.
device_client.connect()


# define behavior for receiving a message
def patching_twin_listener(device_client):
    while True:
        payload = {"temperature": random.randint(320, 800) / 10}
        device_client.patch_twin_reported_properties(payload)
        print("the data in the payload was")
        print(payload)
        time.sleep(8)


# Run a listener thread in the background
listen_thread = threading.Thread(target=patching_twin_listener, args=(device_client,))
listen_thread.daemon = True
listen_thread.start()


# Wait for user to indicate they are done listening for messages
while True:
    selection = input("Press Q to quit\n")
    if selection == "Q" or selection == "q":
        time.sleep(10)
        all_iothub_objects = get_all_iothub_objects()
        print(all_iothub_objects)
        print("Quitting...")
        break


# finally, disconnect
device_client.disconnect()
