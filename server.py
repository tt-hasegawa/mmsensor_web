from flask import Flask,render_template,jsonify,make_response,abort,request
from flask_httpauth import HTTPDigestAuth
import datetime
import peewee
import base64
import os

# 初期設定
app = Flask(__name__)
app.config['SECRET_KEY'] = 'matsusakaEDPcenter'
auth = HTTPDigestAuth()
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

DIFF_JST_FROM_UTC = 9

# SQLiteDBの生成
db=None
if os.path.exists('/tmp'):
    db = peewee.SqliteDatabase("/tmp/data.db")
elif os.path.exists('c:\\temp'):
    db = peewee.SqliteDatabase("c:\\temp\\data.db")


################################################################################
# 換気情報データクラス
class VentilationInfo(peewee.Model):
    recdate = peewee.TextField()
    temperature = peewee.FloatField(null=True,default=0.0)
    humidity = peewee.FloatField(null=True,default=0.0)
    population = peewee.IntegerField(null=True,default=0)
    images = peewee.TextField(null=True,default="")
    co2 = peewee.FloatField(null=True,default=0.0)

    class Meta:
        database = db
################################################################################

# テーブルの作成
db.create_tables([VentilationInfo])

# パスワード認証用ユーザ設定
users = {
    "user": "password",
}

# パスワード認証がかかっているページでの認証処理
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


# API実装
# データ取得API→Chart.jsで参照するのに使う
@app.route('/getVentilation/<int:numOfRecord>', methods=['GET'])
def get_Ventilations(numOfRecord):
    # データを日時順に取得する.
    try:
        ventilist = VentilationInfo.select().order_by(VentilationInfo.recdate)
    except VentilationInfo.DoesNotExist:
        abort(404)
    # グラフ描画用データセットを準備する。
    # 色や説明はここで変更する。
    dataset1 = {
        'label':'気温(c)',
        'backgroundColor':'rgba(75,192,192,0.4)',
        'borderColor':'rgba(75,192,192,1)',
        'yAxisID':'y-axis-1',
        'data':[]
    }
    dataset2 = {
        'label':'湿度(%)',
        'backgroundColor':'rgba(192,75,192,0.4)',
        'borderColor':'rgba(192,75,192,1)',        
        'yAxisID':'y-axis-1',
        'data':[]
    }
    dataset3 = {
        'label':'人数(*10人)',
        'backgroundColor':'rgba(192,192,75,0.4)',
        'borderColor':'rgba(192,192,75,1)',        
        'yAxisID':'y-axis-1',
        'data':[]
    }
    dataset4 = {
        'label':'CO2(ppm)',
        'backgroundColor':'rgba(192,75,75,0.4)',
        'borderColor':'rgba(192,75,75,1)',        
        'yAxisID':'y-axis-2',
        'data':[]
    }
    dataset5 = {
        'label':'不快指数',
        'backgroundColor':'rgba(75,75,192,0.4)',
        'borderColor':'rgba(75,75,192,1)',        
        'yAxisID':'y-axis-1',
        'data':[]
    }
    labels = []
    # データを読み込んで、グラフ用に編集しながら追加していく。
    for v in ventilist:
        key=v.recdate
        labels.append(key)
        # 不快指数の計算
        f = int(0.81*v.temperature + 0.01 * v.humidity * (0.99 * v.temperature - 14.3) + 46.3)

        dataset1['data'].append(v.temperature)
        dataset2['data'].append(v.humidity)
        dataset3['data'].append(v.population*10) # 人数×10をグラフ表示
        dataset4['data'].append(v.co2)
        dataset5['data'].append(f)
        
    # JSON形式で戻り値を返すために整形
    result = {
            "labels":labels,
            "datasets":[dataset1,dataset2,dataset3,dataset4,dataset5]}
    return make_response(jsonify(result))

# データ登録API
# 人口密度を登録するAPI
@app.route('/addPopulation/', methods=['POST'])
def addPopulation():
    result="ok"
    try:
        # 登録日時を日本のTimeZoneで取得して、文字列化して設定
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        d = dt.strftime('%Y-%m-%d %H:%M')

        # POSTされたJSONデータからキーを元にデータ取得
        jsonData = request.json
        p = jsonData.get("population")
        g = jsonData.get("image").encode('utf-8')
        print("{} p:{} g:{}".format(d,p,len(g)))

        # 同日時のデータがあれば更新、無ければ新規登録
        v = VentilationInfo(recdate=d,population=p,images=g)
        ventilist = VentilationInfo.select().where(VentilationInfo.recdate == d)
        if len(ventilist) != 0:
            v = ventilist[0]
            v.population=p
            v.images=g

        # データを保存
        v.save()
    except Exception as e:
        # エラー時はログ出力して終わり
        print(e)
        result="ng"
    return result

