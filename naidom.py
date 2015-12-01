# -*- coding: utf-8 -*-
#
__author__ = 'Sem'

import re
import os
import logging
import datetime
from google.appengine.api import users
from google.appengine.ext import ndb


from naidomModel import Url, House, NdUrlTest, NaiDomEx

logger = logging.getLogger('NaiDom-api')
logger.setLevel(logging.INFO)


# используется для тестовых методов где пользователь фиксирован
naidom_test_user = 'test_user'


class ND:
    is_develop_flag = None

    @staticmethod
    def is_develop():
        if ND.is_develop_flag is None:
            if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
                ND.is_develop_flag = True
            else:
                ND.is_develop_flag = False
        return ND.is_develop_flag


def check_url(url):
    """
    Проверка url на валидность
    :param url:
    :return:
    """
    if len(url) == 0:
        raise NaiDomEx(u"Пустой url")
    if len(url) > 300:
        raise NaiDomEx(u"Слишком длинный url")

    #match = re.search(r'^(?=[^&])(?:(?P<scheme>[^:/?#]+):)?(?://(?P<authority>[^/?#]*))?(?P<path>[^?#]*)(?:\?(?P<query>[^#]*))?(?:#(?P<fragment>.*))?', url)
    match = re.search(r'^((http|https|ftp)\://)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(:[a-zA-Z0-9]*)?/?([a-zA-Z0-9\-\._\?\,\'/\\\+&amp;%\$#\=~])*$', url)

    if not match:
        raise NaiDomEx(u"Неправильный url")


def is_url_inbase(url, userid):
    """
    Проверка нахождения ссылки в базе
    """
    url_key = ndb.Key(Url, url.lower())
    url_db = url_key.get()
    if url_db is None:
        return 0, None
    house_key = ndb.Key(Url, url.lower(), House, userid)
    house_db = house_key.get()
    if house_db is None:
        return url_db.cnt, False
    else:
        return url_db.cnt, True


def url_user_kind(url, userid):
    """
    Проверка нахождения ссылки среди ссылок _пользователя_ и возвращает тип ссылки
    """
    house_key = ndb.Key(Url, url.lower(), House, userid)
    house_db = house_key.get()
    if house_db is None:
        raise NaiDomEx(u"URL не найден:" + url)
    else:
        return house_db.page_kind




@ndb.transactional
def house_add(house_msg, userid):
    """
    Добавляет/обновляет персональную страницу
    """
    url = house_msg.url
    url_key = ndb.Key(Url, url)
    db_url = url_key.get()
    if db_url is None:  # нет в таблице url, создать
        db_url = Url(cnt=0)
        db_url.key = url_key
        db_url.put()

    cnt = db_url.calc_cnt()
    house_key = ndb.Key(Url, url, House, userid)
    db_house = house_key.get()
    if db_house is None:
        db_url.cnt = cnt+1
        msg = u"добавлено в базу"
    else:
        db_url.cnt = cnt
        msg = u"обновлено"
    db_house = House(userid=userid, page_kind=1) #house если не задан
    db_house.key = house_key
    db_house.copy_from_message(house_msg)
    db_house.msg(msg)
    db_house.put()
    db_url.put()    # update url count


@ndb.transactional
def house_delete(url, userid):
    """
    Удаляет персональную ссылку
    """
    url_key = ndb.Key(Url, url)
    db_url = url_key.get()

    cnt = db_url.calc_cnt()
    house_key = ndb.Key(Url, url, House, userid)

    house_key.delete()
    if cnt == 1:
        url_key.delete()    # последняя персональная страница, удаляем url
    else:
        db_url.cnt = cnt-1  # НЕ последняя персональная страница, уменьшаем счетчик в url
        db_url.put()


def houses_select(price_f, price_t, houseSize_f, houseSize_t, plotSize, tags):

    q = NdUrlTest.query()
    if price_f is not None:
        q = q.filter(NdUrlTest.price >= price_f)
    if price_t is not None:
        q = q.filter(NdUrlTest.price <= price_t)

    if houseSize_f is not None:
        q = q.filter(NdUrlTest.houseSize >= houseSize_f)
    if houseSize_t is not None:
        q = q.filter(NdUrlTest.houseSize <= houseSize_t)
    for t in tags:
        q = q.filter(NdUrlTest.tags == t)

    ret = []
    for url in q.fetch(11):
        ret.append(url.title)

    return ret


def house_by_url(url_str, userid):
    house_key = ndb.Key(Url, url_str.lower(), House, userid)
    house = house_key.get()
    if house is None:
        raise NaiDomEx(u"Нет такого url")
    # house.url = house_key.id()
    return house


def load2xml(url):
    valid_domains_regs = [
        r'^(https?:\/\/)?([\da-z\.-]+)\.([Rr][Uu])([\/\w \.-]*)*\/?$', #  xx.RU
    ]
    for reg in valid_domains_regs:
        if re.search(reg, url):
            return True
    return False


def houses_by_user(userid):

    q = House.query(House.userid == userid)

    return [house for house in q.fetch(100)]


def tags_by_url(url_str, userid):

    check_url(url_str.lower())
    url_key = ndb.Key(Url, url_str.lower())
    q = House.query(ancestor=url_key).filter(House.userid != userid)

    tags_dict = {}
    for house in q.fetch():
        for tag in house.tags:
            tags_dict[tag] = tags_dict[tag]+1 if tag in tags_dict else 1
    # возвращаем сортированный массив пар (метка,количество_использований)
    return sorted(tags_dict.items(), key=lambda t: t[1], reverse=True)
