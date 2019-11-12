# 人臉拍照
def face_shot(filename):
    isCnt = False
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    detector.load('haarcascade_frontalface_default.xml')
    print("開啟攝影機中...")
    vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

    while True:
        frame = vs.read()
        orig = frame.copy()
        frame = imutils.resize(frame, width=400)
        rects = detector.detectMultiScale(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
            minNeighbors=3, minSize=(100, 100))

        if len(rects) == 1:
            if isCnt == False:
                t1 = time.time()
                isCnt = True
            cnter = 1 - int(time.time() - t1)
            for (x, y, w, h) in rects:
                cv2.rectangle(
                        frame, (x, y), (x+w, y+h),
                        (0, 255, 255), 2)
                cv2.putText(
                        frame, str(cnter),
                        (x+int(w/2), y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 2)
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