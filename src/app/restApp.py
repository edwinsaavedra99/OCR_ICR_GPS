from flask import Flask, request, jsonify
from flask_restful import Resource, Api
#from sqlalchemy import create_engine

app = Flask(__name__)
api = Api(app)

class GpsIcr(Resource):
    def get(self):
        return {'about':'hello'}
    def post(self):
        some_json = request.get_json()
        return {'you sent':some_json},201

api.add_resource(GpsIcr,'/gpsicr')

if __name__ == '__main__':
    app.run(debug=True)