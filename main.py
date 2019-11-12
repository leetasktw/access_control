import cv2
import time
import json
from datetime import datetime
import face_recognition
import argparse
import pickle
import imutils
from imutils.video import VideoStream
from linebot import LineBotApi
from linebot.models import *
from linebot.exceptions import LineBotApiError
from imgurpython import ImgurClient
import paho.mqtt.client as mqtt


# *********************************************************************
# MQTT 組態設定

MQTT_SERVER = "soldier.cloudmqtt.com"
MQTT_USERNAME = "byxigwdy"
MQTT_PASSWORD = "4X8YiIXxSGiK"
MQTT_PORT = 12571
MQTT_ALIVE = 60

# *********************************************************************

ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True, help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))


def send_mqtt(topic, message):
    client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    client = mqtt.Client(client_id)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    client.publish(topic, message, qos=0, retain=False)


# 人臉拍照
def face_shot(filename):
    isCnt = False    
    print("開啟攝影機中...")
    vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

    while True:
        frame = vs.read()
        orig = frame.copy()
        frame = imutils.resize(frame, width=640)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        
        boxes = face_recognition.face_locations(rgb, model='hog')        

        if len(boxes):
            if isCnt == False:
                t1 = time.time()
                isCnt = True
            cnter = 2 - int(time.time() - t1)
            for (top, right, bottom, left) in boxes:                
                cv2.rectangle(
                        frame, (left, top), (right, bottom),
                        (0, 0, 255), 2)
                cv2.putText(
                        frame, str(cnter),
                        (left + int((right - left) / 2), top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)
            if cnter == 0:
                isCnt = False
                filename = datetime.now().strftime(
                        '%Y-%m-%d %H_%M_%S')
                cv2.imwrite(filename + '.jpg', orig)
                cv2.destroyAllWindows()
                vs.stop()
                break
        else:
            isCnt = False

        cv2.imshow('Frame', frame)
        k = cv2.waitKey(1)
        if k == ord('q') or k == ord('Q'):
            cv2.destroyAllWindows()
            vs.stop()
            break


    return filename


# 臉部辨識
def face_recognize(filename):
    data = pickle.loads(open(args["encodings"], "rb").read())
    image = cv2.imread(filename + '.jpg')
    if image.shape[1] > 640:
        image = imutils.resize(image, width=640)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print("臉部辨識中...")
    boxes = face_recognition.face_locations(rgb, model='hog')
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.3)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1
            name = max(counts, key=counts.get)
        names.append(name)
        print('確認身分為: ' + names[0])

    try:
        if names[0] != 'Unknown':
            send_mqtt('Door/Lock', 'open')
            link = upload_photo(filename + '.jpg')
            send_log(filename, 'Known', names[0], link)
        else:
            link = upload_photo(filename + '.jpg')
            send_message(link)
            send_log(filename, 'Unknown', names[0], link)
    except IndexError:
        print('發生錯誤，請再試一次')


# 上傳陌生人圖檔
def upload_photo(image):
    client_id = '76dfe2bb62f2011'
    client_secret = '0f9a38b191a63a1f3326a4f3adafe4e906e63b28'
    access_token = 'b0ea685b45331131a48d1d9d7fb23b318385d145'
    refresh_token = '57be9f3bb90134ba0d6e379fafff10853c1358f5'

    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    album = None

    config = {
        'album': album,
    }
    print("上傳圖檔中... ")
    image = client.upload_from_path(image, config=config, anon=False)
    print("完成")


    return image['link']


# 透過LineBot傳送訊息
def send_message(link):
    Channel_Access_Token = 'LLc+Ap7TmKlo/ZRhiXGdi83elssVe/SopnwlZTgSHsFYTeUqpjqB9Ylnwuv7rCc+DVX94ejqpJgjT1q7K5lMVu1lfIr6BobsVQwLRH3FchA/69neiO5KlW/JywGrgWcFIhSVGn6qJpPEBPzqieTNNAdB04t89/1O/w1cDnyilFU='
    To = 'C75e801944e58ba69dd0944e43549086d'

    line_bot_api = LineBotApi(Channel_Access_Token)

    try:
        image_message = ImageSendMessage(
            original_content_url=link,
            preview_image_url=link
        )
        buttons_template = TemplateSendMessage(
            alt_text='偵測到陌生人',
            template=ButtonsTemplate(
                title='陌生人訪客',
                text='請選擇如何處置',
                actions=[
                    MessageTemplateAction(
                        label='開門',
                        text='開門'
                    ),
                    MessageTemplateAction(
                        label='警鈴',
                        text='警鈴'
                    )
                ]
            )
        )
        line_bot_api.push_message(To, image_message)
        line_bot_api.push_message(To, buttons_template)
    except LineBotApiError as e:
        raise e


# 上傳訊息至資料庫
def send_log(date, status, name, link):
    data = {"data":{"tag":"gate", "date":date, "recognize":status, "people":name, "img":link}}
    json_str = json.dumps(data)
    send_mqtt('Sensor/Temperature/Room1', json_str)


# 主程式
def main():
    try:
        while True:
            filename = ''
            unidentified = face_shot(filename)
            if unidentified != '':                
                face_recognize(unidentified)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()


main()
