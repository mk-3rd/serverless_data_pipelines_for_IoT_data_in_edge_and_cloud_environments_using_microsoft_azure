import logging

import azure.functions as func
from zipfile import ZipFile
import tempfile
import datetime


def main(myblob: func.InputStream, outputblob: func.Out[bytes]):

          
    dir_path = tempfile.gettempdir()

    logging.info(f"FUNC START" + ('%s' % datetime.datetime.now()) + "\n"
                 f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes and path is {dir_path}")


    with open("/tmp/my_file.zip", "wb") as binary_file:
   
        binary_file.write(myblob.read())
   
    # loading the temp.zip and creating a zip object
    with ZipFile("/tmp/my_file.zip", 'r') as zObject:
  
    # Extracting all the members of the zip 
    # into a specific location.
        zObject.extractall(path="/tmp")

    logging.info(f"DECOMPRESS END" + ('%s' % datetime.datetime.now()) + "\n")

    #zip_file = myblob.name
    #audio_file =  zip_file.replace("zip", "mp3")
    #audio_file = "p001.mp3"
    
    with open ("/tmp/" + 'audio.mp3', 'rb') as file:
        # read all content of a file
        content = file.read()
        outputblob.set(content)
    
    logging.info(f"UPLOAD END" + ('%s' % datetime.datetime.now()) + "\n")

