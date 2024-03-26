#!/usr/bin/env python3
import numpy as np
import socket # UDP通信を行うためのパケージ
import cv2 # 画像処理をするためのパッケージ
import time
import threading
import subprocess
import os
import sys
import traceback
import logging
import re
import asyncio

class Console():

    LOCAL_IP = '0.0.0.0'
    LOCAL_PORT = 8889
    VIDEO_PORT = 11111
    TELLO_IP = '192.168.10.1'
    TELLO_ADDRESS = (TELLO_IP, LOCAL_PORT)

    # set video frame
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FRAME_AREA = FRAME_WIDTH * FRAME_HEIGHT

    FRAME_DATA_SIZE = FRAME_AREA * 3 # pixel channel
    FRAME_CENTER_X, FRAME_CENTER_Y= FRAME_WIDTH / 2, FRAME_HEIGHT / 2
    FFMPEG_CMD = (f'ffmpeg -hwaccel auto -hwaccel_device opencl -i pipe:0 '
              f'-pix_fmt bgr24 -s {FRAME_WIDTH}x{FRAME_HEIGHT} -f rawvideo pipe:1')


    def __init__ (self, show_log=True, drone_type="TELLO"):
        ## initial valiables
        self.get_status_interval = 1
        self.show_log = show_log # show log
        self.low_battery_error_level = 10 # set clitical low battery warning for debug
        self.response = None
        self._event_killer = threading.Event()
        self._video_stopper = False
        self._status_buckup = None # status_dicts buckup
        self.frame = None
        self.rotate_frame = False # down vision resize video flag
        self.proc = None
        self._proc_exit_cycle = 0
        self.sdk = None
        self.wifi = None
        self.sn = None
        self.drone_type = drone_type

        ## log set
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        #self.log = logging.getself.log(__name__)
        self.log = logging.getLogger('TELLO_CONSOLE ')
        
        ## connect drone
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.LOCAL_IP, self.LOCAL_PORT))

            ## activate status recver
            self._recv_th = threading.Thread(target=self._recver, args=(self._event_killer, ), daemon=True)
            self._recv_th.start()

            ## drone check and start
            self.send_cmd('command', show=False)
            self.sdk = self.send_cmd('sdk?', show=False)
            self.wifi = self.send_cmd('wif?', show=False)
            self.sn = self.send_cmd('sn?', show=False)
            self.battery_level = self.get_status()['battery']
            self.log.info('残りバッテリー残量 %d パーセント'%self.battery_level)
            
            if self.battery_level < 50:
                self.log.warning('バッテリー残量が 50 % 以下のため、flip メソッドは使用できません。')
            if self.battery_level < self.low_battery_error_level:
                raise Exception("low_battery")
            self.log.info('TELLO CONSOLE スタート !')
            
        except OSError:
            self.clean()
            self._error_handler()
            
        except Exception as e:
            self.clean()
            self._error_handler(str(e))

    def __del__(self):
        self.clean()

    def clean(self):
        self.log.info('TELLO CONSOLE close')
        self._event_killer.set()
        self.socket.close()

        if self.proc is not None:
            os.kill(self.proc.pid, 9)

    def _error_handler(self, error_msg=""):
        if error_msg == "low_battery":
            log_msg = 'バッテリー残量がありません'
            exit_msg = "ドローンのバッテリー残量が残りわずかであるため、TELLO CONSOLE は終了しました。バッテリーを充電または交換してください。"
        elif error_msg == "motor_stop":
            log_msg = 'モーターが停止しています'
            exit_msg = "ドローンのモーターが停止しました。このメソッドは実行できません"
        else:
            log_msg = 'ドローンとの通信に失敗しました！'
            exit_msg = "ドローンとの接続に失敗したため、TELLO CONSOLE は終了しました。接続を確認してください。"
        self.log.error(log_msg)
        self.clean()
        sys.exit(exit_msg)

    def _issues_inspector(self, msg):
        if 'error Auto land' in msg or 'error Low voltage land' in msg:
            if self.get_status('battery') <= 10:
                self._error_handler('low_battery')
        elif 'error Motor stop' in msg:
            self._error_handler('motor_stop')
        else:
            self.log.error('CONTROL ERROR IS OCURED. msg is ... \n'+msg)

    def _recver(self, event_killer):
        init_time = time.time()
        while not event_killer.is_set():
            try:
                if self.response is None:
                    if time.time() - init_time > self.get_status_interval:
                        init_time = time.time()
                        self.get_status()
                        #self.log.info('STATUS UPDATED...')
                else:
                     init_time = time.time()
                self.response, _ = self.socket.recvfrom(3000)
            except socket.error as exc:
                #print(exc)
                #traceback.print_exc()
                self.log.error('CONNECTION ERROR \n'+str(exc))
                break

            except OSError:
                self.log.warn('CONNECTION WARN')

    def send_cmd(self, command, wait=0.5, show=True):
        try:
            response = None # init
            init_time = time.time()
            
            self.socket.sendto(command.encode('utf-8'), self.TELLO_ADDRESS)

            if wait is not None:
                while self.response is None:
                    if time.time() - init_time > wait:
                        if show : self.log.warning('COMMAND TIMEOUT')
                        self.response = b'None'
                    continue
            else: 
                self.response = b'None'

            response = self.response.decode('utf-8')
            if show : self.log.info({'COMMAND':command, 'RESPONSE':response})
            self.response = None

            return response

        except OSError:
            self._error_handler()

    def get_status(self,*keys):
        if self.drone_type == "TELLO":
            _key = ''
            try:
                status = []
                for key in keys:
                    if key == "roll" or key == "pitch" or key == "yaw":
                        _key = key
                        key = "attitude"
                    data = self.send_cmd(f'{key}?', show=False)
                    if ';' in data:
                        s = [int(re.search(r'\d+', item).group()) for item in data.split(';')[:-1] if re.search(r'\d+', item)]
                        if _key == 'pitch':
                            s = s[0]
                        if _key == 'roll':
                            s = s[1]
                        if _key == 'yaw':
                            s = s[2]
                    else:
                        s = int(re.findall(r'-?\d+\.?\d*', data)[0])
                    status.append(s)
                if len(status) == 1:
                    status = status[0]
                self._status_buckup = status
                return status
            except IndexError:
                self.log.warning('DETECT BROKEN DATA')
                s = []
                for key in keys:
                    s.append(self.get_status(key))
                if len(status) == 1:
                    s = s[0]
                status = s
                return s
        elif self.drone_type == "TELLO-EDU":
            try:
                keydata = []
                raw_status = self.send_cmd('status?', show=True)
                status = {key: [int(val) if '.' not in val else float(val) for val in value] if len(value) > 1 else (int(value[0]) if '.' not in value[0] else float(value[0])) for key, value in dict(
                            zip(['mid', 'x', 'y', 'z', 'mpry', 'pitch', 'roll', 'yaw', 'vgx', 'vgy', 'vgz', 'templ', 'temph', 'tof', 'height', 'battery', 'baro', 'time', 'agx', 'agy', 'agz'],
                                [item for item in [re.findall(r'-?\d+\.?\d*', item) for item in raw_status.split(';')] if item is not None])).items()}
                if not keys:
                    return status
                else:
                    if len(keys) == 1:
                        return status[keys[0]]

                    for key in keys:
                        keydata.append(status[key])
                    return keydata
            except IndexError:
                self.log.warning('RETURN OLD DATA')
                print(keys)
                if self._status_buckup is None:
                    if len(keys) == 1:
                        status = self.send_cmd(keys[0]+'?', show=True)
                        return status
                        
                if not keys:
                    return self._status_buckup
                else:
                    if len(keys) == 1:
                        return self._status_buckup[keys[0]]
                    
                    for key in keys:
                        keydata.append(self._status_buckup[key])
                    return keydata

    def stream(self, stream):
        if stream:
            response = self.send_cmd('streamon', show=self.show_log, wait=10)
            # FFmpegプロセスの設定
            '''
            if self.show_log:
                self.proc = subprocess.Popen(self.FFMPEG_CMD.split(' '), 
                                             stdin=subprocess.PIPE, 
                                             stdout=subprocess.PIPE)
                
            else:
            '''
            self.proc = subprocess.Popen(self.FFMPEG_CMD.split(' '), 
                                         stdin=subprocess.PIPE, 
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL)
                                         
            self.proc_stdin = self.proc.stdin
            self.proc_stdout = self.proc.stdout

            # 受信映像の設定
            self._receive_video_thread = threading.Thread(
                target=self._receive_video,
                args=(self._event_killer, self.proc_stdin,
                      self.LOCAL_IP, self.VIDEO_PORT,))
            self._receive_video_thread.start()
            '''
            self._receive_video_thread = threading.Thread(target=self._recv_video,args=(self._event_killer,))
            self._receive_video_thread.start()
            '''

            '''
            self.loop = asyncio.get_event_loop()
            self.loop.create_task(self._gen_video())
            self.loop.run_forever()
            self._receive_video_thread = threading.Thread(target=self._video_recver)
            self._receive_video_thread.start()
            '''
            self._receive_video_thread = threading.Thread(target=self._gen_video)
            self._receive_video_thread.start()
            
            while self.frame is None:
                continue
            self.log.info('STREAM START')

        else:
            #self.loop.stop()
            cv2.destroyAllWindows()
            if self.proc is not None:
                os.kill(self.proc.pid, 9)

    def _receive_video(self, stop_event, pipe_in, host_ip, tello_video_port):
        #self.log.info('run recv video')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_video:
            sock_video.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock_video.settimeout(.5)
            sock_video.bind((host_ip, tello_video_port))
            data = bytearray(2048)
            while not stop_event.is_set():
                if self._proc_exit_cycle > 3:
                    self.log.error('STREAM TIMEOUT BREAK')
                    self.clean()
                try:
                    size, _ = sock_video.recvfrom_into(data)
                    self._proc_exit_cycle = 0
                except socket.timeout as exception:
                    self.log.warning({'video streaming':exception})
                    self._proc_exit_cycle += 1
                    time.sleep(0.5)
                    continue
                except socket.error as exception:
                    self.log.error({'video streaming':exception})
                    break

                try:
                    pipe_in.write(data[:size])
                    pipe_in.flush()
                except Exception as exception:
                    self.log.error({'video streaming':exception})
                    break
                
    def _gen_video(self):
        try:
            while True:
                frame = None
                try:
                    frame = self.proc_stdout.read(self.FRAME_DATA_SIZE)
                except Exception as exception:
                    self.log.error({'video gen': exception})
                    #continue

                if frame is None:
                    #pass
                    continue
                frame = np.frombuffer(frame, np.uint8).reshape(self.FRAME_HEIGHT, self.FRAME_WIDTH, 3)
                if self.rotate_frame:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                frame = cv2.UMat(frame)
                self.frame = frame
        except ValueError:
            pass

    def _start_video_recver(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._gen_video())
        
    def downvision(self, dir=True):
        if dir:
            self.send_cmd('downvision 1', show=False, wait=None)

            #self._video_stopper = True
            self.rotate_frame = True
            #cv2.destroyAllWindows()
            #time.sleep(1)
            #self._video_stopper = False
            
            #self.FRAME_HEIGHT = 640
            #self.FRAME_WIDTH = 480
        else:
            self.send_cmd('downvision 0', show=False, wait=None)

            #self._video_stopper = True
            self.rotate_frame = False
            #cv2.destroyAllWindows()
            #time.sleep(1)
            #self._video_stopper = False
            #self.FRAME_WIDTH = 640
            #self.FRAME_HEIGHT = 480

    #def show_flight_display(self):

    def takeoff(self,wait=10):
        try:
            response = self.send_cmd('takeoff', show=self.show_log, wait=wait)
            if 'ok' in response:
                self.log.info('TAKEOFF!')
            elif wait is not None:
                self.log.error('TAKEOFF ERROR IS OCURED msg is ... \n'+response)
            return response
            
        except OSError:
            self._error_handler()
        except KeyboardInterrupt:
            self.emergency()

    def land(self,wait=10):
        try:
            response = self.send_cmd('land', show=self.show_log, wait=wait)
            if 'ok' in response:
                self.log.info('LANDING')
            elif wait is not None:
                self.log.error('LANDING ERROR IS OCURED msg is ... \n'+response)
            return response

        except OSError:
            self._error_handler()

    def emergency(self):
        try:
            response = self.send_cmd('emergency', show=False, wait=0.1)
            self.log.error('EMERGENCY ! ドローンのモーターを停止しました')
            return response

        except OSError:
            self._error_handler()

    def up(self, distance, wait=10):
        try:
            if distance < 20:
                distance = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif distance > 500:
                distance = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            response = self.send_cmd('up %d'%(distance), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def down(self, distance, wait=10):
        try:
            if distance < 20:
                distance = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif distance > 500:
                distance = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            response = self.send_cmd('down %d'%(distance), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def forward(self, distance, wait=10):
        try:
            if distance < 20:
                distance = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif distance > 500:
                distance = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            response = self.send_cmd('forward %d'%(distance), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def back(self, distance, wait=10):
        try:
            if distance < 20:
                distance = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif distance > 500:
                distance = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            response = self.send_cmd('back %d'%(distance), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def right(self, distance, wait=10):
        try:
            if distance < 20:
                distance = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif distance > 500:
                distance = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            response = self.send_cmd('right %d'%(distance), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def left(self, distance, wait=10):
        try:
            if distance < 20:
                distance = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif distance > 500:
                distance = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            response = self.send_cmd('left %d'%(distance), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def cw(self, angle, wait=10):
        try:
            '''
            if angle < 20:
                angle = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif angle > 500:
                angle = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            '''
            time.sleep(0.5)
            response = self.send_cmd('cw %d'%(angle), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def ccw(self, angle, wait=10):
        try:
            '''
            if angle < 20:
                angle = 20
                self.log.warning('このメソッドは20以下の値を指定できません。指定可能範囲は 20 ~ 500 です')
            elif angle > 500:
                angle = 500
                self.log.warning('このメソッドは500以上の値を指定できません。指定可能範囲は 20 ~ 500 です')
            '''
            time.sleep(0.5)
            response = self.send_cmd('ccw %d'%(angle), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def go(self, x, y, z, speed=100, wait=10):
        try:
            response = self.send_cmd('go %d %d %d %d'%(x,y,z,speed), show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def flip(self, direction, wait=10):
        try:
            response = self.send_cmd('direction '+direction, show=self.show_log, wait=wait)
            if 'ok' not in response and wait is not None:
                self._issues_inspector(response)
            return response
            
        except OSError:
            self._error_handler()

    def rc(self, roll=0, pitch=0, throttle=0, yaw=0):
        try:
            self.send_cmd('rc %d %d %d %d'%(roll, pitch, throttle, yaw), show=False, wait=None)
        except OSError:
            self._error_handler()

    def height_tof(self, height, speed=100, debug=False):
        while True:
            try:
                cur_height = self.get_status("tof")
                if height - cur_height < 10 and height - cur_height > -10:
                    break
                throttle = ((height-cur_height) / height) * 100
                throttle = max(-speed, min(speed, throttle))
                if debug: self.log.info({"throttle":throttle,"cur_height":cur_height})
                self.rc(throttle=int(throttle))
            except KeyboardInterrupt:
                self.log.warning('BREAK')
                break
        self.rc(throttle=0)
        self.log.info("REACHED %d"%height)

    def height_rlt(self, height):
        cur_height = self.get_status("height")
        distance = height-cur_height
        self.go(0,0,distance,0)
        self.log.info("REACHED %d"%height)

    def angle(self, direction, debug=False):
        while True:
            try:
                cur_direction = self.get_status('yaw')
                if cur_direction < 0:
                    cur_direction = 360 + cur_direction
                rotation = (1.9*(direction - cur_direction) / direction) * 100
                rotation = max(-100, min(100, rotation))
                if debug: self.log.info({"rotation":rotation,"cur_direction":cur_direction})

                if rotation < 1 and rotation > -1:
                    break
                self.rc(yaw=int(rotation))
                
            except KeyboardInterrupt:
                self.log.warning('BREAK')
                break
            
        self.rc(yaw=0)
        self.log.info("REACHED %d"%direction)

    def missionpad_detection(self, detect, detect_area='down', wait=10):
        try:
            if detect:
                response = self.send_cmd('mon', show=self.show_log, wait=wait)
                if 'ok' not in response and wait is not None:
                    self._issues_inspector(response)
                if detect_area == 'down':
                    detect_area = 0
                elif detect_area == 'forward':
                    detect_area = 1
                elif detect_area == 'all':
                    detect_area = 2
                else:
                    self.log.error('その引数は無効です')
                    self._error_handler()

                response = self.send_cmd('mdirection %d'%detect_area, show=self.show_log, wait=wait)
                if 'ok' not in response and wait is not None:
                    self._issues_inspector(response)

        except OSError:
            self._error_handler()

    def debug(self):
        while True:
            try:
                data = self.get_status('mid', 'x', 'y', 'z', 'mpry')
                self.log.info({"data":data})
            except KeyboardInterrupt:
                self.log.warning('BREAK')
                break
