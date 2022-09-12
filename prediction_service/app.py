# libraries
import os
import pickle
import logging
import numpy as np
import pandas as pd
#import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient

class columnDropperTransformer():
    def __init__(self,columns):
        self.columns=columns

    def transform(self,X,y=None):
        return X.drop(self.columns,axis=1)

    def fit(self, X, y=None):
        return self 

#import boto3

#AWS_SERVER_PUBLIC_KEY = os.getenv('AWS_SERVER_PUBLIC_KEY')
#AWS_SERVER_SECRET_KEY = os.getenv('AWS_SERVER_SECRET_KEY')

# enviroment parameters
#RUN_ID = os.getenv('RUN_ID', 'f96296ba6d4a4122ad13490bbde0bad2')
MONGODB_ADDRESS = os.getenv('MONGODB_ADDRESS', "mongodb://127.0.0.1:27017")
#EVIDENTLY_SERVICE_ADDRESS = os.getenv('EVIDENTLY_SERVICE', "http://127.0.0.1:5000")

#s3client = boto3.client('s3', 
#                        aws_access_key_id = AWS_SERVER_PUBLIC_KEY, 
#                        aws_secret_access_key = AWS_SERVER_SECRET_KEY,
#                        region_name = 'eu-west-3'
#                       )

#response = s3client.get_object(Bucket='mlflow-semicon-clf', Key=f'{RUN_ID}/artifacts/artifacts/model.pkl')

#body = response['Body'].read()
#body = 'initial_rf_pipe.sav'
#loaded_model = pickle.loads(body)
# import model
# loaded_model = mlflow.pyfunc.load_model(MODEL_FILE)

#temporarly until model
filename = 'initial_rf.sav'
loaded_model = pickle.load(open(filename, 'rb'))

df_columns = ['UTC', 'Temperature[C]', 'Humidity[%]', 'TVOC[ppb]', 'eCO2[ppm]',
       'Raw H2', 'Raw Ethanol', 'Pressure[hPa]', 'PM1.0', 'PM2.5', 'NC0.5',
       'NC1.0', 'NC2.5', 'CNT']
# flask application
app = Flask('Smoke_detection')
mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database('prediction_service')
collection = db.get_collection('data')


@app.route('/predict', methods=['POST'])
def predict():
    logging.info("Starting new prediction")
    row2 = request.get_json()
    row = row2.values()
    row = np.array(list(row)).reshape(1, -1)
    df = pd.DataFrame(row, columns=df_columns)
    df = df.drop(['PM2.5', 'NC0.5', 'NC1.0', 'NC2.5','CNT','UTC'], axis=1)
    #loaded_model = pickle.load(open('model.pkl', 'rb'))

    pred = int(loaded_model.predict(df))
    # pred = str(pred)
    result = {
        'Fire Alarm': pred,
    }
    logging.info("Saving data to mongodb and evidently service")
    save_to_db(row2, pred)
    #send_to_evidently_service(row2, pred)

    return jsonify(result)


def save_to_db(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    collection.insert_one(rec)


#def send_to_evidently_service(record, prediction):
#   rec = record.copy()
#    rec['prediction'] = prediction
#    requests.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/semicon", json=[rec])
#    logging.info(f"Logged data to evidently row:{rec}")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
