from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "wikiarticls" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "url" VARCHAR(512) NOT NULL,
    "title" VARCHAR(200) NOT NULL,
    "text" TEXT NOT NULL,
    "summary" TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_wikiarticls_url_ca63d9" ON "wikiarticls" ("url");
COMMENT ON TABLE "wikiarticls" IS 'Модель статьи из Wikipedia';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