@app.route('/addHygrometer/', methods=['POST'])
# 温度・湿度を登録するAPI
def addHygrometer():
    result="ok"
    try:
        # 登録日時を日本のTimeZoneで取得して、文字列化して設定
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        d = dt.strftime('%Y-%m-%d %H:%M')

        # POSTされたJSONデータからキーを元にデータ取得
        jsonData = request.json
        t = jsonData.get("temperature")
        h = jsonData.get("humidity")
        print("{} t:{} h:{}".format(d,t,h))

        # 同日時のデータがあれば更新、無ければ新規登録
        v = VentilationInfo(recdate=d,temperature=t,humidity=h)
        ventilist = VentilationInfo.select().where(VentilationInfo.recdate == d)
        if len(ventilist) != 0:
            v = ventilist[0]
            v.temperature=t
            v.humidity=h

        # データを保存
        v.save()
    except Exception as e:
        # エラー時はログ出力して終わり
        print(e)
        result="ng"
    return result


@app.route('/addCO2/', methods=['POST'])
# CO2濃度を登録するAPI
def addCO2():
    result="ok"
    try:
        # 登録日時を日本のTimeZoneで取得して、文字列化して設定
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        d = dt.strftime('%Y-%m-%d %H:%M')

        # POSTされたJSONデータからキーを元にデータ取得
        jsonData = request.json
        c = jsonData.get("co2")
        print("{} c:{}".format(d,c))

        # 同日時のデータがあれば更新、無ければ新規登録
        v = VentilationInfo(recdate=d,co2=c)
        ventilist = VentilationInfo.select().where(VentilationInfo.recdate == d)
        if len(ventilist) != 0:
            v = ventilist[0]
            v.co2 = c
        
        # データを保存
        v.save()
    except Exception as e:
        # エラー時はログ出力して終わり
        print(e)
        result="ng"
    return result

# APIエラー
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#####################################################################
# ページ遷移
# 初期ページ
@app.route('/')
def index():
    idx=0
    h=0
    t=0
    p=0
    c=0
    f=0

    try:
        # 換気情報で、各値が0以外の最新データ1件目を取得する.
        ventilist = VentilationInfo.select().where(
                (VentilationInfo.humidity > 0) &
                (VentilationInfo.temperature > 0) &
                (VentilationInfo.co2 > 0) &
                (VentilationInfo.population > 0)
                ).order_by(VentilationInfo.recdate.desc()).limit(1)
    except VentilationInfo.DoesNotExist:
        abort(404)
    # データがあれば、三密指数を計算する.
    if len(ventilist) > 0:
        v = ventilist[0]
        h=v.humidity
        t=v.temperature
        p=v.population
        c=v.co2
        # 不快指数の計算
        f = int(0.81*t + 0.01 * h * (0.99*t - 14.3) + 46.3)
        idx=0 # 三密指数
        # 人口密度が3人を越える1人毎に10%増加
        if p is not None and p > 3:
            idx+=(p-3)*10
        # 不快指数が70を越える1%毎に1%増加
        if f > 70:
            idx+=(f-70)
        # CO2濃度が1000を越える10ppm毎に1%増加
        if c > 1000:
            idx+=(c-1000)/10

    # 画面にパラメータを渡してhtml描画
    return render_template('index.html',
            idx=int(idx),
            f=f,
            temperature=t,
            humidity=h,
            person=p,
            co2=c)

@app.route('/graph')
def graph():
    # 画面にパラメータを渡してhtml描画
    # ※グラフからchart.jsがjsonを取得しているので、パラメータは無し
    return render_template('graph.html')

@app.route('/images')
@auth.login_required
def images():
    try:
        # 直近10件を取得
        ventilist = VentilationInfo.select().order_by(VentilationInfo.recdate.desc()).limit(10)
    except VentilationInfo.DoesNotExist:
        abort(404)

    # 画面にパラメータを渡してhtml描画
    return render_template('images.html',images=ventilist)

@app.route('/help')
def help():
    return render_template('help.html')
#####################################################################

# サービス起動
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
