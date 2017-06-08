#!/usr/bin/python
# -- encoding:utf-8 --
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import os
from flask import Flask,url_for , request,redirect , render_template,make_response

appname = "none"
app = Flask(appname)

@app.route("/")
def index():
    return "hello"

