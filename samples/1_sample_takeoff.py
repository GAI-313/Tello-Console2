# これを書いて TELLO を制御するためのモジュール Console を読み込む
from console import Console

# Console を変数に格納すると TELLO CONSOLE2 が起動します
drone = Console()

# takeoff メソッドを実行すると、ドローンは離陸します
drone.takeoff()

# land メソッドを実行すると、ドローンは着陸します
drone.land()