# これを書いて TELLO を制御するためのモジュール Console を読み込む
from console import Console

# Console を変数に格納すると TELLO CONSOLE2 が起動します
drone = Console()

# takeoff メソッドを実行すると、ドローンは離陸します
drone.takeoff()

# forward メソッドに値 40 を入れるとドローンは 40cm 前進します
drone.forward(40)

# back メソッドに値 40 を入れるとドローンは 40cm 前進します
drone.back(40)

# up メソッドに値 40 を入れるとドローンは 40cm 上昇します
drone.up(40)

# down メソッドに値 40 を入れるとドローンは 40cm 下降します
drone.down(40)

# right メソッドに値 40 を入れるとドローンは 40cm 右移動します
drone.right(40)

# left メソッドに値 40 を入れるとドローンは 40cm 左移動します
drone.left(40)

# cw メソッドに値 90 を入れるとドローンは 90° 時計回りに旋回します
drone.cw(40)

# ccw メソッドに値 90 を入れるとドローンは 90° 反時計回りに旋回します
drone.ccw(40)

# land メソッドを実行すると、ドローンは着陸します
drone.land()