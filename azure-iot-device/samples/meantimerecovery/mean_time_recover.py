# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
import uuid
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from time import perf_counter

messages_to_send = 10

times = []


async def main():
    # The SharedAccessKey Used here is random, but our code is designed in a manner where
    # we need a kaye that can be base 64 decoded. So a string like 'FakeAccessKey' will not work.

    # The device Id does not matter here
    conn_str = "HostName=localhost;DeviceId=devicemtr;SharedAccessKey=Zm9vYmFy"
    # Zm9vYmFy

    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str, keep_alive=30)

    # Connect the client.
    await device_client.connect()

    async def send_test_message(device_client):
        i = 0
        while True:
            print("sending message #" + str(i))
            msg = Message("test wind speed " + str(i))
            msg.message_id = uuid.uuid4()
            msg.correlation_id = "correlation-1234"
            msg.custom_properties["tornado-warning"] = "yes"
            t_start = perf_counter()
            await device_client.send_message(msg)
            t_stop = perf_counter()
            elapsed_time = t_stop - t_start
            print("Elapsed time in seconds:", elapsed_time)
            times.append(elapsed_time)
            print("done sending message #" + str(i))
            i = i + 1
            await asyncio.sleep(8)

    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Schedule task for message listener
    asyncio.create_task(send_test_message(device_client))

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for messages
    await user_finished

    print(times)
    # finally, disconnect
    await device_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
