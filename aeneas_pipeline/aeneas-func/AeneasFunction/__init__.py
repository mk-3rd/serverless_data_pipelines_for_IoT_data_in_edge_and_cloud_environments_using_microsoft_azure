import logging
import azure.functions as func
from zipfile import ZipFile
import datetime

import sys
sys.path.append('/root/Aeneas/aeneas')

from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from azure.storage.blob import BlobServiceClient

from pathlib import Path


def main(myblob: func.InputStream, outputblob: func.Out[str]):
    logging.info(f"FUNC START: " + ('%s' % datetime.datetime.now()) + "\n"
                 f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    with open("audio.mp3", "wb") as binary_file:
   
        binary_file.write(myblob.read())
    
    # loading the temp.zip and creating a zip object
    #with ZipFile("my_file.zip", 'r') as zObject:
  
    # Extracting all the members of the zip 
    # into a specific location.
    #    zObject.extractall()

    #get text from another blob

    STORAGEACCOUNTURL = "https://aeneasstorage.blob.core.windows.net"
    STORAGEACCOUNTSTRING = "DefaultEndpointsProtocol=https;AccountName=aeneasstorage;AccountKey=blp6sHh3FRrYF56TZrWhVSkNGy5AEICWrGJGCt7Sh9/QPE8KP8ZHMc33rz1jL4JN01SsCG9094TV+ASty6fYmw==;EndpointSuffix=core.windows.net"
    CONTAINERNAME = "textfilecontainer"
    BLOBNAME = "p001.xhtml"

    blob_service_client_instance = BlobServiceClient.from_connection_string(STORAGEACCOUNTSTRING)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)

    with open ("p001.xhtml", 'wb') as file:
        blob_data = blob_client_instance.download_blob()
        data = blob_data.readall()
        file.write(data)
    

    # generate map with aeneas

    # create Task object
    config_string = u"task_language=eng|is_text_type=unparsed|os_task_file_format=json"
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = "/home/site/wwwroot/audio.mp3"
    task.text_file_path_absolute = "/home/site/wwwroot/p001.xhtml"
    task.sync_map_file_path_absolute = "/home/site/wwwroot/syncmap.json"

    # process Task
    ExecuteTask(task).execute()

    # output sync map to file
    task.output_sync_map_file()

    logging.info(f"SYNCMAP CREATED: " + ('%s' % datetime.datetime.now()) + "\n")

    with open ("syncmap.json", 'r') as file:
        # read all content of a file
        content = file.read()
        outputblob.set(content)

    logging.info(f"UPLOAD COMPLETED: " + ('%s' % datetime.datetime.now()) + "\n")