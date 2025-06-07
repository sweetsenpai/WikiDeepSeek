from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "wikiarticls" DROP COLUMN "test_field";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "wikiarticls" ADD "test_field" TEXT NOT NULL;"""
