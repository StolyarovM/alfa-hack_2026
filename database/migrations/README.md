
В MVP таблицы создаются при старте через SQLAlchemy `Base.metadata.create_all`.
Для командной разработки/production добавьте Alembic migrations и не используйте
`create_all` как механизм обновления схемы.
