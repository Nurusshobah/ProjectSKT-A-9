import socket
import threading
import paho.mqtt.client as mqtt_client
import json
import datetime
import time
from flask import Flask, request
from pymongo import MongoClient
from flask_pymongo import PyMongo


data_sensor_kelembapan=""
data_sensor_suhu=''
client =''
client = MongoClient()
client = MongoClient('mongodb://localhost:27017/')
db = client['skt']


def handle_subcriber():
    sub = mqtt_client.Client()
    sub.connect("127.0.0.1", 1883)
    sub.subscribe("/#")
    sub.on_message = handle_message
    sub.loop_forever()

# Fungsi untuk handle message yang masuk

def handle_message(mqttc, obj, msg):
    global data_sensor_kelembapan,data_sensor_suhu,client
    ts = time.time()
    WaktuHost = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    topic = msg.topic
    NamaSensor=topic.replace("/","")
    value = msg.payload
    value=value.decode('ascii')
    try:
        if(NamaSensor=='node1suhu'):
            print(NamaSensor + "\t\t" + value + "\t" + WaktuHost)
            data_sensor_suhu= [{
                "NamaSensor":""+NamaSensor,
                "Value":""+(value)+"",
                "Waktu":""+WaktuHost+"",
                }]
            data_sensor_db = db['sensor_suhu']
            data_sensor_db.insert_many(data_sensor_suhu)
            with open ('data_sensor_suhu.json','w') as datasensorsuhu:
                datasensorsuhu.write(json.dumps(data_sensor_suhu))
                datasensorsuhu.close()
        else:
            print(NamaSensor + "\t" + value + "\t" + WaktuHost)
            data_sensor_kelembapan = [{
                "NamaSensor": "" + NamaSensor,
                "Value": "" + (value) + "",
                "Waktu": "" + WaktuHost + "",
            }]
            data_sensor_db = db['sensor_kelembapan']
            data_sensor_db.insert_many(data_sensor_kelembapan)

            with open ('data_sensor_kelembapan.json','w') as datasensokelembapan:
                datasensokelembapan.write(json.dumps(data_sensor_kelembapan))
                datasensokelembapan.close()

    except TypeError:
        pass


def restfull():
    app = Flask("Sensor")
    app.config['MONGO_DBNAME'] = 'skt'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/skt'
    mongo = PyMongo(app)

    @app.route('/sensor/suhu', methods=['GET'])
    def handle_get_suhu():
        sensor_suhu=mongo.db.sensor_suhu
        for doc in sensor_suhu.find():
            print(doc)
        return 'Nama Sensor\t :' + str(doc['NamaSensor']) + '\nValue\t\t :' + str(doc['Value']) + '°C\nWaktu\t\t :' + str(doc['Waktu'])

    @app.route('/sensor/humidity', methods=['GET'])
    def handle_get_kelembapan():
        sensor_kelembapan = mongo.db.sensor_kelembapan
        for doc in sensor_kelembapan.find():
            print(doc)
        return 'Nama Sensor\t :'+str(doc['NamaSensor'])+'\nValue\t\t :'+str(doc['Value'])+'%\nWaktu\t\t :'+str(doc['Waktu'])
    # Jalankan server Flask
    app.run(host='192.168.0.122', port=7777)



if __name__ == '__main__':  # Main
    t = threading.Thread(target=handle_subcriber)
    #t1=threading.Thread(target=restfull)
    t.start()
    restfull()
    #t1.start()
    t.join()
    #t1.join()