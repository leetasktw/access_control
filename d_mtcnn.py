from mtcnn.mtcnn import MTCNN
# 人臉拍照
def face_shot(filename):
    isCnt = False
    detector = MTCNN()    
    print("開啟攝影機中...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)    

    while True:
        ret, frame = cap.read() 
        orig = frame.copy()       
        frame = imutils.resize(frame, width=400)
        rects = detector.detect_faces(frame)

        if len(rects) == 1:
            if isCnt == False:
                t1 = time.time()
                isCnt = True
            cnter = 1 - int(time.time() - t1)
            rects = rects[0]['box']        
            x = rects[0]
            y = rects[1]
            w = rects[2]
            h = rects[3]
            cv2.rectangle(frame, (x, y), (x+w, y+h),
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
                cap.release()
                break
        else:
            isCnt = False

        cv2.imshow('Frame', frame)
        k = cv2.waitKey(1)
        if k == ord('q') or k == ord('Q'):
            cv2.destroyAllWindows()
            cap.release()
            break


    return filename