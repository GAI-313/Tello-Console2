from console import Console
import cv2

drone = Console()
drone.stream(True)
drone.downvision(False)

fw,fh = drone.FRAME_WIDTH // 2, drone.FRAME_HEIGHT // 2
try:
    while True:
        frame = drone.frame
        if drone.drone_type == "TELLO-EDU":
                tof, battery, roll, pitch, yaw = drone.get_status('tof', 'battery', 'roll', 'pitch', 'yaw')

                cv2.putText(frame,
                        text="BATTERY : %d"%(battery),
                        org=(10,20),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.8,
                        color=(0, 255, 0),
                        thickness=2,
                        lineType=cv2.LINE_4)
                cv2.putText(frame,
                        text="%d"%(yaw),
                        org=(fw,20),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.8,
                        color=(0, 255, 0),
                        thickness=2,
                        lineType=cv2.LINE_4)
                cv2.putText(frame,
                        text="TOF : %d"%(tof),
                        org=(10,45),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.8,
                        color=(0, 255, 0),
                        thickness=2,
                        lineType=cv2.LINE_4)

                if 30 >= battery:
                        cv2.putText(frame,
                                        text="LOW BATTERY !",
                                        org=(fw-100,drone.FRAME_HEIGHT-30),
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                        fontScale=0.8,
                                        color=(0, 0, 255),
                                        thickness=2,
                                        lineType=cv2.LINE_4)
                                        
                        cv2.ellipse(frame,
                                (fw,fh),
                                (100,0),
                                roll,0,90,
                                color=(0,255,0),
                                thickness=1)
                        cv2.ellipse(frame,
                                (fw,fh),
                                (100,0),
                                180+roll,0,90,
                                color=(0,255,0),
                                thickness=1)

                        cv2.line(frame,
                                pt1=(fw, fh-10),
                                pt2=(fw, fh+10),
                                color=(0, 255, 0),
                                thickness=2,
                                lineType=cv2.LINE_4,
                                shift=0)
                        cv2.line(frame,
                                pt1=(fw-10, fh),
                                pt2=(fw+10, fh),
                                color=(0, 255, 0),
                                thickness=2,
                                lineType=cv2.LINE_4,
                                shift=0)

                        cv2.line(frame,
                                pt1=(fw-50, fh-pitch),
                                pt2=(fw+50, fh-pitch),
                                color=(0, 255, 0),
                                thickness=1,
                                lineType=cv2.LINE_4,
                                shift=0)
        
        cv2.imshow('camera', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    drone.clean()
except KeyboardInterrupt:
    drone.land()