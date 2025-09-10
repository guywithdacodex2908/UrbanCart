from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email =  Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    user_type = Column(String, default="buyer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    seller_profile = relationship("Seller", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")

class Seller(Base):
    __tablename__ = "sellers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    account_phone =  Column(String, unique=True, index=True, nullable=False)
    cac_number =  Column(String, unique=True, index=True, nullable=False)
    user = relationship("User", back_populates="seller_profile")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id= Column(Integer, ForeignKey("users.id"), nullable=False)
    refrence = Column(String, unique=True, index=True, nullable=False)
    total_amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="NGN", nullable=False)
    status = Column(String, default="created", nullable=False)
    shipping_address = Column(String, nullable=False)
    paymet_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="orders")
    transactions = relationship("Transaction", back_populates="order",cascade="all,delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    reference = Column(String, unique=True, nullable=False)
    provider = Column(String, nullable=False)
    provider_reference = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="NGN", nullable=False)
    status = Column(String, default="pending", nullable=False)
    idemptency_key = Column(String, unique=True, nullable=True)
    provider_response = Column(JSON, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now)
    order = relationship("Order", back_populates="transactions")
    user = relationship("User", backref="transactions")

class EmailVerificationOTP(Base):
    __tablename__ = "email_verification_otps"
    id = Column(Integer, primary_key=True, index=True)
    email =  Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)