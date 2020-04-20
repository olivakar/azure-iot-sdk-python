from azure.iot.device import IoTHubModuleClient
import time
import threading


class IoTHubManager:
    """
    This class manages iothub control

    :ivar client : iothub client Object from Microsoft Azure library
    :ivar logger : logger object
    """

    methodList = ["shutdown", "setTunnel", "sendStatus", "searchDevices"]

    def __init__(self, connection_string, logger=None):
        """
        Connects to Azure IoT Hub
        :param connection_string: IoTHub connection string
        :param logger: logger
        """
        self.client = IoTHubModuleClient.create_from_connection_string(connection_string)
        self.logger = logger

    def sendReportedState(self, payload):
        """
        Sends reported state to IoT Hub.

        :param payload: Required Payload as JSON
        """
        # print("check: " + str(payload))
        payload = self.adjustKeys(payload, [".", "$", "#", " "], "_")
        try:
            print("IIoTHub Send to Azure: " + str(payload))
            # next line commented, because it causes our memory leak
            self.client.patch_twin_reported_properties(payload)
        except Exception:
            print("Exception in send Reported state " + str(payload))

    def emit_status(self, reported_state):
        """
        Send state to devicetwin with log
        """
        try:
            # TODO: check user context value
            self.sendReportedState(reported_state)
            self.logger.handle_info("send_reported_state accepted message: %s" % reported_state)
        except Exception as e:
            self.logger.handle_exception(e, "emit_status ")


class Observer:
    def sendBufferToTwin(self, seconds=0):
        """
        Sens
        :param seconds:
        :return:
        """
        time.sleep(seconds)
        payload = {}
        # output queue length before sending
        print("MEMORY-LEAK-DEBUG: Queue length BEFORE sending: %s" % self.payloadQueue.qsize())
        self.payloadQueue.put(None)
        for data in iter(self.payloadQueue.get, None):
            # payload = update_dict(payload, data)
            pass
        self.iothub.sendReportedState(payload)
        self.collectorTimerRuns.clear()
        print("MEMORY-LEAK-DEBUG: Queue length AFTER sending: %s" % self.payloadQueue.qsize())

    def bufferAndSendToTwin(self, payload):
        """
        Buffer payload data for in self.updateTime specified time and then send it to Azure device twin
        :param payload: Dict wich should be sent to azure deviceTiwn
        :return:
        """
        # hold payload to send it at next sending period
        self.payloadQueue.put(payload)

        # if data comes in, buffer further data for 10s and then push it to Azure
        if not self.collectorTimerRuns.is_set():
            self.collectorTimerRuns.set()
            triggerThread = threading.Thread(
                target=self.sendBufferToTwin,
                name="TriggerBufferThread",
                args=(self.updateTime,),
                daemon=False,
            )
            triggerThread.start()
