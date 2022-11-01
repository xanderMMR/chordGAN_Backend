from pyexpat import model
from flask import Flask, send_from_directory, send_file, request
from flask_cors import CORS, cross_origin

import os
import yaml
import zipfile
import json
import subprocess
import time
import shutil
import ssl 
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) 
context.load_cert_chain('./resources/server.crt', './resources/server.key')
# from .model.message import new_message as msg

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# Path where MIDI file are generated
DOWNLOAD_DIRECTORY = "./model/Output_Uncondtitionl_MIDI"

###############
# FILE SERVICES

# Get a .zip with all files


@app.route('/get-files', methods=['GET'])
def download_all():

    try:
        # Zip file Initialization
        zipfolder = zipfile.ZipFile(
            'generated.zip', 'w', compression=zipfile.ZIP_STORED)  # Compression type

        # zip all the files which are inside in the folder
        for root, dirs, files in os.walk(DOWNLOAD_DIRECTORY):
            print(root, dirs, files)
            for file in files:
                zipfolder.write(DOWNLOAD_DIRECTORY+"/"+file)
        zipfolder.close()

        return send_file('generated.zip',
                         mimetype='zip',
                         as_attachment=True)

        # Delete the zip file if not needed
        os.remove("generated.zip")

    except Exception as e:
        print(e)

# Get file by name


@app.route('/getFile', methods=['POST'])
@cross_origin()
def getFile():
    try:
        model = json.loads(request.data)
        path = model['filename']
        print(DOWNLOAD_DIRECTORY, path)
        return send_from_directory(DOWNLOAD_DIRECTORY, path, as_attachment=False)
    except Exception as e:
        print("ERROR", e)
        return "406"

# Return list of files to load dropdown





# ------------
# AI ENDPOINTS

@app.route('/generate')
@cross_origin()
def to_generate():
    midi_files = []

    try:

        # Write 0 in IsGenerated.txt file
        f1 = open("DidGenerate.txt", 'w')
        f1.write("0")
        f1.close()

        # Write 0 in IsParsed.txt file
        f2 = open("IsParsed.txt", 'w')
        f2.write("0")
        f2.close()

        # print("IsGenerated.txt and IsParsed.txt where written with message 0")
        # msg("IsGenerated.txt and IsParsed.txt where written with message 0")
        time.sleep(1.0)
    
        shutil.rmtree('./model/output_uncondition')
        shutil.rmtree("./model/Output_Uncondtitionl_MIDI")
        os.mkdir('./model/output_uncondition')
        os.mkdir("./model/Output_Uncondtitionl_MIDI")

        print("Output folders were cleaned")
        time.sleep(1.0)

        # os.system('py -m pip install numpy --upgrade')

        ##########
        # GENERATE
        print("executing generate.py")
        timerInit = time.perf_counter()
        subprocess.call(["python", "./model/generate.py", "--inference_config",
                        "./model/inference_config/inference_unconditional.yml"])

        timerGenerated = time.perf_counter()

        # Check asynchronously if IsGenerated.txt is 1
        # os.chdir('..\\flask-server')
        file1 = open('DidGenerate.txt')
        didGenerate = file1.readline()
        if didGenerate == "1":
            timerGenerated = time.perf_counter()
            print("Generation done. It took ",
                  timerGenerated - timerInit, " seconds")

        cont = 0
        while didGenerate == "0":
            time.sleep(3.0)
            file1.close()
            file1 = open('DidGenerate.txt')
            didGenerate = file1.readline()
            if didGenerate == "0":
                print("not generated yet...")
            else:
                timerGenerated = time.perf_counter()
                print("Generation done. It took ",
                      timerGenerated - timerInit, " seconds")
            cont = cont + 1
            # print(cont)

        # os.system('py -m pip install numpy===1.22.0 --user')
        ######################
        # PARSE GENERATED MIDI
        print("executing music_encoder.py")
        # os.chdir('..\model')
        timerInit = time.perf_counter()
        subprocess.call(["python", "./data/music_encoder.py", "--input_folder", "./model/output_uncondition",
                        "--output_folder", "./model/Output_Uncondtitionl_MIDI", "--mode", "to_midi"])

        # Check asynchronously if IsParsed.txt is 1
        # os.chdir('..\\flask-server')
        file2 = open('IsParsed.txt')
        isParsed = file2.readline()
        timerParsed = time.perf_counter()

        if isParsed == "1":
            timerParsed = time.perf_counter()
            print("Parsing txt to MIDI done. It took ",
                  timerParsed - timerInit, " seconds")

        cont = 0
        while isParsed == "0":
            time.sleep(3.0)
            file2.close()
            file2 = open('IsParsed.txt')
            isParsed = file2.readline()
            if isParsed == "0":
                print("not parsed yet...")
            else:
                print("Parsing txt to MIDI done. It took ",
                      timerParsed - timerInit, " seconds")
            cont = cont + 1
            # print(cont)

        return "200"
    except Exception as e:
        print("ERROR:", e)
        return e

# Update inference_config file
@app.route('/config_inference', methods=['POST'])
@cross_origin()
def config_inference():
    
    try:
        record = json.loads(request.data)
        memoryLength = int(record['memoryLength'])
        numberOfFiles = record['numberOfFiles']
        temperature = record['temperature']
        print ("memoria", memoryLength)
        dict_file = {
            "MODEL": {
                "model_directory": "model/exp_dir/jazzharm1/test",
                "memory_length": memoryLength,
                "checkpoint_name": "checkpoint_300.pt",
                "debug": False
            },
            "SAMPLING": {
                "technique": "topk",
                "threshold": 32.0,
                "temperature": temperature
            },
            "INPUT": {
                "time_extension": False,
                "conditional_input_melody": "Null",
                "num_conditional_tokens": 50,
                "exclude_bos_token": True,
                "num_midi_files": numberOfFiles,
                "num_empty_tokens_to_ignore": 0,
                "conditional_duration": 22
            },
            "OUTPUT": {
                "output_txt_directory": "model/output_uncondition"
            },
            "GENERATION": {
                "generation_length": 1024,
                "generation_duration": 30,
                "duration_based": False
            }
        }
        print (dict_file)
        with open('./model/inference_config/inference_unconditional.yml', 'w') as file:
            documents = yaml.dump(dict_file, file, allow_unicode=True)
        f = open('./model/inference_config/inference_unconditional.yml', "r")
        return '200'

    except Exception as ex:
        print(ex)
        return '406'

@app.route('/', methods=['GET'])
@cross_origin()
def defect():
    return 'Hola'


@app.route('/listMidiFiles/')
@cross_origin()
def ListMidiFiles():
    try:
        filenames = os.listdir('./model/Output_Uncondtitionl_MIDI')
        return filenames
    except Exception as e:
        print(e)
        return "406"
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5000,ssl_context=context)