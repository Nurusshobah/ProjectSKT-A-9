#include <DHTesp.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* clientname = "node1";
const char* ssid = "ProjekSKT";
const char* password = "@okaygoogle@";
const char* mqtt_broker = "192.168.0.122";
const char* topic_node = "/node1";
long lastMsg = 0;
char kirim_data[50];
char topic_full[50];

#define port_broker 1883
#define pinDHT 2

WiFiClient node_SKT_ESP;
PubSubClient client(node_SKT_ESP);
DHTesp sensor;

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_broker, port_broker);
  sensor.setup(pinDHT, DHTesp::DHT11);
}

void setup_wifi() {

  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(clientname)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void ambil_data(float pdata[]){
  TempAndHumidity data_sensor = sensor.getTempAndHumidity();
  if (sensor.getStatus() != 0) {
    Serial.println("Error mengambil data DHT11: " + String(sensor.getStatusString()));
    pdata[0] = 0;
    pdata[1] = 0;
    pdata[2] = 0;   //status
    return;
  }
  else {
    Serial.println("Suhu: " + String(data_sensor.temperature) + "\tKelembapan: " + String(data_sensor.humidity));
    pdata[0] = data_sensor.temperature;
    pdata[1] = data_sensor.humidity;
    pdata[2] = 1;   //status
    return;
  }
}

void publish_data(float qdata[]){
  int count = 0;
  if(int(qdata[2]) != 1) Serial.println("Publish data ke broker gagal (Pengambil data Sensor)");
  else{
    while(count < 2){
      snprintf(kirim_data, sizeof kirim_data, "%.1f", qdata[count]);
      switch(count){
        case 0:
          strcpy(topic_full, topic_node);
          strcat(topic_full, "/suhu");
          break;
        case 1:
          strcpy(topic_full, topic_node);
          strcat(topic_full, "/kelembapan");
          break;
        default:
          Serial.println("Error");
      }
      if(client.publish(topic_full, kirim_data)){
        Serial.println("Publish Topik:" + String(topic_full) +"\t\tberupa data : " + String(kirim_data) + " ke Broker berhasil");
      }
      else Serial.println("Publish data ke broker gagal (Publish data Sensor)");
      count++;
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
   long now = millis();
   if(now - lastMsg > 5000){
    float data[2];
    lastMsg = now;
    
    Serial.println("");
    ambil_data(data);
    publish_data(data);
   }
}
