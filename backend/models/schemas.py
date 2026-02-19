from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel as PydBase


class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    category: Optional[str]
    available: bool
    model_config = {"from_attributes": True}


class BrandOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    model_config = {"from_attributes": True}


class CartItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)


class MenuItemCreate(BaseModel):
    brand_id: int
    name: str
    price: float
    category: Optional[str] = None
    available: Optional[bool] = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    available: Optional[bool] = None


class OrderCreate(BaseModel):
    brand_slug: str
    items: List[CartItem]
    customer_name: str
    customer_phone: Optional[str] = None
    address: Optional[str] = None
    payment_method: str = "COD"


class OrderOut(BaseModel):
    id: int
    brand_id: int
    total: float
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: float
    name: Optional[str] = None
    model_config = {"from_attributes": True}


class AdminOrderOut(BaseModel):
    id: int
    brand_id: int
    total: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]
    model_config = {"from_attributes": True}


class OrderStatusUpdate(PydBase):
    status: str


class Token(PydBase):
    access_token: str
    token_type: str


class TokenData(PydBase):
    username: str | None = None


class LoginRequest(PydBase):
    username: str
    password: str


class UserOut(PydBase):
    id: int
    username: str
    role: str
    model_config = {"from_attributes": True}
