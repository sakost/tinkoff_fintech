# Books holder

### Description:
Management of books

### Задание

#### Бизнес-логика

Реализовать бэкенд-сервер, который будет хранить в себе сущность пользователя и книг, связанных с данным пользователем.
Реализовать доступ к данным на сервере.

#### Сущности
1. Пользователь
1. Книги с заголовками и текстом

#### Технологии
1. fastapi
1. sqlalchemy
1. typer
1. pydantic

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format

## Run

Чтобы запустить проект в докере, нужно запустить `docker-compose`:

    docker-compose -f docker-compose.yml up

