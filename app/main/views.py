# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: views.py
# @Date:   2019-03-13 10:07:12
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2020-06-23 01:05:46

from flask import render_template, abort, request,jsonify, redirect,url_for,flash, current_app, send_from_directory
from . import main
from sqlalchemy import desc
from .. import db
from flask_login import login_user, logout_user, login_required,current_user
from ..models import User, Weidian, LoginLog
import os,json,time
from ..email import send_email
from .forms import JobDateForm,JobCronForm,JobIntervalForm
import json as simplejson
import requests, subprocess, json, datetime
from datetime import date
from app.job.views import show_jobs,job_log
from ..models import TaskLog
from .. import scheduler
from app.job.core import jobfromparm
from ..dingding import dingding
#demo环境切换
DEMO_ENV=False

@main.route('/dingding',methods=['POST'])
def dingding():
    # USDT 充值通知
    if request.method == "POST":
        pay_method = json.loads(request.form.get('data'))['pay_methods']

        dingding_send_info = {
            "address": request.headers.get('X-Forwarded-For',request.remote_addr) ,
            "agent": str(request.user_agent),
            "title": "***[{0}支付通知***[MSG]".format( pay_method)
        }
        dingding(dingding_send_info)
        try:
            dingding(dingding_send_info)
            return jsonify({"result":True, "message":"OK, 您的付款信息已經通知客服小姐姐啦~.\n30分鐘內為您開通VIP~"})
        except Exception as why:
            print("*** 支付完成後的通知失敗 ***", why)
            return jsonify({"result":False, "message":"x"})

@main.route('/')
# @login_required
def index():
    ''' 返回主页内容 '''
    if not current_user.is_authenticated:
        return redirect('auth/login')
    else:
        task =  show_jobs()
        return render_template('index.html',task=task)

@main.route('/joblist')
@login_required
def joblist():
    ''' 返回作业任务列表 '''
    return render_template('all_job_list.html')

@main.route('/joblog')
@login_required
def joblog():
    ''' 返回job日志 '''
    return render_template('all_job_log.html')

@main.route('/caidan')
# @login_required
def caidan():
    ''' others '''
    return render_template('others.html')

@main.route('/dellog',methods=['DELETE'])
@login_required
def dellog():
    ''' 删除job日志 '''
    response = {}
    data = request.get_json(force=True)
    db_id = data.get('id')
    job_id = data.get('task_id')
    try:
        db.session.query(TaskLog).filter_by(id=db_id).delete()
        response['status']=True
        response['msg'] = "job [%s] joblog delete success!" % job_id
    except Exception as e:
        response["msg"] = "删除失败 --- %s" % e
        response['status'] = False    
    return jsonify(response)

@main.route('/createjob',methods=['POST','GET'])
@login_required
def createjob():
    ''' 创建定时任务 '''
    form_date = JobDateForm()
    form_cron = JobCronForm()
    form_interval = JobIntervalForm()
   
    # date job
    if form_date.submit_date.data and form_date.validate_on_submit():
        data = {
            "id": form_date.job_id.data,
            "cmd": form_date.func_cmd.data,
            "run_date": form_date.run_date.data,
            "trigger_type": "date"
        }
        response = {'status': '-1'}
        try:
            data = data
            if DEMO_ENV:
                job_id = jobfromparm(scheduler,**data)
                flash('定时任务 {0} 添加成功'.format(data['id']),'success')
            else:
                flash("Demo环境已关闭任务添加功能","danger") 
        except Exception as e:
            response['msg'] = str(e)
            print(e)
            flash('定时任务 {0} 添加失败 {1}'.format(data['id'],e),'danger')

    # cron job
    if form_cron.submit_cron.data and form_cron.validate_on_submit():
        data = {
            "id": form_cron.job_id.data,
            "cmd": form_cron.func_cmd.data,
            "cron": form_cron.cron_date.data,
            "trigger_type": "cron"
        }
        response = {'status': '-1'}
        try:
            data = data
            print (data)
            if DEMO_ENV:
                job_id = jobfromparm(scheduler,**data)
                flash('定时任务 {0} 添加成功'.format(data['id']),'success')
            else:
                flash("Demo环境已关闭任务添加功能","danger") 
        except Exception as e:
            response['msg'] = str(e)
            print(e)
            flash('定时任务 {0} 添加失败 {1}'.format(data['id'],e),'danger')
    
    # interval job
    if form_interval.submit_interval.data and form_interval.validate_on_submit():
        data = {
            "id": form_interval.job_id.data,
            "cmd": form_interval.func_cmd.data,
            "interval_time": form_interval.interval_time.data,
            #"start_date": form_interval.start_date.data,
            #"end_date": form_interval.end_date.data,
            "trigger_type": "interval"
        }
  
        response = {'status': '-1'}
        try:
            data = data
            print (data)
            if not DEMO_ENV:
                job_id = jobfromparm(scheduler,**data)
                flash('定时任务 {0} 添加成功'.format(data['id']),'success')
            else:
                flash("Demo环境已关闭任务添加功能","danger") 
        except Exception as e:
            response['msg'] = str(e)
            print(e)
            flash('定时任务 {0} 添加失败 {1}'.format(data['id'],e),'danger')
           
    return render_template('create_job.html',form_date=form_date,form_cron=form_cron,form_interval=form_interval)

@main.route('/stdout/<id>')
def stdout(id):
    result = db.session.query(TaskLog).filter_by(id=id).first()
    stdout = result.to_json()['stdout']
    return render_template('stdout.html',stdout=stdout)

@main.route('/loginlog')

def loginlog():
    data = []
    data_list = LoginLog.query.all()
    for i in data_list:
        data.append(i.to_json())
    for s in data:
        print (s['id'])
    return render_template('login_log.html',data=data)
