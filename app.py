from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response, jsonify
from werkzeug.utils import secure_filename
from shutil import rmtree
import os
from integrate import *
from preIntegrate import *
from PreProccesImage import *
from PIL import Image
from io import BytesIO
from textblob import TextBlob
import base64

UPLOAD_FOLDER = os.path.abspath("data_in/")
OUT_FOLDER = os.path.abspath("out/0.png/")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "" in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/icrgps", methods=["GET", "POST"])
def icrgps():
    if request.method == "POST":
        some_json = request.get_json()
        filename = '0.png'
        filename = secure_filename(filename)
        imagePath = (app.config["UPLOAD_FOLDER"]+"/"+filename)
        img = Image.open(BytesIO(base64.b64decode(some_json['base64'].split(',')[1])))
        img.save(imagePath,'png')
        fase1 = ''
        fase2 = ''
        fase3 = ''
        icr_main = ''
        probabilidad = ''
        rutaImage = 'data_in/'
        if(some_json['fase1A'] == True): #Hacer preprocesamiento
            preProces(rutaImage+filename)
            rutaImage = 'out/ocr/'
            img_aux = open(rutaImage+filename, 'rb')
            img_aux = img_aux.read()
            fase1 = str(base64.b64encode(img_aux))
            fase1 = str('data:image/png;base64,') + fase1[2:len(fase2) - 1]
        if(some_json['fase2A'] == True): #Hacer segmentacion
            rmtree("out/0.png")
            icr_main, prob = icrMain(rutaImage)  # aqui tambien sacar la probabilidad - la imagen de pepe tambien de agregarse al proceso
            probabilidad = prob
            img_aux = open(OUT_FOLDER+'/summary.png','rb')
            img_aux = img_aux.read()
            fase2 = str(base64.b64encode(img_aux))
            fase2 = str('data:image/png;base64,') + fase2[2:len(fase2)-1]
        else:
            icr_main, prob = icrPreIntegrate(rutaImage+'0.png')  # aqui tambien sacar la probabilidad - la imagen de pepe tambien de agregarse al proceso
            probabilidad = prob
        if(some_json['fase3A'] == True):
            fase3 = str(icr_main) #corrector ortografico
            d = open('out/file/1.txt', 'w')
            d.write(fase3)
            d.close()
            file1 = open('out/file/1.txt', 'r+')
            b=TextBlob(file1.read())
            icr_main = str(b.correct())
            file1.close()
        return jsonify({'textoReconocidofinal':str(icr_main),'fase1':fase1,'fase2':fase2,'fase3':fase3,'probabilidad':str(probabilidad)}),201
    else:
        return jsonify({"about":"hello icr - gps"})

@app.route("/icrv2", methods=["GET", "POST"])
def icrv2():
    if request.method == "POST":
        #if "outfile" not in request.files:
        #   return "This form has no file part."
        filesize = request.cookies.get('filesize')
        file = request.files["file"]
        f = file
        aux = file.filename
        #if f.filename == "":
        #   return "No file selected."
        if f and allowed_file(f.filename):
            f.filename = "0.png"
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            icr_main = icrMain('data_in/',True)
            return make_response(jsonify({"message":f"{aux} recognized", "textICR":f"{icr_main}"}),200)
        return make_response(jsonify({"message":f"{aux} no uploaded"}),400)
    return render_template('icr.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
