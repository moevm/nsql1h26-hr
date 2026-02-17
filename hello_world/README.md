# Пример приложения

Базовый пример, демонстрирующий связку технологий проекта

## Запуск

Приложение работает в Docker-контейнерах. Запустите приложение:

```
make up
```

После запуска приложения проверьте порт frontend-части:
```
$ make logs

Starting the development server...

Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://172.18.0.4:3000
```

Для доступа к frontend, в данном примере, откройте в браузере `http://172.18.0.4:3000`

## Используемые технологии

- База данных: neo4j;
- Backend: Python, FastAPI;
- Frontend: React, JS, TS

