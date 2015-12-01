# -*- coding: utf-8 -*-
#

"""NaiDom API implemented using Google Cloud Endpoints.

    Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""

import endpoints
import inspect
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from naidomModel import *
import naidom
import FT

ALLOWED_CLIENT_IDS = [
            '95036697911-u6ejmr11n3qpm90prtlp72sam83bk4h0.apps.googleusercontent.com',  # web site JavaScript
            '95036697911-n6lnr399388pt8ec9s77cm9icf9k0kbf.apps.googleusercontent.com',  # chrome.ext
            endpoints.API_EXPLORER_CLIENT_ID]
			
ALLOWED_ADMIN_CLIENT_IDS = [
            endpoints.API_EXPLORER_CLIENT_ID]

@endpoints.api(name='naidom', version='v0.2.1')
class NaiDomApi(remote.Service):

    @staticmethod
    def get_current_userid():
        user = endpoints.get_current_user()
        if user is None:
            raise endpoints.UnauthorizedException
        userid = user.email()
        if userid is None:
            raise endpoints.UnauthorizedException
        return userid

    @endpoints.method(UrlRequestMessage, IsInBaseResponseMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='url.isinbase', http_method='GET',
                      name='url.isinbase')
    def url_isinbase(self, request):
        """
        Проверяет, есть ли такой url в базе (среди персональных и общих ссылок)
        """
        try:
            url = request.url
            userid = NaiDomApi.get_current_userid()
            naidom.check_url(url)
        except NaiDomEx as ex:
            return IsInBaseResponseMessage(code=-1, text=ex.message)

        url_count, is_private = naidom.is_url_inbase(url, userid)
        if url_count == 0:
            return IsInBaseResponseMessage(code=0, text=u"Нет в базе URL:" + url, pages_count=0)
        else:
            if is_private:
                return IsInBaseResponseMessage(code=1, text=u"Есть в персональных ссылках:" + url,
                                               pages_count=url_count-1)
            else:
                    return IsInBaseResponseMessage(code=2, text=u"Есть в общих ссылках:" + url,
                                               pages_count=url_count)

    @endpoints.method(HouseSelectRequestMessage, HousesResponseMessage,
                      allowed_client_ids=ALLOWED_ADMIN_CLIENT_IDS,
                      path='oltp.export', http_method='POST',
                      name='oltp.export')
    def OLTP2OLAP_export(self, request):
        """
        Переносит N букмарков из OLTP базы в OLAP. Начинает с самых старых
        :param request: count - количество букмарков для переноса
        :return:
        """
        return 
		
    @endpoints.method(HouseSelectRequestMessage, HousesResponseMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='houses.select', http_method='GET',
                      name='houses.select')
    def houses_select(self, request):
        """
        Возвращает список закладок из базы
        :param request: url - url to add
        :return:
        """
        # 2do try - на случай не передачи некоторых параметров

        price_f = int(request.price_f) if (hasattr(request, 'price_f') and request.price_f is not None) else None
        price_t = int(request.price_t) if (hasattr(request, 'price_t') and request.price_t is not None) else None
        houseSize_f = int(request.houseSize_f) if (hasattr(request, 'houseSize_f') and request.houseSize_f is not None) else None
        houseSize_t = int(request.houseSize_t) if (hasattr(request, 'houseSize_t') and request.houseSize_t is not None) else None
        plotSize = request.plotSize if hasattr(request, 'plotSize') else None
        tags = request.tags if hasattr(request, 'tags') else None

        urls = naidom.houses_select(price_f=price_f, price_t=price_t,
                                houseSize_t=houseSize_t, houseSize_f=houseSize_f,
                                plotSize=plotSize, tags=tags)

        houses = []
        for url in urls:
            house = HouseMessage(title=url)
            houses.append(house)

        return HousesResponseMessage(code=0, houses=houses)

    #   --- House Add ---

    @endpoints.method(HouseMessage, ApiErrorMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='house.add', http_method='POST',
                      name='house.add')
    def house_add(self, request):
        """
        Добавляет дом в базу. Требует аутентификации.
        """
        userid = NaiDomApi.get_current_userid()
        return NaiDomApi.house_add_userid(request, userid)


    @endpoints.method(HouseMessage, ApiErrorMessage,
                      path='house.add.tu', http_method='POST',
                      name='house.add.tu')
    def house_add_tu(self, request):
        """
        Добавляет дом в базу
        Тестовый вариант, устанавливает фиксированный userid = test_user. Для отладки в plunker
        """
        return NaiDomApi.house_add_userid(request, naidom.naidom_test_user)

    @staticmethod
    def house_add_userid(request, userid):
        try:
            url = Url.from_string(request.url)
            naidom.check_url(url)
            naidom.house_add(request, userid)
            FT.ft_update_by_url(url)
        except NaiDomEx as ex:
            return ApiErrorMessage(code=-1, text=ex.message)

        return ApiErrorMessage(code=0, text=u"Добавлен в базу URL:" + request.url)

    #   --- Page Delete ---

    @endpoints.method(UrlRequestMessage, ApiErrorMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='house.delete', http_method='POST',
                      name='house.delete')
    def house_delete(self, request):
        """
        Удаляем персональную страницу из базы. Требует аутентификации.
        """
        userid = NaiDomApi.get_current_userid()
        return NaiDomApi.house_delete_userid(request, userid)


    @endpoints.method(UrlRequestMessage, ApiErrorMessage,
                      path='house.delete.tu', http_method='POST',
                      name='house.delete.tu')
    def house_delete_tu(self, request):
        """
        Удаляем персональную страницу из базы.
        Тестовый вариант, устанавливает фиксированный userid = test_user. Для отладки в plunker
        """
        return NaiDomApi.house_delete_userid(request, naidom.naidom_test_user)


    @staticmethod
    def house_delete_userid(request, userid):
        try:
            url = Url.from_string(request.url)
            naidom.check_url(url)
            #naidom.url_user_kind(request.url, userid)
            naidom.house_delete(url, userid)
            FT.ft_update_by_url(url)
        except NaiDomEx as ex:
            return ApiErrorMessage(code=-1, text=ex.message)

        return ApiErrorMessage(code=0, text=u"Удалён из базы URL:" + request.url)



    #   --- House By URL ---

    @endpoints.method(UrlRequestMessage, HouseResponseMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='house.byUrl', http_method='GET',
                      name='house.byUrl')
    def house_by_url(self, request):
        """
        Возвращает полную информацию о персональной странице по URL. Требует аутентификации
        """
        userid = NaiDomApi.get_current_userid()
        return NaiDomApi.house_by_url_userid(url=request.url, userid=userid)


    @endpoints.method(UrlRequestMessage, HouseResponseMessage,
                      path='house.byUrl.tu', http_method='GET',
                      name='house.byUrl.tu')
    def house_by_url_tu(self, request):
        """
        Возвращает информацию о странице  по URL (для тестового пользователя)
        """
        return NaiDomApi.house_by_url_userid(url=request.url, userid=naidom.naidom_test_user)


    @staticmethod
    def house_by_url_userid(url, userid):
        """
        Возвращает информацию о доме по URL и userid (ключи)
        """
        try:
            naidom.check_url(url)
            house = naidom.house_by_url(url, userid)
            h = HouseMessage()
            house.copy2message(h)
        except NaiDomEx as ex:
            return HouseResponseMessage(code=-1, text=ex.message)

        return HouseResponseMessage(code=0, house=h)


    #   --- HouseS By user ---

    @endpoints.method(message_types.VoidMessage, HousesResponseMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='houses.byUser', http_method='GET',
                      name='houses.byUser')
    def houses_by_user(self, request):
        """
        Возвращает список всех домов авторизованного пользователя.
        """

        userid = NaiDomApi.get_current_userid()
        return NaiDomApi.houses_by_user_userid(userid=userid)


    @endpoints.method(message_types.VoidMessage, HousesResponseMessage,
                      path='houses.byUser.tu', http_method='GET',
                      name='houses.byUser.tu')
    def houses_by_user_tu(self, request):
        """
        Возвращает список всех домов тестового пользователя. Пользователь "test_user"
        """

        return NaiDomApi.houses_by_user_userid(userid=naidom.naidom_test_user)

    @staticmethod
    def houses_by_user_userid(userid):

        try:
            houses = naidom.houses_by_user(userid=userid)
            hs = [house.copy2message(HouseMessage()) for house in houses]
            # hs = []
            # for house in houses:
            #     house_message = HouseMessage()
            #     house.copy2message(house_message)
            #     hs.append(house_message)
        except NaiDomEx as ex:
            return HousesResponseMessage(code=-1, text=ex.message)

        return HousesResponseMessage(code=0, houses=hs)

    @endpoints.method(UrlRequestMessage, TagsResponseMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='tags.byUrl', http_method='GET',
                      name='tags.byUrl')
    def tags_by_url(self, request):
        """
        Возвращает список меток ДРУГИХ пользователей по этой ссылке (если есть)
        """
        userid = NaiDomApi.get_current_userid()
        return NaiDomApi.tags_by_url_userid(request.url, userid)

    @endpoints.method(UrlRequestMessage, TagsResponseMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='tags.byUrl.tu', http_method='GET',
                      name='tags.byUrl.tu')
    def tags_by_url_tu(self, request):
        """
        Возвращает список меток ДРУГИХ пользователей для тесвого пользователя
        """
        return NaiDomApi.tags_by_url_userid(request.url, userid=naidom.naidom_test_user)

    @staticmethod
    def tags_by_url_userid(url, userid):
        """
        Возвращает используемые ДРУГИМИ пользователями метки о доме по URL и userid
        """
        try:
            tags = naidom.tags_by_url(url, userid)
            tags_msg = [TagMessage(name=tag[0], cnt=tag[1]) for tag in tags]
        except NaiDomEx as ex:
            return TagsResponseMessage(code=-1, text=ex.message)

        return TagsResponseMessage(code=0, tags=tags_msg)


    #   --- update Fusion Table by URL ---

    @endpoints.method(UrlRequestMessage, ApiErrorMessage,
                      allowed_client_ids=ALLOWED_CLIENT_IDS,
                      path='FT.updateByUrl', http_method='POST',
                      name='FT.updateByUrl')
    def ft_update_by_url(self, request):
        """
        Добаляет или  обновлет  информацию в  Fusion Table по URL.
        Требует аутентификации
        """
        userid = NaiDomApi.get_current_userid()
        return NaiDomApi.ft_update_by_url_userid(url=request.url, userid=userid)


    @staticmethod
    def ft_update_by_url_userid(url, userid):
        """
        Возвращает информацию о доме по URL и userid (ключи)
        """
        try:
            naidom.check_url(url)
            FT.ft_update_by_url(url)
        except NaiDomEx as ex:
            return ApiErrorMessage(code=-1, text=ex.message)

        return ApiErrorMessage(code=0)


APPLICATION = endpoints.api_server([NaiDomApi])

