from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from OpenSSL import crypto
from datetime import datetime, timedelta, time
import uuid
import os
import argparse
import getpass

# one_day = datetime.timedelta(1, 0, 0)
PUBLIC_EXPONENT = 65537
EXTENSION_NAME = ".pem"
COMMON_DEVICE_PASSWORD_FILE = "demoCACrypto/private/device_key"
COMMON_DEVICE_CSR_FILE = "demoCACrypto/newcerts/device_csr"
COMMON_DEVICE_CERT_FILE = "demoCACrypto/newcerts/device_cert"


def create_certificate_chain(
    common_name,
    ca_password,
    intermediate_password,
    device_password,
    device_count=1,
    key_size=4096,
    days=365,
):
    """
    This method will create a basic 3 layered chain certificate containing a root, then an intermediate and then some number of leaf certificates.
    This function is only used when the certificates are created from script.

    :param common_name: The common name to be used in the subject. This is a single common name which would be applied to all certs created. Since this common name is meant for all,
    this common name will be prepended by the words "root", "inter" and "device" for root, intermediate and device certificates.
    For device certificates the common name will be further appended with the index of the device.
    :param ca_password: The password for the root certificate which is going to be referenced by the intermediate.
    :param intermediate_password: The password for the intermediate certificate
    :param device_password: The password for the device certificate
    :param device_count: The number of leaf devices for which that many number of certificates will be generated.
    :param key_size: The key size to use for encryption. The default is 4096.
    :param days: The number of days for which the certificate is valid. The default is 1 year or 365 days.
    For the root cert this value is multiplied by 10. For the device certificates this number will be divided by 10.
    """
    # common_name_for_root = "root" + common_name
    # create_root_ca_cert(
    #     root_common_name=common_name_for_root, ca_password=ca_password, key_size=key_size, days=days * 10
    # )
    pass


def create_private_key(password_file, password=None, key_size=4096):
    if password:
        encrypt_algo = serialization.BestAvailableEncryption(str.encode(password))
    else:
        encrypt_algo = None

    private_key = rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT, key_size=key_size, backend=default_backend()
    )
    # Write our key to file
    with open(password_file, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encrypt_algo,
            )
        )

    return private_key


def create_root_ca_cert(root_common_name, root_private_key, days=3650):
    file_root_certificate = "demoCACrypto/newcerts/ca_cert.pem"

    root_public_key = root_private_key.public_key()

    subject = x509.Name(
        [
            x509.NameAttribute(
                NameOID.COMMON_NAME, str.encode(root_common_name).decode("utf-8")
            )  # unicode(common_name, "utf-8")
        ]
    )

    builder = create_cert_builder(
        subject=subject, issuer_name=subject, public_key=root_public_key, days=days, is_ca=True
    )

    root_cert = builder.sign(
        private_key=root_private_key, algorithm=hashes.SHA256(), backend=default_backend()
    )
    with open(file_root_certificate, "wb") as f:
        f.write(root_cert.public_bytes(serialization.Encoding.PEM))

    return root_cert


def create_intermediate_ca_cert(
    root_cert,
    root_key,
    intermediate_common_name,
    intermediate_private_key,
    key_size=4096,
    days=3650,
):
    file_intermediate_certificate = "demoCACrypto/newcerts/intermediate_cert.pem"
    file_intermediate_csr = "demoCACrypto/newcerts/intermediate_csr.pem"

    intermediate_csr = create_csr(
        private_key=intermediate_private_key,
        csr_file=file_intermediate_csr,
        subject=intermediate_common_name,
        is_ca=True,
    )

    builder = create_cert_builder(
        subject=intermediate_csr.subject,
        issuer_name=root_cert.subject,
        public_key=intermediate_csr.public_key(),
        days=int(days / 10),
        is_ca=True,
    )

    intermediate_cert = builder.sign(
        private_key=root_key, algorithm=hashes.SHA256(), backend=default_backend()
    )
    with open(file_intermediate_certificate, "wb") as f:
        f.write(intermediate_cert.public_bytes(serialization.Encoding.PEM))

    return intermediate_cert


def create_cert_builder(subject, issuer_name, public_key, days, is_ca=False):
    builder = x509.CertificateBuilder()

    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer_name)
    builder = builder.public_key(public_key)
    builder = builder.not_valid_before(datetime.today())
    builder = builder.not_valid_after(datetime.today() + timedelta(days=days))
    builder = builder.serial_number(int(uuid.uuid4()))
    builder = builder.add_extension(
        x509.BasicConstraints(ca=is_ca, path_length=None), critical=True
    )
    return builder


