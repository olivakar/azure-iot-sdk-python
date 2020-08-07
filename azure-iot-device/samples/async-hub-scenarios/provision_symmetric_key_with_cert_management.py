# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from azure.iot.device.aio import ProvisioningDeviceClient
import os
from azure.iot.device.aio import IoTHubDeviceClient
import uuid
from azure.iot.device import Message, X509


messages_to_send = 10
provisioning_host = os.getenv("PROVISIONING_HOST")
id_scope = os.getenv("PROVISIONING_IDSCOPE")
registration_id = os.getenv("PROVISIONING_REGISTRATION_ID")
symmetric_key = os.getenv("PROVISIONING_SYMMETRIC_KEY")
x509_key_file = os.getenv("X509_KEY_FILE")
passphrase = os.getenv("PASS_PHRASE")
x509_key_content = None
x509_cert_file = "device_cert.pem"


async def main():
    # here my the mere presence of the kwarg with the private key we will know that the choice is cert management
    with open(x509_key_file, "rb") as kf:
        key_content = kf.read()

    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host, registration_id, id_scope, symmetric_key, cert_management_key=key_content
    )

    # custom payload defined by the user
    properties = {"House": "Gryffindor", "Muggle-Born": "False"}
    provisioning_device_client.provisioning_payload = properties
    registration_result = await provisioning_device_client.register()

    print("The complete registration result is")
    print(registration_result.registration_state)

    cert_content = registration_result.certificate_data

    with open(x509_cert_file, "wb") as cf:
        cf.write(cert_content)

    if registration_result.status == "assigned":
        print("Will send telemetry from the provisioned device")

        x509 = X509(cert_file=x509_cert_file, key_file=x509_key_file, pass_phrase=passphrase)

        device_client = IoTHubDeviceClient.create_from_x509_certificate(
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
            x509=x509,
        )
        # Connect the client.
        await device_client.connect()

        async def send_test_message(i):
            print("sending message #" + str(i))
            msg = Message("test wind speed " + str(i))
            msg.message_id = uuid.uuid4()
            await device_client.send_message(msg)
            print("done sending message #" + str(i))

        # send `messages_to_send` messages in parallel
        await asyncio.gather(*[send_test_message(i) for i in range(1, messages_to_send + 1)])

        # finally, disconnect
        await device_client.disconnect()
    else:
        print("Can not send telemetry from the provisioned device")


if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
