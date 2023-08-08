import asyncio
import sys
import signal
import threading
from azure.iot.device.aio import IoTHubModuleClient

from azure.storage.blob import BlobServiceClient
import time, datetime, os, uuid
from pathlib import Path
import zlib, zipfile


# global counters
TWIN_CALLBACKS = 0

ACTIVE = False
INTERVAL_SEC = 0.0
UPLOAD_COUNTER = 0
UPLOAD_TARGET = 0
FILE_NAME = "p001.mp3"
TIME_ZERO = time.time()

# Event indicating client stop
stop_event = threading.Event()


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received twin patches
    async def receive_twin_patch_handler(twin_patch):
        global INTERVAL_SEC
        global TWIN_CALLBACKS
        global ACTIVE
        global UPLOAD_TARGET
        global FILE_NAME
        global UPLOAD_COUNTER

        print("Twin Patch received")
        print("     {}".format(twin_patch))
        if "Active" in twin_patch:
            ACTIVE = twin_patch["Active"]
            INTERVAL_SEC = twin_patch["IntervalSec"]
            UPLOAD_TARGET = twin_patch["UploadTarget"]
            FILE_NAME = twin_patch["FileName"]
            UPLOAD_COUNTER = 0
        TWIN_CALLBACKS += 1
        print("Total calls confirmed: {}".format(TWIN_CALLBACKS))

    try:
        # Set handler on the client
        client.on_twin_desired_properties_patch_received = receive_twin_patch_handler
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client

async def run_sample(client):

    # Set up storage connection
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=aeneasstorage;AccountKey=blp6sHh3FRrYF56TZrWhVSkNGy5AEICWrGJGCt7Sh9/QPE8KP8ZHMc33rz1jL4JN01SsCG9094TV+ASty6fYmw==;EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = 'edgeuploadcontainer'
    global UPLOAD_COUNTER
    global ACTIVE

    while True:
        if ACTIVE:
            print("Start job")
            #to get in sync
            while UPLOAD_COUNTER < UPLOAD_TARGET:
                
                print("COMPRESSION START: " + ('%s' % datetime.datetime.now()))
                identifier = str(uuid.uuid4()) + ".zip"
                zf = zipfile.ZipFile(identifier, mode="w")
                zf.write(FILE_NAME, 'audio.mp3', compress_type=zipfile.ZIP_DEFLATED)
                zf.close()
                print("COMPRESSION END: " + ('%s' % datetime.datetime.now()))

                blob_client = blob_service_client.get_blob_client(container=container_name, blob=identifier)
                with open(file=identifier, mode="rb") as data:
                    sleeper()
                    print("UPLOAD START: " + ('%s' % datetime.datetime.now()))
                    blob_client.upload_blob(data)

                print("UPLOAD COMPLETED: " + ('%s' % datetime.datetime.now()))
                UPLOAD_COUNTER += 1
            ACTIVE = False
        else:
            await asyncio.sleep(10)

def sleeper():
    time.sleep(INTERVAL_SEC - ((time.time() - TIME_ZERO) % INTERVAL_SEC))

def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.close()


if __name__ == "__main__":
    main()
