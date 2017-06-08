#!/usr/bin/python
# -- encoding:utf-8 --
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import os
from flask import Flask,url_for , request,redirect , render_template,make_response
from hashlib import sha256
from StringIO import StringIO
from commands import getstatusoutput
from pass_conf import *

appname = "pass"
app = Flask(appname)
hashkey = passcfg.loginhash
secertfile = passcfg.projname + os.sep + passcfg.secretfile

def gethash(raw):
    sha = sha256()
    sha.update(raw)
    return sha.hexdigest()

class dataobj(object):
    def __init__(self):
        self.pos = 0
        self.posend = 0
        self.title = ""
        self.body = []

def parse_file(fname):
    f = open(fname,"r")
    data = []
    while True :
        line = f.readline()
        if not line :
            break
        if line.startswith("# "):
            obj = dataobj()
            obj.title = line[2:]
            obj.pos = f.tell() - len(line)
            print "pos",obj.pos
            if len(data) > 0 :
                data[-1].posend = obj.pos -1
            obj.body = []
            data.append(obj)
        else :
            data[-1].body.append(line)
    data[-1].posend = f.tell()
    return data

@app.route("/")
def index():
    key = request.cookies.get('key','')
    hk = gethash(key) 
    if hk == hashkey :
        if not os.path.exists(secertfile) :
            return redirect(url_for("update"))
        data = parse_file(secertfile)
        resp = make_response( render_template("index.html",data=data) ) 
    else :
        resp = make_response( render_template("login.html") ) 
    return resp 

@app.route("/login",methods=["POST"])
def login():
    key = request.form.get('key','')
    resp = redirect(url_for("index"))
    resp.set_cookie('key', key)  
    return resp 

@app.route("/getdata2") # not crypte
def getdata():
    begin = int(request.args.get("from","0"))
    to = int(request.args.get("to","0"))
    f = open(secertfile,"r")
    f.seek(begin)
    return f.read(to-begin)


def decrypt(enstr,key):
    args = ['/usr/bin/openssl', 'enc', '-d','-a', '-aes-256-ecb', '-k', '8151381555']
    cmd = "echo %s | openssl enc -d -a -aes-256-ecb -k %s" % (enstr,key)
    status,out = getstatusoutput(cmd)
    print "openssl  status:",status
    return out

enpattern = re.compile(r'<\*\[.*?\]\*>')
def parse_data(fname , begin , to , key):
    f = open(fname,"r")
    f.seek(begin)
    sio = StringIO( f.read(to-begin) )
    data = []
    for line in sio :
        if line.startswith("# "):
            data.append(line)
        else :
            s1 = []
            pos = 0 
            for it in enpattern.finditer(line):
                s1.append( line[pos : it.start()] )
                enstr = line[it.start() + 3 : it.end()-3] 
                plainstr = decrypt(enstr,key)
                s1.append( plainstr )
                pos = it.end() 
            s1.append(line[pos:])
            data.append("".join(s1))
    return data

@app.route("/getdata")
def getdatadecrypt():
    key = request.cookies.get('key','')
    begin = int(request.args.get("from","0"))
    to = int(request.args.get("to","0"))
    data = parse_data(secertfile,begin,to,key)
    return "<br/>".join(data)

@app.route("/update")
def update():
    oldpath = os.getcwd()
    projdir = passcfg.projname
    os.chdir(projdir)
    cmd = "git pull;git checkout -- ."
    status,out = getstatusoutput(cmd)
    os.chdir(oldpath)
    return redirect(url_for("index"))


