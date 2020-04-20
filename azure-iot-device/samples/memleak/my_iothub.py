import os
import random
from azure.iot.device import IoTHubDeviceClient
import time
import threading
from queue import Queue

# conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
conn_str = "HostName=IOTHubQuickStart.azure-devices.net;DeviceId=crookshanks;SharedAccessKey=Y3AhIaab0smKoYh4PwELfT2iVf+kZ0hkGE3shbSf/2NWGYqVDsQzQwrGib/Rq3RLtMEEDWo66dCKDhlqvqC7MA=="
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)


# send new reported properties
# reported_properties = {"temperature": random.randint(320, 800) / 10}
# print("Setting reported temperature to {}".format(reported_properties["temperature"]))
# device_client.patch_twin_reported_properties(reported_properties)


def update_dict(dict_payload, data):
    key = "temperature" + str(random.randint(1, 1000))
    dict_payload[key] = data
    return dict_payload


class Observer(object):
    def __init__(self):
        self.payloadQueue = Queue()
        self.collectorTimerRuns = threading.Event()
        self.updateTime = 2

    def sendBufferToTwin(self, seconds=1):
        """
        Sens
        :param seconds:
        :return:
        """
        while True:
            time.sleep(seconds)
            payload = {}
            # output queue length before sending
            print("MEMORY-LEAK-DEBUG: Queue length BEFORE sending: %s" % self.payloadQueue.qsize())
            self.payloadQueue.put(None)
            # for data in iter(self.payloadQueue.get, None):
            #     payload = update_dict(payload, data)
            # print(payload)
            payload = {"temperature": random.randint(320, 800) / 10}
            device_client.patch_twin_reported_properties(payload)
            self.collectorTimerRuns.clear()
            print("MEMORY-LEAK-DEBUG: Queue length AFTER sending: %s" % self.payloadQueue.qsize())

    # def bufferAndSendToTwin(self, payload):
    #     """
    #     Buffer payload data for in self.updateTime specified time and then send it to Azure device twin
    #     :param payload: Dict wich should be sent to azure deviceTiwn
    #     :return:
    #     """
    #     #hold payload to send it at next sending period
    #     self.payloadQueue.put(payload)
    #
    #     #if data comes in, buffer further data for 10s and then push it to Azure
    #     if not self.collectorTimerRuns.is_set():
    #         self.collectorTimerRuns.set()
    #         triggerThread = threading.Thread(target=self.sendBufferToTwin,
    #                                          name='TriggerBufferThread',
    #                                          args=(self.updateTime,),
    #                                          daemon=False)
    #         triggerThread.start()


# def bufferAndSendToTwin(observer, payload):
#     while True:
#         observer.payloadQueue.put(payload)
#         if not observer.collectorTimerRuns.is_set():
#             observer.collectorTimerRuns.set()
#             triggerThread = threading.Thread(target=observer.sendBufferToTwin,
#                                                      name='TriggerBufferThread',
#                                                      args=(2,),
#                                                      daemon=False)
#             triggerThread.start()


observer = Observer()
if not observer.collectorTimerRuns.is_set():
    listen_thread = threading.Thread(
        target=observer.sendBufferToTwin, name="TriggerBufferThread", args=(2,)
    )
    listen_thread.daemon = False
    listen_thread.start()

if __name__ == "__main__":

    observer = Observer()

    while True:
        temp = random.randint(320, 800) / 10
        print("Setting reported temperature to {temp}".format(temp=temp))
        observer.bufferAndSendToTwin(temp)
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break
