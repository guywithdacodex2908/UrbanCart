from fastapi import FastAPI
from sqlalchemy.orm import Session
import models
from database import engine, Base, get_db
from payments import router as payments_router

app =  FastAPI(title="E-commerce API")
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return{"message":"E-commerce API is running"}

app.include_router(payments_router, prefix="/paymets", tags=["Payments"])