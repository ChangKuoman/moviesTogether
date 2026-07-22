from sqlalchemy import Engine, text


def run_startup_migrations(engine: Engine) -> None:
    """One-off, idempotent schema fixups for SQLite databases created before a model change -
    there's no Alembic here (see CLAUDE.md), so this is the self-healing mechanism instead:
    it inspects the live table DDL and rebuilds only if it's still on the old shape. Safe to run
    on every startup - a no-op once migrated, and a no-op on a fresh database (create_all handles
    that with the current, already-correct schema).
    """
    if engine.dialect.name != "sqlite":
        return
    _migrate_half_star_ratings(engine)


def _migrate_half_star_ratings(engine: Engine) -> None:
    """Ratings used to be whole stars only (CHECK rating >= 1 AND rating <= 5, INTEGER column).
    Half stars need the column widened to allow 0.5 increments down to 0.5. SQLite has no
    ALTER TABLE ... DROP CONSTRAINT, so this rebuilds the table via the standard SQLite pattern:
    create the new shape, copy the data across, drop the old table, rename the new one into place.
    """
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'ratings'")
        ).first()
        if row is None or row[0] is None or "rating >= 0.5" in row[0]:
            return  # table doesn't exist yet, or already migrated

        conn.execute(
            text(
                """
                CREATE TABLE ratings_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    rating FLOAT NOT NULL,
                    rated_at DATETIME NOT NULL,
                    UNIQUE (user_id, item_id),
                    CHECK (rating >= 0.5 AND rating <= 5 AND CAST(rating * 2 AS INTEGER) = rating * 2),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (item_id) REFERENCES items (id)
                )
                """
            )
        )
        conn.execute(
            text(
                "INSERT INTO ratings_new (id, user_id, item_id, rating, rated_at) "
                "SELECT id, user_id, item_id, rating, rated_at FROM ratings"
            )
        )
        conn.execute(text("DROP TABLE ratings"))
        conn.execute(text("ALTER TABLE ratings_new RENAME TO ratings"))
        conn.execute(text("CREATE INDEX ix_ratings_user_id ON ratings (user_id)"))
        conn.execute(text("CREATE INDEX ix_ratings_item_id ON ratings (item_id)"))
