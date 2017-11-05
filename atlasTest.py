import pymongo
import datetime
import pprint
from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4

from flask import Flask
from flask import jsonify
from flask import request


app = Flask(__name__)

client = pymongo.MongoClient("mongodb://giles53716:A@cluster0-shard-00-00-ztwly.mongodb.net:27017,cluster0-shard-00-01-ztwly.mongodb.net:27017,cluster0-shard-00-02-ztwly.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/star', methods=['GET'])
def get_all_stars():
  db = client.stars

  star = db.stars

  output = []

  for s in star.find():
    output.append({'name' : s['name'], 'distance' : s['distance']})

  return jsonify({'result' : output})

@app.route('/star/<name>', methods=['GET'])
def get_one_star(name):
  db = client.stars

  star = db.stars
  s = star.find_one({'name' : name})
  if s:
    output = {'name' : s['name'], 'distance' : s['distance']}
  else:
    output = "No such name"
  return jsonify({'result' : output})

@app.route('/star', methods=['POST'])
def add_star():

  db = client.stars
  stars = db.stars

  name = request.json['name']
  distance = request.json['distance']

  star = {'name' : name, 'distance' : distance}
  star_id = stars.insert_one(star).inserted_id


  new_star = stars.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "./atlasTest/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print("=== Form Data ===")
    for key, value in list(form.items()):
        print(key, "=>", value)

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))


@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "uploadr/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template("files.html",
        uuid=uuid,
        files=files,
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')







def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))

