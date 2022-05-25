from pymongo import MongoClient
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB = os.getenv('DB')
DB_TABLE = os.getenv('DB_TABLE')

class DB:
    def __init__(self, host=DB_HOST, db=DB, table=DB_TABLE):
        self.host = host
        self.db = db
        self.table = table
        self.connect()

    def connect(self):
        self.client = MongoClient(host=self.host, port=27017)
        self.client_db = self.client[self.db]
        self.client_table = self.client_db[self.table]

    def disconnect(self):
        self.client.close()

    def read_json(self, path):
        with open(path) as file:
            return json.load(file)

    def find(self, date):
        doc = self.client_table.find_one({"date": date})
        return doc

    def find_all(self, date):
        doc = self.client_table.find({"date": date})
        return doc

    def count(self, date):
        doc = self.client_table.count_documents({"date": date})
        return doc

    def delete(self, date):
        query = {"date": date}
        result = self.client_table.delete_one(query)
        result
        print(f"Data deleted: {result}")

    def update(self, date, json_data):
        query = {"date": date}
        data = {"$set": json_data}
        result = self.client_table.update_one(query, data)
        result
        print(f"Data updated: {result}")

    def insert(self, json_data):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.count(today) == 0:
            result = self.client_table.insert_one(json_data)
            result

            print(f"Data entered: {json_data}")
        else:
            self.update(today, json_data)
