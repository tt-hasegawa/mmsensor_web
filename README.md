# M and M 's Sensor Project

* はじめに
 Raspberry Piと機械学習ライブラリで画像認識して、
 三密状態を計測するサービスのサンプルです。

* ソースファイルのチェックアウト
```
 git clone https://github.com/tt-hasegawa/mmsensor.git
```

* サーバ側作業
 herokuアカウントを作成します。
```
 pip freeze > requirements.txt
 git init
 git add .
 git commit -m "Initial Commit"
```

```
 heroku login

 →ここでWebブラウザが起動してくるので、herokuにログインしてください。
```

```
 heroku create 

 →割り当てられたURLが表示されるのでメモっておいてください。
```

```
 git push heroku master
```

* プログラムを修正した場合は以下のコマンドで再度herokuにアップしてください。
```
 heroku login
 pip freeze > requirements.txt
 git add .
 git commit -m "initial commit2"
 git push heroku master
```

* Raspberry Pi側作業
 raspberrypiフォルダをそのままraspberrypi側の任意のフォルダに転送します。

```
 pip install -r ./requirements.txt
 sh install.sh
```

```
 vi VentiSensor.py

 urlとproxiesの部分を適宜環境に合わせて書き換えます。
```

```
 python VentiSensor.py
 しばらくすると、温度センサーとカメラの内容がWebサーバにアップされていきます。
```
"# mmsensor" 
