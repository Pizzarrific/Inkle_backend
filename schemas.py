from pydantic import BaseModel

# -------- USERS --------
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True


# -------- POSTS --------
class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    owner_id: int

class PostOut(PostBase):
    id: int
    owner_id: int
    sentiment_label: str | None = None
    sentiment_score: str | None = None

    class Config:
        orm_mode = True
