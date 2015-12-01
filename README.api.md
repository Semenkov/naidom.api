#NaiDom.API

Под-проект серверный API проекта **NaiDom bookmark**  

Содержание:

[TOC]

Серверное API по добавлению и просмотру закладок. Написано на python с использованием google App Engine и google endpoints. API используется в подпроектах:

* Chrome extension;
* сайт проекта.

## Боевой сервер

Функции API на боевом сервере можно дергать в API Explorer - [https://apis-explorer.appspot.com/apis-explorer/?base=https://naidom-api.appspot.com/_ah/api#p/](https://apis-explorer.appspot.com/apis-explorer/?base=https://naidom-api.appspot.com/_ah/api#p/)

Или конкретно API NaiDom v1 - [https://apis-explorer.appspot.com/apis-explorer/?base=https://naidom-api.appspot.com/_ah/api#p/naidom/v1/](https://apis-explorer.appspot.com/apis-explorer/?base=https://naidom-api.appspot.com/_ah/api#p/naidom/v1/)


## Модель данных

Данные хранятся в двух базах/моделях:

* Закладки - OLTP база всех закладок, ориентированная на быстрое добавление и редактирование;
* Объекты - OLAP база (суммарных) объектов, ориентированная на быстрый просмотр, поиск и фильтрование.

### OLTP - закладки

- Основная структура полиморфная, поля закладок заранее не известны, будут добавляться новые, матрица полей сильно разряжена;
- Есть небольшое подмножество обязательных полей. Обязательных как в базе так и в итерфейсе добавления/редактирования. Эти поля известны, известны их типы и названия;


### OLAP - объекты

OLAP структура ориентирована на поиск и просмотр. **"Только для чтения"** для пользователей. Исходные данные - полиморфная OLTP база. Отображение OLTP в OLAP происходит автоматически процессом обновления OLAP. 

Для быстрого поиска полиморфную базу преобразуем в разряженную RO базу на основе Google FusionTables. По тестам она быстрая и вроде не дорогая в содержании. Нужно проверить.

#### Обровление OLAP

Процесс обновления OLAP срабатывает периодически (повторяющаяся задача на сервере). Алгоритм:

- берём N объектов (url) с наиболее ранними НЕВНЕСЁННЫМИ правками;
- вычисляем для них суммарные атрибуты по всем закладкам объекта (url);
- обновляем объект, ставим дату последнего обновления

В зависимости от количества закладок, правок и нагрузки, нужно править параметры срабатывания алгоритма, такие как:

- как часто запускать обновление;
- сколько объектов обновлять за один раз.

## Разработка и тестирование

Разработка и тестирование ведутся на отдельном **локальном** сервере, на котором поднято своё API.

Для запуска локального сервера для разработки нужно выполнить файл api_local_start.bat, который запустит локальный сервер и локальное datastore.


**Для отладки** на локальном компьютере:

+ Для запуска API запустить  [file:\\D:\Sem\Dropbox\NaiDom_bm\naidom.api\api_local_start.bat](file:\\D:\Sem\Dropbox\NaiDom_bm\naidom.api\api_local_start.bat);
+ Для просмотра [API консоли](https://apis-explorer.appspot.com/apis-explorer/?base=https://localhost:8080/_ah/api#p/);
+ Developer (local) console [http://localhost:8000/instances](http://localhost:8000/instances) (включая локальное хранилище)

> Обрати внимание, что тестирование web интерфейса Chrome расширения ведется с использованием **боевого API** а не тестового/локального!

## SDK

App engine Python SDK часто обновляется. Свежую копию можно скачать здась [https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)