def create_multiple_device_keys_and_certs(
    number_of_devices, inter_cert, inter_key, device_common_name, password, key_size=4096, days=3650
):

    for i in range(1, number_of_devices + 1):
        device_password_file = COMMON_DEVICE_PASSWORD_FILE + str(i) + EXTENSION_NAME
        device_csr_file = COMMON_DEVICE_CSR_FILE + str(i) + EXTENSION_NAME
        device_cert_file = COMMON_DEVICE_CERT_FILE + str(i) + EXTENSION_NAME
        device_private_key = create_private_key(
            password_file=device_password_file, password=password, key_size=key_size
        )
        device_csr = create_csr(
            private_key=device_private_key,
            csr_file=device_csr_file,
            subject=device_common_name + str(i),
            is_ca=False,
        )

        builder = create_cert_builder(
            subject=device_csr.subject,
            issuer_name=inter_cert.subject,
            public_key=device_csr.public_key(),
            days=int(days / 100),
            is_ca=False,
        )

        device_cert = builder.sign(
            private_key=inter_key, algorithm=hashes.SHA256(), backend=default_backend()
        )
        with open(device_cert_file, "wb") as f:
            f.write(device_cert.public_bytes(serialization.Encoding.PEM))


def create_csr(private_key, csr_file, subject, is_ca=False):
    builder = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    # Provide various details about who we are.
                    x509.NameAttribute(NameOID.COMMON_NAME, str.encode(subject).decode("utf-8"))
                ]
            )
        )
        .add_extension(x509.BasicConstraints(ca=is_ca, path_length=None), critical=False)
    )

    csr = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(), backend=default_backend()
    )

    with open(csr_file, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    return csr


def create_directories_and_prereq_files(pipeline):
    """
    This function creates the necessary directories and files. This needs to be called as the first step before doing anything.
    :param pipeline: The boolean representing if function has been called from pipeline or not. True for pipeline, False for calling like a script.
    """
    os.system("mkdir demoCACrypto")
    if pipeline:
        # This command does not work when we run locally. So we have to pass in the pipeline variable
        os.system("touch demoCACrypto/index.txt")
    else:
        os.system("type nul > demoCACrypto/index.txt")
        # TODO Do we need this
        # os.system("type nul > demoCACrypto/index.txt.attr")

    os.system("echo 1000 > demoCACrypto/serial")
    # Create this folder as configuration file makes new keys go here
    os.mkdir("demoCACrypto/private")
    # Create this folder as configuration file makes new certificates go here
    os.mkdir("demoCACrypto/newcerts")


def before_cert_creation_from_pipeline():
    """
    This function creates the required folder and files before creating certificates.
    This also copies an openssl configurtaion file to be used for the generation of this certificates.
    NOTE : This function is only applicable when called from the pipeline via E2E tests
    and need not be used when it is called as a script.
    """
    create_directories_and_prereq_files(True)

    # shutil.copy("config/openssl.cnf", "demoCACrypto/openssl.cnf")
    #
    # if os.path.exists("demoCACrypto/openssl.cnf"):
    #     print("Configuration file have been copied")
    # else:
    #     print("Configuration file have NOT been copied")


def create_verficattion_cert(nonce, root_verify):
    issuer_private_key = None
    issuer_cert = None

    if root_verify:
        verification_password_file = "demoCACrypto/private/verfiication_ca_key.pem"
        verfication_csr_file = "demoCACrypto/newcerts/verfiication_ca_csr.pem"
        verfication_cert_file = "demoCACrypto/newcerts/verfiication_ca_cert.pem"
        issuer_key_file = "demoCACrypto/private/ca_key.pem"
        issuer_cert_file = "demoCACrypto/newcerts/ca_cert.pem"
    else:
        verification_password_file = "demoCACrypto/private/verfiication_inter_key.pem"
        verfication_csr_file = "demoCACrypto/newcerts/verfiication_inter_csr.pem"
        verfication_cert_file = "demoCACrypto/newcerts/verfiication_inter_cert.pem"
        issuer_key_file = "demoCACrypto/private/intermediate_key.pem"
        issuer_cert_file = "demoCACrypto/newcerts/intermediate_cert.pem"

    with open(issuer_key_file, "r") as fh:
        pem_data = fh.read()
        issuer_private_key = x509.load_pem_x509_certificate(pem_data, default_backend())

    with open(issuer_cert_file, "r") as fh:
        pem_data = fh.read()
        issuer_cert = x509.load_pem_x509_certificate(pem_data, default_backend())

    verification_private_key = create_private_key(
        password_file=verification_password_file, password=None, key_size=key_size
    )
    verification_csr = create_csr(
        private_key=verification_private_key,
        csr_file=verfication_csr_file,
        subject=nonce,
        is_ca=False,
    )

    verification_builder = create_cert_builder_for_verification(
        subject=verification_csr.subject,
        issuer_name=issuer_cert.subject,
        public_key=verification_csr.public_key(),
        is_ca=False,
    )

    verification_cert = verification_builder.sign(
        private_key=issuer_private_key, algorithm=hashes.SHA256(), backend=default_backend()
    )
    with open(verfication_cert_file, "wb") as f:
        f.write(verification_cert.public_bytes(serialization.Encoding.PEM))


def create_cert_builder_for_verification(subject, issuer_name, public_key, is_ca=False):
    builder = x509.CertificateBuilder()

    builder = builder.subject_name(subject)
    builder = builder.issuer_name(issuer_name)
    builder = builder.public_key(public_key)
    # builder = builder.not_valid_before(datetime.today())
    # builder = builder.not_valid_after(datetime.today() + timedelta(days=days))
    builder = builder.serial_number(int(uuid.uuid4()))
    builder = builder.add_extension(
        x509.BasicConstraints(ca=is_ca, path_length=None), critical=True
    )
    return builder


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a certificate chain.")
    parser.add_argument("domain", help="Domain name or common name.")
    #
    # parser.add_argument(
    #     "--ca-password", type=str, help="CA key password. If omitted it will be prompted."
    # )
    #

    parser.add_argument(
        "--mode",
        type=str,
        help="The mode in which certificate is created. By default non-verification mode. For verification use 'verification'",
    )

    parser.add_argument(
        "--root-verify",
        type=str,
        help="The boolean value to enter in case it is the root or intermediate verification. By default it is True meaning root verifictaion. If veriication of intermediate certification is needed please enter False ",
    )

    parser.add_argument(
        "--nonce",
        type=str,
        help="thumprint generated from iot hub certificates. During verification mode if omitted it will be prompted.",
    )

    args = parser.parse_args()

    common_name = args.domain

    if args.mode:
        if args.mode == "verification":
            mode = "verification"
        else:
            raise ValueError(
                "No other mode except verification is accepted. Default is non-verification"
            )
    else:
        mode = "non-verification"

    if mode == "non-verification":
        pass
    else:
        if args.nonce:
            nonce = args.nonce
        else:
            nonce = getpass.getpass("Enter nonce for verification mode")

        # By default root verify is True unless specifically passed
        if args.root_verify:
            lower_root_verify = args.root_verify.lower()
            if lower_root_verify == "false":
                root_verify = False
            else:
                root_verify = True
        else:
            root_verify = True

    # if args.ca_password:
    #     ca_password = args.ca_password
    # else:
    #     ca_password = getpass.getpass("Enter pass phrase for root key: ")

    # common_name = "leviosa"
    # print(common_name.decode("utf-8"))
    # bytes_val = str.encode(common_name)
    # print(bytes_val)
    # u_val = bytes_val.decode("utf-8")
    # print(u_val)
    # print(str.encode(common_name).decode("utf-8"))

    if mode == "non-verification":
        create_verficattion_cert(nonce, root_verify)
    else:

        create_directories_and_prereq_files(False)
        key_size = 4096
        abs_common_name = "leviosa"
        root_pass = "hogwarts"
        inter_pass = "hogwartsi"
        device_pass = "hogwartsd"

        root_password_file = "demoCACrypto/private/ca_key.pem"
        root_private_key = create_private_key(
            password_file=root_password_file, password=root_pass, key_size=key_size
        )
        root_cert = create_root_ca_cert(
            root_common_name="root" + abs_common_name, root_private_key=root_private_key, days=3650
        )  # Arg parse password

        intermediate_password_file = "demoCACrypto/private/intermediate_key.pem"

        intermediate_private_key = create_private_key(
            password_file=intermediate_password_file, password=inter_pass, key_size=key_size
        )

        intermediate_cert = create_intermediate_ca_cert(
            root_cert=root_cert,
            root_key=root_private_key,
            intermediate_common_name="inter" + abs_common_name,
            intermediate_private_key=intermediate_private_key,
            key_size=4096,
            days=3650,
        )

        create_multiple_device_keys_and_certs(
            number_of_devices=3,
            inter_cert=intermediate_cert,
            inter_key=intermediate_private_key,
            device_common_name="device" + abs_common_name,
            password=device_pass,
            key_size=4096,
            days=3650,
        )
