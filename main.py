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
            "MOISTURE_CHANNELS":    1,          
            "MOISTURE_THRESHOLD":   450,        
            "WATER_PUMP_GPIO":      23,         
            "WATERING_TIME":        5,          
        },
        {
            "NAME":                 "Flower2",
            "MOISTURE_CHANNELS":    2,
            "MOISTURE_THRESHOLD":   430,
            "WATER_PUMP_GPIO":      24,
            "WATERING_TIME":        4,
        },
    ]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "sensordata.db")

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
    for plant in PLANTS:        
        channel = plant['MOISTURE_CHANNELS']
        readvalue = mcp.read_adc(channel)
        writeMoistureDataToDB(readvalue,channel)
        if(readvalue>=plant['MOISTURE_THRESHOLD']):
            GPIO.setup(plant['WATER_PUMP_GPIO'], GPIO.OUT, initial=GPIO.LOW)
            time.sleep(plant['WATERING_TIME'])
            GPIO.output(plant['WATER_PUMP_GPIO'], GPIO.HIGH)

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
        writeDHTDataToDB(temperature,humidity,'DHT22_inner')
    else:
        print("Failed to retrieve data from humidity sensor")
    

    time.sleep(0.5)

while True:
    GPIO.setwarnings(False)
    watering()

