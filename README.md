# Tello Console 2
## インストール
　ターミナルを開き、ホームディレクトリに移動します。
```bash
cd ~
```
　以下のコマンドを実行してシェル設定を `zsh` から `bash` に切り替えます。
```bash
chsh -s /bin/bash
```
　完了したらここで一度ターミナルを再起動してください。<br>
　TELLO-CONSOLE2 を以下のコマンドを実行してダウンロードします。
```bash
git clone https://github.com/GAI-313/Tello-Console2.git
```
　このパッケージの依存関係である **OpenCV** を以下のコマンドを実行してインストールします。
```bash
pip install opencv-python
```
  もし上記のコマンドを実行して
```
error: externally-managed-environment
```
から始まる `pip` 関連のエラーが発生したら以下のコマンドを実行してください。
```bash
pip install  --break-system-packages opencv-python
```
　インストールが完了したらこのパッケージを以下のコマンドを実行して PYTHONPATH に追加します。
```bash
echo 'export PYTHONPATH=$HOME/Tello-Console2/tello_console2:$PYTHONPATH' >> ~/.bashrc
```
　以下のコマンドを実行してパッケージを再読み込みします。
```bash
source ~/.bashrc
```
## 使用方法
　Python スクリプト上に以下のモジュールをインポートすることで利用できます。
```python
from console import Console
```
　インポートした `Console` コンストラクタを任意の変数に格納させインスタンス化して任意のメソッドを使用できます。
```python
drone = Console()
```
　以降ドローンの制御を実装可能になります。詳しい使用方法はサンプルコードを参照してください。

## サンプルコードを実行する
　サンプルコードは本パッケージの `samples` ディレクトリにあります。サンプルコードには本パッケージの使用例をいくつか用意してありますので、参考にしてください。

## メソッド一覧
　メソッド一覧は現在作成中です。完成次第 Qiita にて公開予定です。
