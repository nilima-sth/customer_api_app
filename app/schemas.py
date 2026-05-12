from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator

from logger import get_logger

logger = get_logger(__name__)


# ── shared ORM config ─────────────────────────────────────────────────────────
class OrmBase(BaseModel):
    model_config = {"from_attributes": True}


# ── Order (used inside CustomerOut) ──────────────────────────────────────────
class OrderOut(OrmBase):
    orderNumber:  int
    orderDate:    date
    requiredDate: date
    shippedDate:  Optional[date] = None
    status:       str
    comments:     Optional[str] = None


# ── Payment (used inside CustomerOut) ────────────────────────────────────────
class PaymentOut(OrmBase):
    checkNumber: str
    paymentDate: date
    amount:      Decimal


# ── Customer ──────────────────────────────────────────────────────────────────
class CustomerCreate(BaseModel):
    customerNumber:          int
    customerName:            str
    contactLastName:         str
    contactFirstName:        str
    phone:                   str
    addressLine1:            str
    addressLine2:            Optional[str]     = None
    city:                    str
    state:                   Optional[str]     = None
    postalCode:              Optional[str]     = None
    country:                 str
    salesRepEmployeeNumber:  Optional[int]     = None
    creditLimit:             Optional[Decimal] = None

    @field_validator("customerName", "contactLastName", "contactFirstName",
                     "phone", "addressLine1", "city", "country")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            logger.warning("Validation error: required field is blank.")
            raise ValueError("This field must not be blank.")
        return v


class CustomerUpdate(BaseModel):
    customerName:            Optional[str]     = None
    contactLastName:         Optional[str]     = None
    contactFirstName:        Optional[str]     = None
    phone:                   Optional[str]     = None
    addressLine1:            Optional[str]     = None
    addressLine2:            Optional[str]     = None
    city:                    Optional[str]     = None
    state:                   Optional[str]     = None
    postalCode:              Optional[str]     = None
    country:                 Optional[str]     = None
    salesRepEmployeeNumber:  Optional[int]     = None
    creditLimit:             Optional[Decimal] = None


class CustomerOut(OrmBase):
    customerNumber:          int
    customerName:            str
    contactLastName:         str
    contactFirstName:        str
    phone:                   str
    addressLine1:            str
    addressLine2:            Optional[str]     = None
    city:                    str
    state:                   Optional[str]     = None
    postalCode:              Optional[str]     = None
    country:                 str
    salesRepEmployeeNumber:  Optional[int]     = None
    creditLimit:             Optional[Decimal] = None
    orders:                  List[OrderOut]    = []
    payments:                List[PaymentOut]  = []


# ── Dashboard (Task 3) ────────────────────────────────────────────────────────
class OverallCountsOut(BaseModel):
    customers:    int
    orders:       int
    products:     int
    employees:    int
    offices:      int
    payments:     int
    orderdetails: int
    productlines: int
