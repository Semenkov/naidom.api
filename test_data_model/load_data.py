# -*- coding: utf-8 -*-
#
# Скрипт для загрузки тестовых данных в базу. Для запуска в интерактивной сонсоли http://localhost:8000/console
# Этот скрипт запускается в отдельном NameSpace (чтобы не портить рабочие данные) !!!
#
__author__ = 'Sem'

import os
import pprint
from google.appengine.ext.remote_api import remote_api_stub
import getpass

from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.api import namespace_manager
import random
from google.appengine.ext import ndb
from naidomModel import NdUrlTest


def auth_func():
    return ('semenkov.su@gmail.com','$$ik0tn0')

#remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func, 'naidom-api.appspot.com')
remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func, 'localhost:8080')


def make_url(tagsCount):
    title = "{0}_title".format(random.randint(100, 300))
    tgs = [random.randint(100, 300) for x in range(tagsCount)]
    price = random.randint(500, 10000)
    houseSize = random.randint(50, 400)
    plotSize = random.randint(5, 20)
    n = NdUrlTest(title=title, price=price, houseSize=houseSize, plotSize=plotSize, tags=tgs)
    print n
    return n


def delete_all():
    # DELETE ALL entities
    ndb.delete_multi(NdUrlTest.query().fetch(keys_only=True))


def add_entities():
    for t in range(5):
        urls = []
        for i in range(10):
            urls.append(make_url(random.randint(1, 10)))
        ndb.put_multi(urls)


def reload_data():
    try:
        namespace_manager.set_namespace('-test-')
        delete_all()
        add_entities()
        print "Reloaded !"
    except:
        print "Error in reloading"


    
#reload_data()

namespace_manager.set_namespace('-test-')
#qry_cnt = NdUrlTest.query(NdUrlTest.tags.IN([ 120,130])).count()
#pprint.pprint( qry_cnt)

#qry_cnt2 = NdUrlTest.query(ndb.AND(NdUrlTest.tags==120, NdUrlTest.tags == 130 )).count()
#pprint.pprint( qry_cnt2)

#qry = NdUrlTest.query(ndb.AND(NdUrlTest.tags==150, NdUrlTest.tags == 151 ))
#qry_cnt2 = qry.count()
#qry_rows = qry.fetch(100)
#pprint.pprint( qry_cnt2)
#for r in qry_rows:
    #pprint.pprint( r)    
