from __future__ import print_function, division
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader

from pymongo import MongoClient
import json
import os
from bson import Binary, Code
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__))  , 'dbconfig.json')

def get_config():
    with open(file_path) as config_file:    
        config = loads(config_file.read())
        return config

def get_db_string():
    config = get_config()
    db_string = ""
    
    if config["username"]:
        db_string = "mongodb://{0}:{1}@{2}/{3}".format(config["username"], config["password"], config["url"], config["db"])
    else:
        db_string = "mongodb://{0}/{1}".format(config["url"], config["db"])

    return db_string

def get_db_client():
    client = MongoClient(get_db_string())
    db = client[get_config()["db"]]
    return db

def index(request):
    template = loader.get_template('present_testcase/index.html')
    
    db = get_db_client()
    testcase_ids = list( db["nba_prediction_result"].find({}, {"_id": 1, "parameters.model": 1}) )
    
    testcase_names = []
    for i in range( len(testcase_ids) ):
        testcase_names.append({
            "name": "testcase " + str(i + 1) + " / " + testcase_ids[i]["parameters"]["model"],
            "id": str(testcase_ids[i]["_id"]) 
        })
    
    print(testcase_names)
    context = {
        "testcases": testcase_names
    }
    return HttpResponse(template.render(context, request))

def detail(request):

    template = loader.get_template('present_testcase/testcase_detail.html')
    id = request.GET.get('id', '')
    db = get_db_client()
    testcase = db["nba_prediction_result"].find_one({"_id": ObjectId(id)} )

    parameters = testcase["parameters"]
    parameters["time_weight"] = str(parameters["time_weight"])
    parameters["seasons"] = json.dumps(parameters["seasons"])

    summaries = sorted(testcase["summaries"], key= lambda x: x["summary"]["accuracy"], reverse=True )
    

    details = []
    i = 0
    for summary in summaries:
        name = "Models: {0}, Time Weight: {1}, Threshold: {2}, Accuracy: {3:.2f}".format(
            summary["summary"]["model"],
            str(summary["summary"]["time_weight"]),
            str(summary["summary"]["threshold"]),
            summary["summary"]["accuracy"]
        )
         
        detail_temp = []
        for tc in summary["testcases"]:
            for game in tc["prediction"]:
                game["season"] = tc["season"]
                detail_temp.append(game)

        details.append({
            "id": "testcase-detail-" + str(i),
            "name": name,
            "games": detail_temp
        })

        i += 1
    context = {
        "id": id,
        "testcase": str(testcase),
        "parameters": parameters,
        "summaries": summaries,
        "details": details
    }
    return HttpResponse(template.render(context, request))

def about(request):

    template = loader.get_template('present_testcase/about.html')
    context = { }
    return HttpResponse(template.render(context, request))

def about(request):

    template = loader.get_template('present_testcase/predict.html')
    context = { }
    return HttpResponse(template.render(context, request))


