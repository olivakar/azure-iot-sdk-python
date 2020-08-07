# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.iot.device import ProvisioningDeviceClient
import os
from azure.iot.device import IoTHubDeviceClient
import uuid
from azure.iot.device import Message, X509
import time

provisioning_host = os.getenv("PROVISIONING_HOST")
id_scope = os.getenv("PROVISIONING_IDSCOPE")
registration_id = os.getenv("PROVISIONING_REGISTRATION_ID")
symmetric_key = os.getenv("PROVISIONING_SYMMETRIC_KEY")
x509_key_file = os.getenv("X509_KEY_FILE")
passphrase = os.getenv("PASS_PHRASE")
x509_key_content = None
x509_cert_file = "device_cert.pem"

with open(x509_key_file, "rb") as kf:
    key_content = kf.read()

provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
    provisioning_host, registration_id, id_scope, symmetric_key, cert_management_key=key_content
)

properties = {"House": "Gryffindor", "Muggle-Born": "False"}
provisioning_device_client.provisioning_payload = properties
registration_result = provisioning_device_client.register()

# Individual attributes can be seen as well
print("The status was :-")
print(registration_result.status)
print("The etag is :-")
print(registration_result.registration_state.etag)


cert_content = registration_result.certificate_data

with open(x509_cert_file, "wb") as cf:
    cf.write(cert_content)

if registration_result.status == "assigned":
    print("Will send telemetry from the provisioned device")
    # Create device client from the above result
    x509 = X509(cert_file=x509_cert_file, key_file=x509_key_file, pass_phrase=passphrase)

    device_client = IoTHubDeviceClient.create_from_x509_certificate(
        hostname=registration_result.registration_state.assigned_hub,
        device_id=registration_result.registration_state.device_id,
        x509=x509,
    )

    # Connect the client.
    device_client.connect()

    for i in range(1, 6):
        print("sending message #" + str(i))
        device_client.send_message("test payload message " + str(i))
        time.sleep(1)

    for i in range(6, 11):
        print("sending message #" + str(i))
        msg = Message("test wind speed " + str(i))
        msg.message_id = uuid.uuid4()
        device_client.send_message(msg)
        time.sleep(1)

        # finally, disconnect
        device_client.disconnect()
else:
    print("Can not send telemetry from the provisioned device")
