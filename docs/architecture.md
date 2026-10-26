
# Архитектура
React/TypeScript frontend -> FastAPI backend -> PostgreSQL.
Backend обращается к отдельному mock-services контейнеру за синтетическими данными
компании и имитацией проверок. Скоринговая модель подключается через `SCORING_API_URL`.
Frontend не вызывает скоринг напрямую и не хранит секреты модели.
