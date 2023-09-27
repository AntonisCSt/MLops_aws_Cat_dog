# libraries
import os
import pickle
import logging
import numpy as np
import pandas as pd
#import requests
from flask import Flask, jsonify, request
from collection_mongodb import collection_mongo_cluster

app = Flask('Smoke_detection')

collection = collection_mongo_cluster()
#temporarly until model
filename = './prediction_service/initial_rf.sav'
loaded_model = pickle.load(open(filename, 'rb'))

df_columns = ['UTC', 'Temperature[C]', 'Humidity[%]', 'TVOC[ppb]', 'eCO2[ppm]',
       'Raw H2', 'Raw Ethanol', 'Pressure[hPa]', 'PM1.0', 'PM2.5', 'NC0.5',
       'NC1.0', 'NC2.5', 'CNT']

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
