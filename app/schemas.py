from pydantic import BaseModel


class TestBase(BaseModel):
    text: str


class TestCreate(TestBase):
    pass


class Test(TestBase):
    id: int

    class Config:
        orm_mode = True
