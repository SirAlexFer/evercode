from datetime import datetime
from app.models.base import ModelBase
from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey, String, Integer, Numeric, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash


class User(ModelBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete")
    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete"
    )
    goals = relationship("Goals", back_populates="user", cascade="all, delete")

    def __init__(
        self, email: EmailStr, password: str, username: str, full_name: str
    ) -> None:
        self.email = email
        self.username = username
        self.full_name = full_name
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


# ------------------- Category Model -------------------
class Category(ModelBase):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    color = Column(String(7), nullable=True, default="#349DCA")  # Default white

    # Relationship back to user
    user = relationship("User", back_populates="categories")
    # Transactions under this category
    transactions = relationship(
        "Transaction", back_populates="category", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<Category {self.name} (User {self.user_id})>"


# ------------------- Transaction Model -------------------
class Transaction(ModelBase):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    item = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    location = Column(String(255), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    payment_method = Column(String(255), nullable=False)
    payment_type = Column(String(255), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"<Transaction {self.id} User {self.user_id} "
            f"Category {self.category_id} Item {self.item} "
            f"Quantity {self.quantity} Location {self.location} "
            f"Amount {self.amount}>"
        )


class Goals(ModelBase):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    date_goals = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="achieves")

    def __repr__(self) -> str:
        return f"<Achieve {self.name} (User {self.user_id})>"
