# Tello Console 2

## インストール
### ffmpeg をインストールする
以下のリンクをクリックして FFmpeg をダウンロードしてください
- https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zipファイル

コマンドプロンプトまたはPowerShellを開いて TELLO-CONSOLE2 をホームディレクトリにダウンロードします。
```
cd %HOMEPATH%
git clone -b win https://github.com/GAI-313/Tello-Console2.git
```
TELLO-CONSOLE2 パッケージに移動して、`install.bat` を実行します。
```
cd Tello-Console2
install.bat
```
　`install.bat` 実行後、実行結果に
```
以下のパスを環境変数PATHに追加してください！
C:\..\..\..\
```
と表示されるので、この `C:\` から始まる文字列をコピーしてください。<br>
　環境変数設定画面でシステム環境変数の `Path` に先ほどコピーした文字列を追加してください。追加後、コマンドプロンプトまたは PowerShell を再起動したらインストール完了です。

## 使用方法
　Python スクリプト上に以下のモジュールをインポートすることで利用できます。
```python
from tello-console2.console import Console
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