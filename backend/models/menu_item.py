from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class MenuItem(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100))
    available = Column(Boolean, nullable=False, default=True)

    brand = relationship("Brand", back_populates="menu_items")
