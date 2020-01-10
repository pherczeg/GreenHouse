import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import sqlite3
import os.path


PLANTS = [
        {
            "NAME":                 "Flower1",
            "MOISTURE_CHANNELS":    0,          
            "MOISTURE_THRESHOLD":   450,        
            "WATER_PUMP_GPIO":      23,         
            "WATERING_TIME":        1,          
        },
        {
            "NAME":                 "Flower2",
            "MOISTURE_CHANNELS":    1,
            "MOISTURE_THRESHOLD":   430,
            "WATER_PUMP_GPIO":      24,
            "WATERING_TIME":        1,
        },
    ]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "sensordata.db")
print(len(PLANTS))
# Set GPIO mode

GPIO.setmode(GPIO.BCM)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# DHT sensor configuration:
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

def writeMoistureDataToDB(value, sensor):
    with sqlite3.connect(db_path) as sqliteConnection:
        cursor = sqliteConnection.cursor()            
        sqlite_insert_query = "INSERT INTO 'moisturereadings' ('moisturelvl','date', 'sensor') VALUES ((?),datetime('now','localtime'),(?))"
        data_tuple = (value, sensor)
        count = cursor.execute(sqlite_insert_query,data_tuple)
        sqliteConnection.commit()
        print("Record inserted successfully into moisturereadings table ", cursor.rowcount)
        cursor.close()
def writeDHTDataToDB(temperature, humidity, device):
    with sqlite3.connect(db_path) as sqliteConnection:
        cursor = sqliteConnection.cursor()            
        sqlite_insert_query = "INSERT INTO 'dhtreadings' ('temperature','humidity','date', 'device') VALUES ((?),(?),datetime('now','localtime'),(?))"
        data_tuple = (temperature, humidity, device)
        count = cursor.execute(sqlite_insert_query,data_tuple)
        sqliteConnection.commit()
        print("Record inserted successfully into dhtreadings table ", cursor.rowcount)
        cursor.close()

def watering():
    for i in range(len(PLANTS)):        
        channel = PLANTS[i]['MOISTURE_CHANNELS']
        readvalue = mcp.read_adc(channel)
        writeMoistureDataToDB(readvalue,channel)
        print(readvalue, channel)
        if(readvalue>=PLANTS[i]['MOISTURE_THRESHOLD']):
            GPIO.setup(PLANTS[i]['WATER_PUMP_GPIO'], GPIO.OUT, initial=GPIO.LOW)
            time.sleep(PLANTS[i]['WATERING_TIME'])
            GPIO.output(PLANTS[i]['WATER_PUMP_GPIO'], GPIO.HIGH)
            print(PLANTS[i]['WATER_PUMP_GPIO'])
            print(PLANTS[i]['NAME'])

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
        writeDHTDataToDB(temperature,humidity,'DHT22_inner')
    else:
        print("Failed to retrieve data from humidity sensor")

while True:
    GPIO.setwarnings(False)
    watering()
    time.sleep(600)

