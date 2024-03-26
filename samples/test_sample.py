# これを書いて TELLO を制御するためのモジュール Console を読み込む
from console import Console

# Console を変数に格納すると TELLO CONSOLE2 が起動します
drone = Console()

while True:
    #drone.get_status("battery", "tof", "attitude")
    a = drone.get_status("tof")
    print(a)

