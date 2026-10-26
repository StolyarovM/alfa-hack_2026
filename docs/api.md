
# API
- POST `/api/v1/auth/login` — получить JWT.
- POST `/api/v1/auth/logout` — демо logout.
- GET `/api/v1/auth/me` — текущий пользователь.
- GET `/api/v1/profile` — профиль.
- GET `/api/v1/profile/checks` — проверки по заявкам.
- GET `/api/v1/products` — каталог.
- POST `/api/v1/products/recommend` — рекомендации.
- POST `/api/v1/applications` — создать заявку и запустить проверки.
- GET `/api/v1/applications` — список заявок текущего пользователя.
- GET `/api/v1/applications/{id}` — заявка текущего пользователя.
- POST `/api/v1/applications/{id}/retry` — повторный запуск.
Swagger: `/docs`.
