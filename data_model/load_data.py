# -*- coding: utf-8 -*-
#
# script for load test data. ONLY ascii char because console run!
#
__author__ = 'SemenS'

import os
import sys
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
from naidomModel import Url, Tag, User, Bookmark, TagValue
from data_model.datas import tagsList



def auth_func():
    return ('semenkov.su@gmail.com','put_pwd_here')

#remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func, 'naidom-api.appspot.com')
remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', auth_func, 'localhost:8080')


def load_tags():
    for t in tagsList:
        Tag(id=t['id'], type=t['type'], name=t['name'], description=t['description']).put()


def load_users():
    User(user_id='test@user.ru',name='test@user.ru').put()


def add_random_bookmark(url):
    bm = Bookmark()
    bm.url = url.key
    bm.user = 'test@user.ru'
    bm.title = "Title - {0}".format(random.randint(100, 999))
    bm.object_type = random.randint(1, 3)
    bm.price = random.randint(100, 7999) * 1000
    bm.gps = ndb.GeoPt(51.0 + random.randint(1,100) / 50.0, 37.0 + random.randint(1,100) / 50.0)
    bm.put()
    add_random_bookmark_tag(bm, 101)
    add_random_bookmark_tag(bm, 102)
    add_random_bookmark_tag(bm, 201)
    add_random_bookmark_tag(bm, 202)
    add_random_bookmark_tag(bm, random.randint(1, 5))


def add_random_bookmark_tag(bm, tag_id):
    tv = TagValue()
    tv.bookmark = bm.key
    tag_key = ndb.Key(Tag, tag_id)
    tv.tag = tag_key

    tag = tag_key.get()
    if tag.type == 2:
        tv.value = random.randint(100, 999)
    if tag.type == 3:
        tv.value = "Value - {0} -".format(random.randint(100, 999))
    tv.put()


def add_random_url():
    url = "http://www.{0}test.ru".format(random.randint(100, 990))
    new_url = Url()
    new_url.url = url
    new_url.put()
    for bm in range(random.randint(3, 6)):
        add_random_bookmark(new_url)
    return new_url


def delete_all():
    for ent in [Tag, User,Bookmark, Url,  TagValue]:
        ndb.delete_multi(ent.query().fetch(keys_only=True))


def add_entities():
    for t in range(2):
        urls = []
        for i in range(5):
            urls.append(add_random_url())
        ndb.put_multi(urls)


def reload_data():
    try:
        namespace_manager.set_namespace('-test-')
        delete_all()
        load_tags()
        load_users()
        add_entities()
        print "Reloaded !"
    except:
        print "Error in reloading", sys.exc_info()[0]


    
reload_data()

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
