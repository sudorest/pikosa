import os
from os import path
from uuid import uuid4

from PIL import Image
from flask import Flask, render_template, request
from rembg import remove
from io import BytesIO

MAXFILES = 14
SAVEPATH = "./static/photo/"

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 90 * 1024 * 1024 # ~90Mb file limit

if not os.path.exists(SAVEPATH):
    os.makedirs(SAVEPATH)

def safe_filename(extension_with_dot):
    while True:
        filepath = f"{SAVEPATH}{uuid4()}{extension_with_dot}"
        if not path.isfile(filepath):
            return filepath

@app.route("/")
def main():
    return render_template("index.html", maxfiles=MAXFILES)

@app.route("/", methods=["POST"])
def mainpost():
    files = request.files.getlist("images[]")[:MAXFILES]
    returnfiles = []

    for x in files:
        extension = path.splitext(x.filename)[1]

        if not "." in extension:
            extension = "." + extension

        output = remove(x.read())
        filename = safe_filename(extension)
        img = Image.open(BytesIO(output))

        if img.mode == 'RGBA':
            white_bg = Image.new("RGB", img.size, (255, 255, 255))
            white_bg.paste(img, (0, 0), img)
            img = white_bg

        img.save(filename)

        returnfiles.append(filename)

    return returnfiles

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
