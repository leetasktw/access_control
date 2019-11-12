import paho.mqtt.client as mqtt
import pigpio
import time


# *********************************************************************
# MQTT 組態設定

MQTT_SERVER = "soldier.cloudmqtt.com"
MQTT_USERNAME = "byxigwdy"
MQTT_PASSWORD = "4X8YiIXxSGiK"
MQTT_PORT = 12571
MQTT_ALIVE = 60
MQTT_TOPIC = "Door/Lock"

# *********************************************************************
# 執行程式前須先執行 sudo pigpiod
PWM_CONTROL_PIN = 18
PWM_FREQ = 50

pi = pigpio.pi()

def client_loop():
    client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    client = mqtt.Client(client_id)    # ClientId不能重複，所以使用當前時間
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)    # 必須設置，否則會返回「Connected with result code 4」
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    client.loop_forever()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)    # 訂閱主題

def on_message(client, userdata, msg):
    str = msg.payload.decode("utf-8")
    if str == 'open':
        pi.hardware_PWM(PWM_CONTROL_PIN, PWM_FREQ, angle_to_duty_cycle(180))
        time.sleep(2)
        pi.hardware_PWM(PWM_CONTROL_PIN, PWM_FREQ, angle_to_duty_cycle(90))

def angle_to_duty_cycle(angle=0):
    duty_cycle = int(500 * PWM_FREQ + (1900 * PWM_FREQ * angle / 180))
    return duty_cycle

if __name__ == '__main__':
    client_loop()
