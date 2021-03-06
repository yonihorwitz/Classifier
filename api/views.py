from datetime import datetime
from flask import Flask, render_template, request, Response, jsonify
from pymongo import errors
from bson.json_util import dumps
from . import app, db, executor
import time
import random

# @app.route("/")
# def home():
#    return render_template("home.html")

# @app.route("/about/")
# def about():
#    return render_template("about.html")

# @app.route("/contact/")
# def contact():
#    return render_template("contact.html")

# @app.route("/hello/")
# @app.route("/hello/<name>")
# def hello_there(name = None):
#    return render_template(
#        "hello_there.html",
#        name=name,
#        date=datetime.now()
#    )


def classify(keyword):
    for i in range(10):
        print("Insert!", keyword)
        label = "UNKNOWN"
        if random.randint(0, 1) == 1:
            label = "KWS_KERIDOS"
        else:
            label = "KWS_KERIDOS_YG"
        db.classifications.insert_one(
            {"index": i, "keyword": keyword, "label": label})
        time.sleep(1)
    print("Done!")
    db.batches.find_one_and_update(
        {"keyword": keyword}, {'$set': {"status": "done"}})


@ app.route("/api/data")
def get_data():
    return '{ \"message\": \"hello\" }'


@ app.route("/submitBatch", methods=['POST'])
def submitBatch():
    kw = request.get_json().get("keyword")
    db.batches.insert_one({"keyword": kw, "status": "working"})
    executor.submit(classify, kw)
    return {"message": "Batch created"}


@ app.route("/batches", methods=["GET"])
def getBatches():
    result = []
    for b in db.batches.find():
        result.append({'keyword': b['keyword']})
    return jsonify(result)


@ app.route("/getClassifications/<keyword>/<length>/")
def getClassifications(keyword, length):
    def generate():
        status = db.batches.find_one({"keyword": keyword})["status"]
        classes = db.classifications.find(
            {"index": {"$gte": int(length)}, "keyword": keyword})
        yield bytes(dumps(classes), encoding='utf8')
        if status != "done":
            try:
                for insert_change in db.classifications.watch([{'$match': {'operationType': 'insert'}}]):
                    # status = db.batches.find_one(
                    #    {"keyword": keyword})["status"]
                    #str = ""
                    # if classes.count() > 0:
                    #    str = ","
                    #str = str + dumps(insert_change["fullDocument"])
                    print(insert_change)
                    yield bytes(dumps(insert_change["fullDocument"]), encoding='utf8')
            except errors.PyMongoError as py_mongo_error:
                print('Error in Mongo watch: %s' %
                      str(py_mongo_error))
    return Response(generate())

    # print("Batch", batch)
    # print("classes", dumps(classes))
    # return
