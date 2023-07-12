# Социальная сеть для публикации микроблогов, дневников и прочих мыслей!

[![CI](https://github.com/yandex-praktikum/socila_network/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


### Описание
Проект предназначит для публикации различных своих мыслей.

### Как запустить проект:
Перейти в него в командной строке:
```
cd yatube
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Технологии
Python 3.7.9
