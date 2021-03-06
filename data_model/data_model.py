# -*- coding: utf-8 -*-
#
__author__ = 'Sem'

from protorpc import messages
from protorpc import message_types
import datetime
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from google.appengine.ext.ndb import polymodel

# -------------   Part I.  NDB models -------------------











# url - ключ этого класса
class Url(ndb.Model):
    cnt = ndb.IntegerProperty()

    def calc_cnt(self):
        return House.query(ancestor=self.key).count()

    @staticmethod
    def from_string(url):
        # Преобразует URL для использования в виде ключа. Пока - просто перевод в нижний регистр
        # Есть потенциальная проблемма если параметры URL case sensitive
        return url.lower()


# userid - ключ этого класса
class House(ndb.Model):
    attrs_for_message = [
        'page_kind', 'title', 'price',
        'houseSize', 'plotSize',
        'tags', 'note', 'date'
    ]   # gps преобразуется особым способом

    userid = ndb.StringProperty(required=True)
    page_kind = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty()
    gps = ndb.GeoPtProperty()
    price = ndb.IntegerProperty()
    houseSize = ndb.IntegerProperty()
    plotSize = ndb.IntegerProperty()
    tags = ndb.StringProperty(repeated=True)
    note = ndb.StringProperty()
    #mdDescription = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    #export2FT_date = ndb.DateTimeProperty()
    #ftROWID = ndb.IntegerProperty()
    debugMessage = ndb.StringProperty()

    def msg(self, msg):
        tm = datetime.datetime.now().strftime(u"%A, %d. %B %Y %I:%M%p")
        self.debugMessage = u"{1} : {0}".format(tm, msg)

    def copy2message(self, dest):
        # копирует свои элементы в message объект

        for attr in House.attrs_for_message:
            if hasattr(self, attr):
                v = getattr(self, attr)
                if v is not None:
                    setattr(dest, attr, v)
        # нестрандартные поля
        dest.url = self.key.parent().id()
        if self.gps is not None:
            dest.gps = [self.gps.lat, self.gps.lon]

        return dest

    def copy_from_message(self, src):
        # копирует свои элементы из объект Message

        for attr in House.attrs_for_message:
            if hasattr(src, attr):
                v = getattr(src, attr)
                if v is not None:
                    setattr(self, attr, v)
        # нестрандартные поля
        if src.gps is not None and len(src.gps) == 2:
            pt = ndb.GeoPt(src.gps[0], src.gps[1])
            self.gps = pt
# // Class House




class Page(ndb.Model):
    userid = ndb.StringProperty()
    title = ndb.StringProperty()
    price = ndb.IntegerProperty()
    houseSize = ndb.IntegerProperty()
    plotSize = ndb.IntegerProperty()
    gps = ndb.GeoPtProperty()
    tags = ndb.IntegerProperty(repeated=True)
    note = ndb.StringProperty()


# -------------   Part II.  MESSAGES  -------------------


# Используется и в запросах и в ответах. Не используемые поля не указываются
class HouseMessage(messages.Message):
    url = messages.StringField(1)
    page_kind = messages.IntegerField(2, required=True)
    title = messages.StringField(3, required=True)
    price = messages.IntegerField(4)
    houseSize = messages.IntegerField(5)
    plotSize = messages.IntegerField(6)
    gps = messages.FloatField(7, repeated=True)
    date = message_types.DateTimeField(8)
    note = messages.StringField(9)
    tags = messages.StringField(10, repeated=True)


#   << ------  II.a Входящие типы сообщений (запросы)-------------- >>

class UrlRequestMessage(messages.Message):
    url = messages.StringField(1, required=True)


class HouseSelectRequestMessage(messages.Message):
    price_f = messages.StringField(1)
    price_t = messages.StringField(2)
    houseSize_f = messages.StringField(3)
    houseSize_t = messages.StringField(4)
    plotSize_f = messages.StringField(5)
    plotSize_t = messages.StringField(6)
    tags = messages.StringField(7,  repeated=True)


#   << ------  II.b Исходящие типы сообщений (ответы)  --------------  >>

class ApiErrorMessage(messages.Message):
    code = messages.IntegerField(1)
    text = messages.StringField(2)

class IsInBaseResponseMessage(messages.Message):
    code = messages.IntegerField(1)
    text = messages.StringField(2)
    pages_count = messages.IntegerField(3)

# ---   Tags ответы  ---


class TagMessage(messages.Message):
    name = messages.StringField(1)
    cnt = messages.IntegerField(2)


class TagsResponseMessage(messages.Message):
    code = messages.IntegerField(1)
    text = messages.StringField(2)
    tags = messages.MessageField(TagMessage, 3, repeated=True)


# --- House ответ ---


class HouseResponseMessage(messages.Message):
    code = messages.IntegerField(1)
    text = messages.StringField(2)

    house = messages.MessageField(HouseMessage, 3)


# --- HouseS (list) ответы ---

class HousesResponseMessage(messages.Message):
    code = messages.IntegerField(1)
    text = messages.StringField(2)

    houses = messages.MessageField(HouseMessage, 3, repeated=True)

# ------  Конец определения классов сообщений ---------------------------------------


#   << ------  III Пользовательские исключения  --------------  >>

class NaiDomEx(Exception): pass
