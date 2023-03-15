import boto3
from botocore import UNSIGNED
from botocore.client import Config
from Crypto.Cipher import AES
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create SQS client
sqs = boto3.client('sqs', config=Config(signature_version=UNSIGNED),
                   verify=False, endpoint_url=f"http://localhost:4566",
                   region_name=f"us-east-1")

queue_url = 'http://localhost:4566/000000000000/login-queue'

# generate a unique encryption key
key = hashlib.sha256("my_secret_key".encode()).digest()

# initialize the encryption algorithm
cipher = AES.new(key, AES.MODE_ECB)

# create an engine to connect to the database
engine = create_engine(f"postgresql://postgres:postgres@localhost:5432")


def get_single_sqs_message(enable_delete=False):
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    message = response['Messages'][0]

    receipt_handle = message['ReceiptHandle']

    if enable_delete:
        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message)
    return eval(message['Body'])


def encrypt_info(data):
    # pad the device ID and IP to the block size of the algorithm
    block_size = AES.block_size
    data_padded = data + (block_size - len(data) % block_size) * chr(block_size - len(data) % block_size)

    # encrypt the device ID and IP
    encrypted_data = cipher.encrypt(data_padded.encode())

    return encrypted_data


def decrypt_info(encrypted_data):
    # decrypt the device ID and IP
    decrypted_data = cipher.decrypt(encrypted_data)

    # remove padding from the decrypted device ID and IP
    unpadded_data = decrypted_data.decode().rstrip(chr(AES.block_size))
    return unpadded_data


# define a model for the user_logins table
class UserLogin(declarative_base()):
    __tablename__ = "user_logins"
    user_id = Column(String(128), primary_key=True)
    device_type = Column(String(32))
    masked_ip = Column(String(256))
    masked_device_id = Column(String(256))
    locale = Column(String(32))
    app_version = Column(Integer)
    create_date = Column(DateTime)


def write_single_message_to_db(user_login):
    # create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    # add the data entry to the session
    session.add(user_login)
    # commit the transaction
    session.commit()
    # close the session
    session.close()


def process_version_number(app_version):
    l = [int(x, 10) for x in app_version.split('.')]
    l.reverse()
    version = sum(x * (100 ** i) for i, x in enumerate(l))
    return version


if __name__ == '__main__':
    data = get_single_sqs_message()
    masked_device_id = encrypt_info(data['device_id'])
    masked_ip = encrypt_info(data['ip'])
    new_entry = UserLogin(user_id=data['user_id'], device_type=data['device_type'],
                          masked_ip=masked_ip, masked_device_id=masked_device_id,
                          locale=data['locale'], app_version=process_version_number(data['app_version']),
                          create_date=datetime.today().strftime('%Y-%m-%d'))
    write_single_message_to_db(new_entry)
