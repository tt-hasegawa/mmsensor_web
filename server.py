from flask import Flask,render_template,jsonify,make_response,abort,request
from flask_httpauth import HTTPDigestAuth
import datetime
import peewee
import base64
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'matsusakaEDPcenter'
auth = HTTPDigestAuth()
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

DIFF_JST_FROM_UTC = 9


# API用DB接続クラス
db=None
if os.path.exists('/tmp'):
    db = peewee.SqliteDatabase("/tmp/data.db")
elif os.path.exists('c:\\temp'):
    db = peewee.SqliteDatabase("c:\\temp\\data.db")

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

db.create_tables([VentilationInfo])


users = {
    "user": "password",
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


# API実装
# データ取得API
@app.route('/getVentilation/<int:numOfRecord>', methods=['GET'])
def get_Ventilations(numOfRecord):
    try:
        ventilist = VentilationInfo.select().order_by(VentilationInfo.recdate)
    except VentilationInfo.DoesNotExist:
        abort(404)
    dataset1 = {
        'label':'気温(c)',
        'backgroundColor':'rgba(75,192,192,0.4)',
        'borderColor':'rgba(75,192,192,1)',
        'data':[]
    }
    dataset2 = {
        'label':'湿度(%)',
        'backgroundColor':'rgba(192,75,192,0.4)',
        'borderColor':'rgba(192,75,192,1)',        
        'data':[]
    }
    dataset3 = {
        'label':'人数(人)',
        'backgroundColor':'rgba(192,192,75,0.4)',
        'borderColor':'rgba(192,192,75,1)',        
        'data':[]
    }
    dataset4 = {
        'label':'CO2(*10ppm)',
        'backgroundColor':'rgba(192,75,75,0.4)',
        'borderColor':'rgba(192,75,75,1)',        
        'data':[]
    }
    dataset5 = {
        'label':'不快指数',
        'backgroundColor':'rgba(75,75,192,0.4)',
        'borderColor':'rgba(75,75,192,1)',        
        'data':[]
    }
    labels = []
    for v in ventilist:
        key=v.recdate
        labels.append(key)
        dataset1['data'].append(v.temperature)
        dataset2['data'].append(v.humidity)
        dataset3['data'].append(v.population*10)
        dataset4['data'].append(v.co2/10)
        f = 0.81*v.temperature + 0.01 * v.humidity * (0.99 * v.temperature - 14.3) + 46.3
        dataset5['data'].append(f)
        
    result = {"labels":labels,"datasets":[dataset1,dataset2,dataset3,dataset4,dataset5]}
    return make_response(jsonify(result))

# データ登録API
@app.route('/addPopulation/', methods=['POST'])
def addPopulation():
    result="ok"
    try:
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        d = dt.strftime('%Y-%m-%d %H:%M')
        jsonData = request.json
        p = jsonData.get("population")
        g = jsonData.get("image").encode('utf-8')

        print("{} p:{} g:{}".format(d,p,len(g)))
        v = VentilationInfo(recdate=d,population=p,images=g)
        ventilist = VentilationInfo.select().where(VentilationInfo.recdate == d)

        if len(ventilist) != 0:
            v = ventilist[0]
            v.population=p
            v.images=g

        v.save()
    except Exception as e:
        print(e)
        result="ng"
    return result

@app.route('/addHygrometer/', methods=['POST'])
def addHygrometer():
    result="ok"
    try:
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        d = dt.strftime('%Y-%m-%d %H:%M')
        jsonData = request.json
        t = jsonData.get("temperature")
        h = jsonData.get("humidity")

        print("{} t:{} h:{}".format(d,t,h))
        v = VentilationInfo(recdate=d,temperature=t,humidity=h)
        ventilist = VentilationInfo.select().where(VentilationInfo.recdate == d)

        if len(ventilist) != 0:
            v = ventilist[0]
            v.temperature=t
            v.humidity=h

        v.save()
    except Exception as e:
        print(e)
        result="ng"
    return result


@app.route('/addCO2/', methods=['POST'])
def addCO2():
    result="ok"
    try:
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        d = dt.strftime('%Y-%m-%d %H:%M')
        jsonData = request.json
        c = jsonData.get("co2")
        v = VentilationInfo(recdate=d,co2=c)

        ventilist = VentilationInfo.select().where(VentilationInfo.recdate == d)
        if len(ventilist) != 0:
            v = ventilist[0]
            v.co2 = c
        
        print("{} c:{}".format(d,c))
        v.save()
    except Exception as e:
        print(e)
        result="ng"
    return result

# APIエラー
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#####################################################################
# ページ遷移
@app.route('/')
def index():
    idx=0
    h=0
    t=0
    p=0
    c=0

    try:
        ventilist = VentilationInfo.select().where(
                (VentilationInfo.humidity > 0) &
                (VentilationInfo.temperature > 0) &
                (VentilationInfo.co2 > 0) &
                (VentilationInfo.population > 0)
                ).order_by(VentilationInfo.recdate.desc()).limit(1)
    except VentilationInfo.DoesNotExist:
        abort(404)
    if len(ventilist) > 0:
        v = ventilist[0]
        h=v.humidity
        t=v.temperature
        p=v.population
        c=v.co2
        idx=0
        if p > 3:
            idx+=(p-3)*10
        f = 0.81*t + 0.01 * h * (0.99*t - 14.3) + 46.3
        if f > 70:
            idx+=(f-70)
        if c > 1000:
            idx+=(c-1000)/10

    return render_template('index.html',
            idx=int(idx),
            f=f,
            temperature=t,
            humidity=h,
            person=p,
            co2=c)

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/images')
@auth.login_required
def images():
    try:
        ventilist = VentilationInfo.select().order_by(VentilationInfo.recdate.desc()).limit(10)
    except VentilationInfo.DoesNotExist:
        abort(404)

    return render_template('images.html',images=ventilist)

@app.route('/help')
def help():
    return render_template('help.html')
#####################################################################

# サービス起動
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
