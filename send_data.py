import json
import uuid
from time import sleep
from datetime import datetime
import requests
from pyarrow import csv

table = csv.read_csv("sample.csv")
data = table.to_pylist()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


with open("target.csv", 'w') as f_target:
    
    for row in data:
        # print(max(0,int(row['Pass/Fail'])))
        row['id'] = str(uuid.uuid4())
        #alarm = row['Fire Alarm']
        #data = json.dumps(row, cls=DateTimeEncoder)
        # duration = str(duration)
        #f_target.write(f"{row['id']},{alarm}\n")
        print('#############################################################')
        data=json.dumps(row, cls=DateTimeEncoder)
        print(data)
        resp = requests.post(
            "http://192.168.2.103:9696/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(row, cls=DateTimeEncoder),
        ).json()
        print(f"prediction: {resp['Fire Alarm']}")
        sleep(0.5)

        #http://127.0.0.1:9696/predict