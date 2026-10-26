# Инструкция по запуску и демонстрации

Инструкция рассчитана на Windows, PowerShell и Docker Desktop.

## 1. Подготовка

1.  Установите и запустите Docker Desktop.

2.  Распакуйте проект.

3.  Откройте PowerShell и перейдите в корень проекта:

    ``` powershell
    cd "C:\Users\fortu\OneDrive\Desktop\test\smart-credit-cabinet"
    ```

4.  Убедитесь, что рядом находится `compose.yaml` или
    `docker-compose.yml`.

5.  Проверьте наличие `.env`. Если есть `.env.example`, создайте копию:

    ``` powershell
    Copy-Item .env.example .env
    ```

    Команда применима только при наличии `.env.example`. Заполните
    обязательные параметры по конфигурации проекта. Не добавляйте
    секреты в Git.

## 2. Запуск

``` powershell
docker compose up --build -d
docker compose ps
```

Первый запуск может занять несколько минут из-за скачивания образов и
сборки.

Если контейнер не запустился, посмотрите логи:

``` powershell
docker compose logs --tail=200
docker compose logs --tail=200 backend
docker compose logs --tail=200 scoring-service
```

## 3. Открытие интерфейса

-   Кабинет: http://localhost:5173
-   Backend: http://localhost:8000
-   Swagger backend: http://localhost:8000/docs
-   Swagger скоринга: http://localhost:9562/docs

Адреса зависят от опубликованных портов в Compose.

## 4. Сценарий демонстрации

1.  Откройте интерфейс.
2.  Зарегистрируйтесь или войдите в существующий аккаунт.
3.  Покажите главную страницу и профиль.
4.  Перейдите к анкете потребности в финансировании.
5.  Заполните анкету и покажите рекомендацию продукта.
6.  Выберите продукт и заполните заявку, включая сведения о компании.
7.  Отправьте заявку.
8.  Откройте карточку заявки и покажите статус, результат и выполненные
    проверки.
9.  Вернитесь на главную страницу и проверьте наличие заявки в истории.

Названия кнопок и полей могут отличаться в зависимости от текущей версии
интерфейса.

## 5. Проверка запроса к скорингу

В отдельном окне PowerShell выполните:

``` powershell
docker compose logs -f --since=1m scoring-service
```

Не закрывая окно, отправьте новую заявку через интерфейс. После отправки
проверьте появление новой строки:

``` text
"POST /score HTTP/1.1" 200 OK
```

`Ctrl+C` завершает просмотр логов, но не останавливает контейнеры.

Проверка доступности scoring-service из backend:

``` powershell
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://scoring-service:9562/docs', timeout=5).status)"
```

Ответ `200` означает, что backend может обратиться к документации
сервиса. Это не является полной проверкой корректности результата
скоринга.

## 6. Перезапуск с сохранением истории

``` powershell
docker compose down
docker compose up -d
```

После запуска войдите в тот же аккаунт и проверьте историю.

**Не используйте `docker compose down -v`, если нужно сохранить
данные.** Эта команда может удалить том PostgreSQL.

## 7. Пересборка после изменений

``` powershell
# Только frontend
docker compose up --build -d frontend

# Только backend
docker compose up --build -d backend

# Всё окружение
docker compose up --build -d
```

## 8. Частые проблемы

### `.env not found`

Создайте `.env` в корне проекта. Если есть `.env.example`, используйте
его как основу.

### Docker не может скачать базовые образы

Проверьте интернет и доступ к Docker Hub:

``` powershell
docker compose pull
docker compose up --build -d
```

### Сервис перезапускается

``` powershell
docker compose ps
docker compose logs --tail=200 ИМЯ_СЕРВИСА
```

Замените `ИМЯ_СЕРВИСА` именем из вывода `docker compose ps`.

### Скоринг недоступен

Проверьте состояние backend и scoring-service. Внутри Docker-сети
обращайтесь к `http://scoring-service:9562/score`, а не к `localhost`.

### История исчезла

Проверьте конфигурацию постоянного тома PostgreSQL и не удаляйте тома
командой `docker compose down -v`.

## 9. Чек-лист перед показом

-   [ ] Docker Desktop запущен.
-   [ ] Контейнеры работают (`docker compose ps`).
-   [ ] Интерфейс открывается.
-   [ ] Можно войти в кабинет.
-   [ ] Можно пройти анкету и отправить заявку.
-   [ ] Карточка заявки показывает статус и результат.
-   [ ] В логах виден запрос к скорингу после отправки заявки.
-   [ ] История сохраняется после обычного перезапуска.
-   [ ] `.env` с секретами не попал в публичный репозиторий.
