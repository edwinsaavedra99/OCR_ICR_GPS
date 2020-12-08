from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response, jsonify
from werkzeug.utils import secure_filename
import os
from integrate import *
from PIL import Image
from io import BytesIO
#from base64 import b64decode,b64encode
import base64

UPLOAD_FOLDER = os.path.abspath("../data_in/")
OUT_FOLDER = os.path.abspath("../out/0.png/")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "" in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__, template_folder='../ui/templates', static_folder='../ui/static')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/icrv3", methods=["GET", "POST"])
def icrv3():
    if request.method == "POST":
        if "file" not in request.files:
            return "This form has no file part."
        f = request.files["file"]
        if f.filename == "":
            return "No file selected."
        if f and allowed_file(f.filename):
            f.filename = "0.png"
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("get_file", filename=filename))
        return "File not allowed"
    return render_template('reconocimiento.html')

@app.route("/icrgps", methods=["GET", "POST"])
def icrgps():
    if request.method == "POST":
        some_json = request.get_json()
        filename = '0.png'
        filename = secure_filename(filename)
        imagePath = (app.config["UPLOAD_FOLDER"]+"/"+filename)
        img = Image.open(BytesIO(base64.b64decode(some_json['base64'].split(',')[1])))
        img.save(imagePath,'png')
        icr_main,prob = icrMain() #aqui tambien sacar la probabilidad - la imagen de pepe tambien de agregarse al proceso
        fase1 = ''
        fase2 = ''
        fase3 = ''
        probabilidad = prob
        if(some_json['fase1A'] == True):
            fase1 = 'test1' #imagen de pepe
        if(some_json['fase2A'] == True):
            #imagen-segmentada
            img_aux = open(OUT_FOLDER+'/summary.png','rb')
            img_aux = img_aux.read()
            fase2 = str(base64.b64encode(img_aux))
            fase2 = str('data:image/png;base64,') + fase2[2:len(fase2)-1]
        if(some_json['fase3A'] == True):
            fase3 = 'test3' #textoreconocido-v1
        return jsonify({'textoReconocidofinal':icr_main,'fase1':fase1,'fase2':fase2,'fase3':fase3,'probabilidad':probabilidad}),201
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
            icr_main = icrMain()
            return make_response(jsonify({"message":f"{aux} recognized", "textICR":f"{icr_main}"}),200)
        return make_response(jsonify({"message":f"{aux} no uploaded"}),400)
    return render_template('icr.html')

@app.route("/icr", methods=["GET", "POST"])
def icr():
    if request.method == "POST":
        if "outfile" not in request.files:
            return "This form has no file part."
        f = request.files["outfile"]
        if f.filename == "":
            return "No file selected."
        if f and allowed_file(f.filename):
            #f.filename = "0.png"
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("get_file", filename=filename))
        return "File not allowed"
    return """
    <form method = "POST" enctype="multipart/form-data">
        <input type = "file" name ="outfile">
        <input type = "submit" vale="UPLOAD">
    </form>
    """


@app.route("/icr/imagen/<filename>")
def get_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == '__main__':
    app.run(debug=True)
