import cv2
import time

avg = 0
for i in range(0,50):
    video_capture = cv2.VideoCapture(0)
    # Check success
    if not video_capture.isOpened():
            raise Exception("Could not open video device")
    # Read picture. ret === True on success

    start = time.time()
    ret, frame = video_capture.read()

#while(True):
#    cv2.imshow('img1',frame)
#    if cv2.waitKey(1) & 0xFF == ord('y'):
#        cv2.imwrite('images/c1.png', frame)
#        cv2.destroyAllWindows()
#        break
# Close device
    cv2.imwrite('image.png', frame)
    video_capture.release()
    end = time.time()
    avg = avg + (end-start)

    #video_capture.release()
print(avg/i)
