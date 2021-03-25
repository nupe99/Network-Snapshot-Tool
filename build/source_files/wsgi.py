from flask import Flask, render_template, request, url_for, jsonify, send_file, make_response
from genie.testbed import load
import pymongo
import requests
import sys
import collect
import threading
import random
import comparing
import json
from bson import json_util
import os


#create and configure the app
app = Flask(__name__, static_folder="static")

@app.route("/", methods=['POST', 'GET'])
def home():
    client = pymongo.MongoClient()
    db = client['network_state']
    db_meta = db['MetaData']
    # Show a list of recent jobs
    if request.method == 'POST':
        form_deletes = request.form.getlist('net_deletes')
        print(form_deletes)
        for job in form_deletes:
            query = {"name": job}
            db_meta.delete_one(query)
            db.drop_collection(job)
    meta_jobs = db_meta.find()
    return render_template("start.html", jobs=meta_jobs)



@app.route("/gather_both", methods=['POST', 'GET'])
def gather_state():
    topology = '/var/www/logs/topology.yaml'
    #Create device list for form
    device_list = []
    testbed = load(topology)
    devices = testbed.devices
    for name in devices.keys():
        device_list.append(name)

    if request.method == 'POST':
        form_devices = request.form.getlist('net_devs')
        net_checks = request.form.getlist('net_checks')
        if not form_devices or not net_checks:
            return render_template("gather_input_error.html", device_list=device_list)

        # create random number for job ID. Ensure it's unique
        client = pymongo.MongoClient()
        db = client['network_state']
        db_meta = db['MetaData']
        while True:
            # create random number for job ID
            random_id = random.randint(1, 50000)
            job_id = f'Job_{random_id}'
            query = {"name": job_id}
            out = db_meta.count_documents(query)
            #If Job ID is unique then break out of loop
            if out == 0:
                break
            else:
                continue

        #Run state collection as a background task
        t1 = threading.Thread(target=collect.main, args=(form_devices, job_id, topology, net_checks))
        t1.start()

        return render_template("gather_both_res.html", device_list=device_list, job_id=job_id)
    else:
        return render_template("gather_both.html", device_list=device_list)


@app.route("/compare", methods=['POST', 'GET'])
def compare():
    client = pymongo.MongoClient()
    db = client['network_state']
    db_meta = db['MetaData']
    meta_jobs = db_meta.find()
    if meta_jobs.count() == 0:
        return render_template("compare.html", jobs=meta_jobs)
    if request.method == 'POST':
        form_compare = request.form.getlist('net_compares')
        if len(form_compare) == 2:
            results = comparing.compare(form_compare)
            return render_template("results.html", results=results)
        else:
            return render_template("compare-error.html", jobs=meta_jobs)

    else:
        return render_template("compare.html", jobs=meta_jobs)


@app.route("/api/list")
def get_jobs():
    client = pymongo.MongoClient()
    db = client['network_state']
    db_meta = db['MetaData']
    # Show a list of recent jobs
    meta_jobs = db_meta.find()
    jobs = {}
    jobs['jobs'] = {}
    for job in meta_jobs:
        job_name = job['name']
        jobs['jobs'][job_name] = {}
        jobs['jobs'][job_name].update(job)

    temp_json = json.dumps(json_util.dumps(jobs))
    jobs = json.loads(json_util.loads(temp_json))
    return jsonify(jobs)


@app.route("/api/delete", methods=['POST'])
def del_jobs():
    client = pymongo.MongoClient()
    db = client['network_state']
    db_meta = db['MetaData']
    # Show a list of recent jobs
    content = request.json
    print(content)
    for job in content['Jobs']:
        query = {"name": job}
        db_meta.delete_one(query)
        db.drop_collection(job)

    return jsonify({"status": "success"})


@app.route("/api/collect", methods=['POST'])
def gather_api():

    topology = '/var/www/logs/topology.yaml'
    #unpack POST elements
    content = request.json

    net_checks = content['Tasks']
    api_devices = content['Devices']

    # create random number for job ID
    random_id = random.randint(1, 50000)
    job_id = f'Job_{random_id}'

    #Run state collection as a background task
    t1 = threading.Thread(target=collect.main, args=(api_devices, job_id, topology, net_checks))
    t1.start()
    return jsonify({"status": "success", "job": job_id})


@app.route("/api/compare", methods=['POST', 'GET'])
def compare_api():
    #unpack POST elements
    if request.method == 'POST':
        content = request.json
        form_compare = content['Jobs']
        if len(form_compare) == 2:
            results = comparing.compare(form_compare)
            return jsonify(results), 201
        else:
            return jsonify({"status": "fail", "Message": "Request must contain exactly two jobs"}), 400
    else:
        return "Request must be a POST method"


@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      try:
        f = request.files['file']
        f.filename = "testbed.csv"
        f.save(f.filename)
        stream = os.popen('pyats create testbed file --path testbed.csv --output /var/www/logs/topology.yaml')
        output = stream.read()
        print(output)
        if 'topology.yaml' in output:
            return render_template('upload_success.html')
        else:
            return f'Error encountered while processing CSV file. Check format -- {output}'
      except Exception as e:
          print(f'Error encountered while processing CSV file -- {output}')
          return f'Error encountered while processing CSV file -- {output}'


@app.route('/download')
def downloadFile ():
    path = "/var/www/templates/testbed.csv"
    return send_file(path, as_attachment=True)

@app.route('/errors')
def errorFile ():

    return render_template("error_log.html")

@app.route('/help')
def help ():
    response = make_response(render_template('help.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context=('/var/www/server.crt', '/var/www/server.key'))



