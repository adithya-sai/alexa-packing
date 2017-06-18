from flask import Flask
from flask import jsonify
from flask import request
from pymongo import MongoClient
from flask_cors import CORS, cross_origin


client=MongoClient()
db=client.alexadb
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
  return 'Hello!'

@app.route('/test')
def test1():
  itinerary_col = db.itinerary
  output = {}
  for s in itinerary_col.find():
    output['duration'] = s['duration']
    output['recommendations'] = s['recommendations']
    output['destination'] = s['destination']
    output['weather'] = s['weather']
  return jsonify(output)


@app.route('/get_checklist_alexa')
def test():
  itinerary_col = db.itinerary
  checklist_col = db.checklist
  for i in checklist_col.find():
	checklist_true = i['true']
	checklist_false = i['false']
  
  checklist = checklist_true + checklist_false

  for i in itinerary_col.find():
 	reco = i['recommendations']
  
  reco = list(set(reco) - set(checklist))
  
  output ={}

  for s in itinerary_col.find():
	output['destination'] = s['destination']
	output['weather'] = s['weather']
	output['duration'] = s['duration']
	output['recommendations'] = reco
	output['checklist'] = checklist_false
  return jsonify(output)

@app.route('/send_checklist',methods=['POST'])
@cross_origin()
def put():
  checklist=db.checklist
  jsonresp=request.get_json(force=True)
  new_true = jsonresp['true']
  new_false = jsonresp['false']
  checklist.remove({})
  checklist.insert({"true":new_true,"false":new_false})  
  return 'OK'

@app.route('/get_checklist_app')
def get_checklist():
	checklist = db.checklist
	output = {}
	for c in checklist.find():
		output['true'] = c['true']
		output['false'] = c['false']
	return jsonify(output)

@app.route('/update_checklist',methods=['POST'])
def update_checklist():
  item = request.data
  collection = db.checklist
  checklist = collection.find_one({})
  checklist_false = checklist['false']
  checklist_false.remove(item)
  checklist_true = checklist['true']
  checklist_true.append(item)
  collection.update_one({},{"$set":{"true":checklist_true,"false":checklist_false}})
  return 'OK'

if __name__ == '__main__':
  app.run()
