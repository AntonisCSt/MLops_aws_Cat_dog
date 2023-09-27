from pymongo.mongo_client import MongoClient
from config import MONGO_PASS,MONGO_USER
import certifi
import logging 

def collection_mongo_cluster():
    ## Reference: https://stackoverflow.com/questions/54484890/ssl-handshake-issue-with-pymongo-on-python3
    ca = certifi.where()

    uri = "mongodb+srv://"+MONGO_USER+":"+MONGO_PASS+"@cluster0.lrojtko.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri,tlsCAFile=ca)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        logging.info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        logging.info(e)

    db = client.get_database('prediction_service')
    collection = db.get_collection('data')

    return collection

def test_mongo_database(collection:object):

    post_example = {"_id":"test_id","test_value1":1,"name":'Tony'}

    collection.insert_one(post_example)
    test_result = collection.find_one({"_id":"test_id"})
    logging.info(f"test_result: {test_result}")
    collection.delete_one({"_id":"test_id"})


if __name__ == '__main__':
    collection = collection_mongo_cluster()
    test_mongo_database(collection)
