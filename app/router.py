import asyncio
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/customers", response_model=List[schemas.CustomerOut])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info("GET /customers  skip=%d limit=%d", skip, limit)
    customers = crud.get_customers(db, skip=skip, limit=limit)
    logger.info("GET /customers → returned %d record(s)", len(customers))
    return customers


@router.get("/customers/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    logger.info("GET /customers/%d", customer_id)
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        logger.warning("GET /customers/%d → 404 Not Found", customer_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found."
        )
    logger.info("GET /customers/%d → 200 OK", customer_id)
    return customer


@router.post("/customers", response_model=schemas.CustomerOut, status_code=201)
def create_customer(data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    logger.info("POST /customers  ID=%d", data.customerNumber)
    if crud.get_customer(db, data.customerNumber):
        logger.warning("POST /customers → 400 duplicate ID=%d", data.customerNumber)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer {data.customerNumber} already exists."
        )
    customer = crud.create_customer(db, data)
    logger.info("POST /customers → 201 Created  ID=%d", customer.customerNumber)
    return customer


@router.put("/customers/{customer_id}", response_model=schemas.CustomerOut)
def update_customer(
    customer_id: int, updates: schemas.CustomerUpdate, db: Session = Depends(get_db)
):
    logger.info("PUT /customers/%d", customer_id)
    updated = crud.update_customer(db, customer_id, updates)
    if updated is None:
        logger.warning("PUT /customers/%d → 404 Not Found", customer_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found."
        )
    logger.info("PUT /customers/%d → 200 OK", customer_id)
    return updated


@router.delete("/customers/{customer_id}", response_model=schemas.CustomerOut)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    logger.info("DELETE /customers/%d", customer_id)
    deleted = crud.delete_customer(db, customer_id)
    if deleted is None:
        logger.warning("DELETE /customers/%d → 404 Not Found", customer_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found."
        )
    logger.info("DELETE /customers/%d → 200 OK", customer_id)
    return deleted


@router.get("/customers/{customer_id}/orders", response_model=List[schemas.OrderOut])
def get_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    logger.info("GET /customers/%d/orders", customer_id)
    if crud.get_customer(db, customer_id) is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    orders = crud.get_customer_orders(db, customer_id)
    logger.info("GET /customers/%d/orders → %d order(s)", customer_id, len(orders))
    return orders


@router.get("/customers/{customer_id}/payments", response_model=List[schemas.PaymentOut])
def get_customer_payments(customer_id: int, db: Session = Depends(get_db)):
    logger.info("GET /customers/%d/payments", customer_id)
    if crud.get_customer(db, customer_id) is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    payments = crud.get_customer_payments(db, customer_id)
    logger.info("GET /customers/%d/payments → %d payment(s)", customer_id, len(payments))
    return payments


@router.get("/customers/count", response_model=dict)
async def count_customers(db: Session = Depends(get_db)):
    logger.info("GET /customers/count")
    return {"customers": await crud.get_customers_count(db)}

@router.get("/orders/count", response_model=dict)
async def count_orders(db: Session = Depends(get_db)):
    logger.info("GET /orders/count")
    return {"orders": await crud.get_orders_count(db)}

@router.get("/products/count", response_model=dict)
async def count_products(db: Session = Depends(get_db)):
    logger.info("GET /products/count")
    return {"products": await crud.get_products_count(db)}

@router.get("/employees/count", response_model=dict)
async def count_employees(db: Session = Depends(get_db)):
    logger.info("GET /employees/count")
    return {"employees": await crud.get_employees_count(db)}

@router.get("/offices/count", response_model=dict)
async def count_offices(db: Session = Depends(get_db)):
    logger.info("GET /offices/count")
    return {"offices": await crud.get_offices_count(db)}

@router.get("/payments/count", response_model=dict)
async def count_payments(db: Session = Depends(get_db)):
    logger.info("GET /payments/count")
    return {"payments": await crud.get_payments_count(db)}

@router.get("/orderdetails/count", response_model=dict)
async def count_orderdetails(db: Session = Depends(get_db)):
    logger.info("GET /orderdetails/count")
    return {"orderdetails": await crud.get_orderdetails_count(db)}

@router.get("/productlines/count", response_model=dict)
async def count_productlines(db: Session = Depends(get_db)):
    logger.info("GET /productlines/count")
    return {"productlines": await crud.get_productlines_count(db)}


# ══════════════════════════════════════════════════════════════════════════════
# TASK 3 — AGGREGATED CONCURRENT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/overall_counts", response_model=schemas.OverallCountsOut)
async def overall_counts(db: Session = Depends(get_db)):
    logger.info("GET /overall_counts — launching 8 concurrent queries")
    start = time.perf_counter()

    (
        customers, orders, products, employees,
        offices, payments, orderdetails, productlines
    ) = await asyncio.gather(
        crud.get_customers_count(db),
        crud.get_orders_count(db),
        crud.get_products_count(db),
        crud.get_employees_count(db),
        crud.get_offices_count(db),
        crud.get_payments_count(db),
        crud.get_orderdetails_count(db),
        crud.get_productlines_count(db),
    )

    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "GET /overall_counts — completed in %.2f ms | "
        "customers=%d orders=%d products=%d employees=%d "
        "offices=%d payments=%d orderdetails=%d productlines=%d",
        elapsed, customers, orders, products, employees,
        offices, payments, orderdetails, productlines,
    )

    return schemas.OverallCountsOut(
        customers=customers, orders=orders, products=products,
        employees=employees, offices=offices, payments=payments,
        orderdetails=orderdetails, productlines=productlines,
    )
