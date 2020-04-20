import sys
import time
import iiothub


class IndustrialGateway:
    def __init__(self):
        try:
            # some code
            self.identity = self.configurator.read_identity()
            # some code
            self.iotTwin = iiothub.IoTHubManager(self.iothub["connection"], self.logger)
            # some code
        finally:
            pass


# if __name__ == "__main__":
#     handler = IndustrialGateway()
#     try:
#         while handler.state == gatewayRunning:
#             time.sleep(1)
#             # pass
#         sys.exit(0)
#     finally:
#         pass
