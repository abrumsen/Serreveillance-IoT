from flask import Flask, jsonify, request, abort
#import pymongo

#mongoclient = pymongo.MongoClient("mongodb://10.43.26.51:27017/")
#db = mongoclient["MQTT-Data"]
#col = db["USERS"]
API_KEY = "test"
AUTHORIZED_CARDS = ["validcard"]

app = Flask(__name__)
@app.route('/auth', methods=['GET']) # Requests should look like .../auth?id=<id>&client=<client>
def get_auth():
    try:
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            abort(401) # Unauthorized api key
        scanned_card = request.args.get("id")
        client = request.args.get("client")
        if scanned_card in AUTHORIZED_CARDS: # Authorized api key and card id : should be done with a DB query
            response = {"scannedCardId" : scanned_card, "isAuthorized" : True, "user": client}
            return jsonify(response)
        else:
            abort(401) # Unauthorized card id

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=False)