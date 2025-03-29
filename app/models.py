import datetime
import enum

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship

Base: DeclarativeMeta = declarative_base()


class TimeStamp(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


# Define the join table for Role and Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Permission(TimeStamp):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    roles = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )


class Role(TimeStamp):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    users = relationship("User", back_populates="role")
    permissions = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )


# User Model
class User(TimeStamp):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")


class LeadStatus(str, enum.Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    LOST = "Lost"


class Lead(TimeStamp):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    utm_source = Column(String, nullable=True)
    utm_medium = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)
    utm_content = Column(String, nullable=True)
    utm_term = Column(String, nullable=True)


class QuotationStatus(str, enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    SENT = "Sent"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Quotation(TimeStamp):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    status = Column(
        Enum(QuotationStatus), default=QuotationStatus.DRAFT, nullable=False
    )
    total_price = Column(Float, default=0.0)
    # Relationship to the lead
    lead = relationship("Lead", backref="quotations")
    # One-to-many relationship to line items
    line_items = relationship(
        "QuotationLineItem", back_populates="quotation", cascade="all, delete-orphan"
    )


class QuotationLineItem(TimeStamp):
    __tablename__ = "quotation_line_items"
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    # Back reference to quotation
    quotation = relationship("Quotation", back_populates="line_items")


class EntityType(str, enum.Enum):
    LEAD = "Lead"
    QUOTATION = "Quotation"
    USER = "User"
    ROLE = "Role"
    PERMISSION = "Permission"
    QUOTATION_LINE_ITEM = "QuotationLineItem"


class AuditLog(TimeStamp):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(Enum(EntityType), nullable=False)
    entity_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    before_values = Column(JSON, nullable=True)
    after_values = Column(JSON, nullable=True)
    context = Column(String, nullable=True)
    user = relationship("User", backref="audit_logs")
