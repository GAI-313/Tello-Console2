from console import Console
import cv2
import os
import glob
import subprocess

class CreateModel:
    def __init__(self):
        self.pos_path = os.getcwd() + '/pos/'
        self.neg_path = os.getcwd() + '/neg/'

        self.pos_window = 'pos window'
        self.neg_window = 'neg window'

        self.clicked_pos = []
    
    def recording_pos(self, downvision):
        def _cb_mouse(event, x, y, flag, param):
            show_img = param['img']
            
            h, w = show_img.shape[0], show_img.shape[1]

            if event == cv2.EVENT_RBUTTONDOWN:
                if len(self.clicked_pos) > 0: self.clicked_pos.pop()
            elif event == cv2.EVENT_LBUTTONDOWN:
                self.clicked_pos.append([x,y])

            cv2.line(show_img, (x, 0), (x, h), (255, 0, 0), 1)
            cv2.line(show_img, (0, y), (w, y), (255, 0, 0), 1)

            if len(self.clicked_pos) == 1:
                cv2.rectangle(show_img, (self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                        (x,y),
                                        (0,0,255),
                                        1)
            elif len(self.clicked_pos) == 2:
                cv2.rectangle(show_img, (self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                        (self.clicked_pos[1][0], self.clicked_pos[1][1]),
                                        (0,255,0),
                                        2)
            
            cv2.imshow('CAMERA', show_img)

        drone = Console()

        drone.stream(True)
        drone.downvision(downvision)
        
        cv2.namedWindow('CAMERA')

        recording_flag = False
        file_num = 0
        pos_list = []

        while True:
            frame = drone.frame
            show_frame = frame.get().copy()
            
            param = {'img':show_frame}

            if len(self.clicked_pos) == 2:
                cv2.rectangle(show_frame, (self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                        (self.clicked_pos[1][0], self.clicked_pos[1][1]),
                                        (0,255,0),
                                        2)

            cv2.setMouseCallback('CAMERA', _cb_mouse, param)

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                break
            elif key == 13:
                if not recording_flag:
                    recording_flag = True
                    
                else:
                    recording_flag = False


            if recording_flag and len(self.clicked_pos) == 2:
                cv2.putText(show_frame,
                                "Recording Now ...",
                                (10,20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,0,255),
                                2)
                cv2.imwrite(self.pos_path + "%d.jpg"%file_num, frame)
                pos_list.append([self.clicked_pos[0][0], self.clicked_pos[0][1],
                                abs(self.clicked_pos[1][0] - self.clicked_pos[0][0]),
                                abs(self.clicked_pos[1][1] - self.clicked_pos[0][1])])
                file_num += 1
                
            elif recording_flag:
                cv2.putText(show_frame,
                                "Please Create BBox!",
                                (10,20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,0,255),
                                2)
                
            cv2.imshow('CAMERA', show_frame)

        drone.clean()

        poslist = self.pos_path + 'poslist.txt'

        with open(poslist, 'w') as file:
            file_num = 0
            for pos in pos_list:
                #text = 'pos/' + str(file_num) + '.jpg' + ' ' + '1' + ' ' + str(pos[0]) + ' ' +str(pos[1]) + ' ' +str(pos[2]) + ' ' +str(pos[3]) + '\n'
                text = str(file_num) + '.jpg' + ' ' + '1' + ' ' + str(pos[0]) + ' ' +str(pos[1]) + ' ' +str(pos[2]) + ' ' +str(pos[3]) + '\n'
                file.write(text)
                file_num += 1
        print('done.')
    
    def recording_neg(self, downvision):
        drone = Console()

        drone.stream(True)
        drone.downvision(downvision)

        recording_flag = False
        file_num = 0

        while True:
            frame = drone.frame
            show_frame = frame.copy()

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                break
            elif key == 13:
                if not recording_flag:
                    recording_flag = True
                    
                else:
                    recording_flag = False

            if recording_flag:
                cv2.putText(show_frame,
                                "Recording Now ...",
                                (10,20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,0,255),
                                2)
                cv2.putText(show_frame,
                                str(file_num),
                                (10,40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,0,255),
                                2)
                cv2.imwrite(self.neg_path + "%d.jpg"%file_num, frame)
                file_num += 1

            cv2.imshow('CAMERA', frame)

        drone.clean()

    def create_box(self):
        def _cb_mouse(event, x, y, flag, param):
            try:
                img = param['img']
                hidedoc = param["hide"]
                
                h, w = img.shape[0], img.shape[1]
                show_img = img.copy()

                cv2.line(show_img, (x, 0), (x, h), (255, 0, 0), 1)
                cv2.line(show_img, (0, y), (w, y), (255, 0, 0), 1)

                if hidedoc:
                    cv2.putText(show_img,
                                "Left Click : check a pose 1",
                                (10,10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,0),
                                1)
                    cv2.putText(show_img,
                                "Left Click again : define a box",
                                (10,25),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,0),
                                1)
                    cv2.putText(show_img,
                                "N key : save and next. if not box, skip this image.",
                                (10,40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,0),
                                1)
                    cv2.putText(show_img,
                                "H key : Hide this document.",
                                (10,55),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,0),
                                1)
                    cv2.putText(show_img,
                                "ESC key : Quit",
                                (10,70),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,0),
                                1)

                if event == cv2.EVENT_RBUTTONDOWN:
                    if len(self.clicked_pos) > 0: self.clicked_pos.pop()
                elif event == cv2.EVENT_LBUTTONDOWN:
                    self.clicked_pos.append([x,y])

                if len(self.clicked_pos) == 1:
                    cv2.rectangle(show_img, (self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                            (x,y),
                                            (0,0,255),
                                            1)
                                            
                elif len(self.clicked_pos) == 2:
                    cv2.rectangle(show_img, (self.clicked_pos[0][0], self.clicked_pos[0][1]),
                                            (self.clicked_pos[1][0], self.clicked_pos[1][1]),
                                            (0,255,0),
                                            2)
                    cv2.putText(show_img,
                                "Press N, save and next image.",
                                (self.clicked_pos[0][0], self.clicked_pos[0][1] - 15),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,255),
                                1)
                    cv2.putText(show_img,
                                "R click, recreate end point.",
                                (self.clicked_pos[0][0], self.clicked_pos[0][1] - 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,(0,255,255),
                                1)

                cv2.imshow(self.pos_window, show_img)
            except KeyboardInterrupt:
                raise KeyboardInterrupt("KeyboardInterrupt in _cb_mouse")

        try:
            files = glob.glob(self.pos_path + '*')
            txt_path = self.pos_path + 'poslist.txt'
            break_flag = False
            hidedoc_flag = True

            cv2.namedWindow(self.pos_window)

            f = open(txt_path, 'w')
            for file in files:
                if ".txt" in file:
                    pass
                else:
                    if break_flag:
                        break
                    img = cv2.imread(str(file))
                    param = {'img' : img,
                            'hide' : True}

                    cv2.imshow(self.pos_window, img)
                    cv2.setMouseCallback(self.pos_window, _cb_mouse, param)
                    while True:
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord("n"):
                            break
                        elif key == ord("h"):
                            if not param["hide"] : param["hide"] = True
                            else : param["hide"] = False
                        elif key == 27:
                            break_flag = True
                            break
                    if len(self.clicked_pos) == 2:
                        f.write(
                            file.replace(self.pos_path, "")+" "+"1"+" "+str(self.clicked_pos[0][0])+" "+
                                                                        str(self.clicked_pos[0][1])+" "+
                                                                        str(abs(self.clicked_pos[1][0] - self.clicked_pos[0][0]))+" "+
                                                                        str(abs(self.clicked_pos[1][1] - self.clicked_pos[0][1]))+" "+"\n"
                        )
                        self.clicked_pos = []
                
                cv2.destroyAllWindows()
            f.close()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()

    def generate_pos_vec(self):
        try:
            file = self.pos_path + 'poslist.txt'
            line = 0
            cmd = ['./opencv_createsamples', '-info',  './pos/poslist.txt', '-vec ', './vec/posvec.vec']
            with open(file, 'r') as f:
                line = len(f.readlines())
        except FileNotFoundError:
            print('Not found poslist.txt')

        if line >= 1000:
            cmd.append('-num ')
            cmd.append(str(line))

        print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, cwd=os.getcwd())
        print(result)
    
    def debug(self):
        # ファイルを読み込んで現在の内容を取得
        path = self.pos_path + 'poslist.txt'
        print(path)
        with open(path, 'r') as file:
            lines = file.readlines()

        new_lines = ["pos/" + line for line in lines]
        with open(path, 'w') as file:
            file.writelines(new_lines)


c = CreateModel()
#c.create_box()
#c.generate_pos_vec()
#c.debug()
c.recording_pos(True)
