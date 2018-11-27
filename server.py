# coding=utf-8

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_wtf import Form
from wtforms.fields import *
from wtforms.validators import DataRequired, Required, Email
from markupsafe import escape
import random
import math
import numpy as np
import utils

# configuration
DATABASE = './datasets.db'
SECRET_KEY = 'development key'
CSRF_ENABLED = True

nav = Nav()
@nav.navigation()
def demonavbar():
    return Navbar(
        'FINGERPRINTING',
        View('Home', '.index'),
        Subgroup(
            '相似度检测',
            View('Text Search', 'test_text_data'),
            View('Image Search', 'test_image_data'),
            View('Video Search', 'test_video_data'),
        ),
        Subgroup(
            'Dataset',
            View('Text', 'show_text_data'),
            View('Image', 'show_image_data'),
            View('Video', 'show_video_data'),
        ),
    )

def create_app():
  app = Flask(__name__)
  Bootstrap(app)
  nav.init_app(app)
  return app

app = create_app()
app.config.from_object(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

class DatasetForm(Form):
    name = TextField(u'Dataset Table Name', validators=[Required()])
    submit = SubmitField(u'查询')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text-data')
def show_text_data():
    cur = g.db.execute('select * from LMRD_1')
    candidates = []
    for row in cur.fetchall():
        if(random.random()<0.01):
            candidates.append(row)
            if(len(candidates)==100):
                break
    return render_template('text_dataset.html', data=candidates)

@app.route('/image-data')
def show_image_data():
    begin = math.floor(random.random()*990000)
    cur = g.db.execute('select * from IMDS where ID>=' + str(begin) + ' and ID<=' + str(begin+1000) + ';').fetchall()
    candidates = []
    for row in cur:
        if (random.random()<0.05):
            candidates.append([row[0],row[1],row[2],row[3]])
            if (len(candidates)==20):
                break

    # 临时计算哈希
    print('start hash...')
    for c in candidates:
        try:
            kpdes = utils.SIFT('static/' + c[2]);
            c[3] = utils.getImageHashValues(kpdes[1]).tobytes()
        except Exception as e:
            print(e)

    return render_template('image_dataset.html', data=candidates)

@app.route('/video-data')
def show_video_data():
    begin = math.floor(random.random()*90000)
    cur = g.db.execute('select * from VDS where ID>=' + str(begin) + ' and ID<=' + str(begin+1000) + ';').fetchall()
    candidates = []
    for row in cur:
        if (random.random()<0.05):
            candidates.append(row)
            if (len(candidates)==20):
                break
    return render_template('video_dataset.html', data=candidates)


@app.route('/test-text-data/', methods=('GET', 'POST'))
def test_text_data():
    if request.method == 'POST':
        category, name = request.form['category'], request.form['name']
        cur = g.db.execute('select data from LMRD_1 where category=:cate and fileid=:name', {'cate':category, 'name':name})
        result = []
        for row in cur.fetchall():
            result.append(row)
        if(len(result)!=1):
            if(len(result)==0):
                return render_template('search_text_form.html',  error='输入查询不到记录')
            else:
                return render_template('search_text_form.html', error='输入查询到了多个记录')
        data  = result[0][0]
        if(request.form['ControlSelect1']=='随机删除两个句子'):
            after_data = utils.removeSentences(data)
        elif(request.form['ControlSelect1']=='随机删除十分之一的单词'):
            after_data = utils.removeWords(data)
        elif(request.form['ControlSelect1']=='随机替换单词为反义词'):
            after_data = utils.switchAntonyms(data)
        else:
            return render_template('search_text_form.html', error='操作选择错误')
        try:
            after_data_hash = utils.getTextHashValues(after_data)
            cur = g.db.execute('select * from LMRD_1')
            similiar_items = []
            simi_values=[]
            for row in cur.fetchall():
                value = utils.jaccardMeasure(np.frombuffer(row[3],dtype=np.uint64), after_data_hash)
                simi_values.append(value)
                if(value>0.65):
                    similiar_items.append([value, row[0], row[1], row[2]])
            app.logger.debug(len(similiar_items))
            similiar_items = sorted(similiar_items, key=lambda x:x[0], reverse=True)
            legend = '相似值数据的分布'
            labels = [".0-.1", ".1-.2", ".2-.3", ".3-.4", ".4-.5", ".5-.6", ".6-.7", ".7-.8", ".8-.9", ".9-1.0"]
            values, _ = np.histogram(simi_values,bins=np.arange(11)/10)
            del simi_values
        except Exception as exc:
            return render_template('search_text_form.html', err='Exception: '+exc)
        return render_template(('result_text_form.html'), before=data, after=after_data, similiar=similiar_items, values=values, labels=labels, legend=legend)
    return render_template('search_text_form.html', error=None)

@app.route('/test-image-data/', methods=('GET', 'POST'))
def test_image_data():
    if request.method == 'POST':
        name = request.form['name']
        cur = g.db.execute('select * from IMDS where name=:imgname', {'imgname':name})
        result = []
        for row in cur.fetchall():
            result.append(row)
        if(len(result)!=1):
            if(len(result)==0):
                return render_template('search_image_form.html',  error='输入查询不到记录')
            else:
                return render_template('search_image_form.html', error='输入查询到了多个记录')
        data  = '../' + result[0][2]
        after_data = 'static/test_image_temp/' + result[0][1]
        before_data_web = '/static/' + result[0][2]
        after_data_web = '/static/test_image_temp/' + result[0][1]
        if(request.form['ControlSelect1']=='随机剪切图片长宽的百分之0-25'):
            flag = utils.cropImage(data, 'static/test_image_temp', result[0][1])
        elif(request.form['ControlSelect1']=='随机旋转图片长宽的0-45度'):
            flag = utils.rotateImage(data, 'static/test_image_temp', result[0][1])
        elif(request.form['ControlSelect1']=='横向合并图片（待续）'):
            return render_template('search_image_form.html', error='操作选择错误')
        else:
            return render_template('search_image_form.html', error='操作选择错误')
        if flag:
            try:
                kpdes = utils.SIFT(after_data)
                after_data_hash = utils.getImageHashValues(kpdes[1]).tobytes()            
            except Exception as exc:
                return render_template('search_image_form.html', err='Exception: '+str(exc))
            return render_template(('result_image_form.html'), before=before_data_web, after=after_data_web)
        else:
            return render_template('search_image_form.html', error='图片处理失败')
    return render_template('search_image_form.html', error=None)

@app.route('/test-video-data/', methods=('GET', 'POST'))
def test_video_data():
    if request.method == 'POST':
        name = request.form['name']
        cur = g.db.execute('select * from VDS where name=:vname', {'vname':name})
        result = []
        for row in cur.fetchall():
            result.append(row)
        if(len(result)!=1):
            if(len(result)==0):
                return render_template('search_video_form.html',  error='输入查询不到记录')
            else:
                return render_template('search_video_form.html', error='输入查询到了多个记录')
        data  = '../' + result[0][2]

        # after_data = 'static/test_image_temp/' + result[0][1]
        # before_data_web = '/static/' + result[0][2]
        # after_data_web = '/static/test_image_temp/' + result[0][1]
        before_data_web = '/static/' + result[0][2]
        after_data_web = None
        if(request.form['ControlSelect1']=='视频关键帧提取'):
            flag = utils.keyFrameExtraction(data, 'static/test_video_keyframe_temp')
        elif(request.form['ControlSelect1']=='随机视频切割(0-10秒)'):
            flag = utils.cutVideo(data, 'static/test_video_cut_temp', result[0][1], 0, random.randint(1,10))
            after_data_web = '/static/test_video_cut_temp/' + result[0][1]
        elif(request.form['ControlSelect1']=='视频合并（待续）'):
            return render_template('search_video_form.html', error='操作选择错误')
        else:
            return render_template('search_video_form.html', error='操作选择错误')
        if flag:
            # try:
            #   哈希计算          
            # except Exception as exc:
            #   return render_template('search_video_form.html', err='Exception: '+str(exc))
            return render_template(('result_video_form.html'), before=before_data_web, after=after_data_web)
        else:
            return render_template('search_video_form.html', error='视频处理失败')
    return render_template('search_video_form.html', error=None)

@app.route('/dataset-query/', methods=('GET', 'POST'))
def dataset_query():
    form = DatasetForm()
    app.logger.debug(request.method)
    app.logger.debug(form.validate())
    app.logger.debug(form.name)
    app.logger.debug(form.errors)
    app.logger.debug(form.name.raw_data)
    if form.validate():
        app.logger.debug('A value for debugging')
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        flash('Hello, {}. You have successfully signed up'
              .format(escape(form.name.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.index'))

    return render_template('dataset_query.html', form=form)

@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('chart.html', values=values, labels=labels, legend=legend)

if __name__ == '__main__':
    #  app.run(debug=True, host='0.0.0.0')
     app.run(host='0.0.0.0')
