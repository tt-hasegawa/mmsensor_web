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
 　※無償アカウントではアプリケーションを5つまで配備できます。
 　　既に5つ作成済みの方は、一度、不要なアプリケーションを削除してください。
     https://dashboard.heroku.com/apps

```

```
 git push heroku master
```

* プログラムを修正した場合は以下のコマンドで再度herokuにアップしてください。
```
 heroku login
 git add .
 git commit -m "Update Comments"
 git push heroku master
```


割り当てられたURLをChromeなどのWebブラウザで開けることを確認してください。
  
同URLを各センサー担当者に伝えて、データ送信してもらうように設定してもらってください。

"# mmsensor" 
