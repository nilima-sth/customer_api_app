import asyncio
from typing import List, Optional

from sqlalchemy.orm import Session

import models
import schemas
from logger import get_logger

logger = get_logger(__name__)

#task-2 from here
def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    logger.info("READ all customers — skip=%d, limit=%d", skip, limit)
    result = db.query(models.Customer).offset(skip).limit(limit).all()
    logger.info("Fetched %d customer(s).", len(result))
    return result


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    logger.info("READ customer ID=%d", customer_id)
    customer = db.query(models.Customer).filter(
        models.Customer.customerNumber == customer_id
    ).first()
    if customer is None:
        logger.warning("Customer not found: ID=%d", customer_id)
    else:
        logger.info("Customer found: ID=%d name=%s", customer_id, customer.customerName)
    return customer


def create_customer(db: Session, data: schemas.CustomerCreate) -> models.Customer:
    logger.info("CREATE customer ID=%d name=%s", data.customerNumber, data.customerName)
    db_obj = models.Customer(**data.model_dump())
    try:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info("Customer created successfully: ID=%d", db_obj.customerNumber)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to create customer: %s", exc)
        raise
    return db_obj


def update_customer(
    db: Session, customer_id: int, updates: schemas.CustomerUpdate
) -> Optional[models.Customer]:
    logger.info("UPDATE customer ID=%d", customer_id)
    db_obj = get_customer(db, customer_id)
    if db_obj is None:
        return None
    changed = updates.model_dump(exclude_unset=True)
    for field, value in changed.items():
        setattr(db_obj, field, value)
    try:
        db.commit()
        db.refresh(db_obj)
        logger.info("Customer ID=%d updated. Fields: %s", customer_id, list(changed.keys()))
    except Exception as exc:
        db.rollback()
        logger.error("Failed to update customer ID=%d: %s", customer_id, exc)
        raise
    return db_obj


def delete_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    logger.info("DELETE customer ID=%d", customer_id)
    db_obj = get_customer(db, customer_id)
    if db_obj is None:
        return None
    try:
        db.delete(db_obj)
        db.commit()
        logger.info("Customer ID=%d deleted.", customer_id)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to delete customer ID=%d: %s", customer_id, exc)
        raise
    return db_obj


def get_customer_orders(db: Session, customer_id: int) -> List[models.Order]:
    logger.info("READ orders for customer ID=%d", customer_id)
    result = db.query(models.Order).filter(
        models.Order.customerNumber == customer_id
    ).all()
    logger.info("Found %d order(s) for customer ID=%d", len(result), customer_id)
    return result


def get_customer_payments(db: Session, customer_id: int) -> List[models.Payment]:
    logger.info("READ payments for customer ID=%d", customer_id)
    result = db.query(models.Payment).filter(
        models.Payment.customerNumber == customer_id
    ).all()
    logger.info("Found %d payment(s) for customer ID=%d", len(result), customer_id)
    return result



#task-3 from here
def _sync_count(db: Session, model) -> int:
    return db.query(model).count()


async def get_customers_count(db: Session) -> int:
    logger.debug("Counting customers...")
    n = await asyncio.to_thread(_sync_count, db, models.Customer)
    logger.debug("customers = %d", n)
    return n

async def get_orders_count(db: Session) -> int:
    logger.debug("Counting orders...")
    n = await asyncio.to_thread(_sync_count, db, models.Order)
    logger.debug("orders = %d", n)
    return n

async def get_products_count(db: Session) -> int:
    logger.debug("Counting products...")
    n = await asyncio.to_thread(_sync_count, db, models.Product)
    logger.debug("products = %d", n)
    return n

async def get_employees_count(db: Session) -> int:
    logger.debug("Counting employees...")
    n = await asyncio.to_thread(_sync_count, db, models.Employee)
    logger.debug("employees = %d", n)
    return n

async def get_offices_count(db: Session) -> int:
    logger.debug("Counting offices...")
    n = await asyncio.to_thread(_sync_count, db, models.Office)
    logger.debug("offices = %d", n)
    return n

async def get_payments_count(db: Session) -> int:
    logger.debug("Counting payments...")
    n = await asyncio.to_thread(_sync_count, db, models.Payment)
    logger.debug("payments = %d", n)
    return n

async def get_orderdetails_count(db: Session) -> int:
    logger.debug("Counting orderdetails...")
    n = await asyncio.to_thread(_sync_count, db, models.OrderDetail)
    logger.debug("orderdetails = %d", n)
    return n

async def get_productlines_count(db: Session) -> int:
    logger.debug("Counting productlines...")
    n = await asyncio.to_thread(_sync_count, db, models.ProductLine)
    logger.debug("productlines = %d", n)
    return n
