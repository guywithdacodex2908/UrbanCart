from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, Order
import requests
from datetime import datetime
import os

router = APIRouter()

PAYSTACK_SECRET_KEY =  "sk_test_6ca9de86ea249c22a66fec3103d474584703f8c0"
@router.post("/initiate-payment/")
def initiate_payment(email: str, amount: int):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
               "content-Type": "application/json",
               }
    data = {
        "emaill": email,
        "amount": amount,
    }
    response = requests.post(url, json=data, headers = headers)
    result = response.json()

    if not result["status"]:
        return {"error": "payment initialization failed", "details": result}
    return {"payment_url": result["data"] ["authorization_url"]}

@router.get("/verify-payment/{reference}")
def verify_payment(reference: str, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter_by(provider_reference=reference).first()
    if not transaction:
        transaction = db.query(Transaction).filter_by(reference=reference).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found in our records")
    if transaction.status == "success":
        return {"status": "already_paid", "transaction_id": transaction.id}
    provider_ref = transaction.provider_reference or reference
    try:
        url = f"https://api.paystack.co/transaction/verify/{provider_ref}"
        headers = {"Authorization":f"Bearer {PAYSTACK_SECRET_KEY}"}
        resp = requests.get(url, headers=headers, timeout=10)
        paystack_result = resp.json()
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Could not reach payment provider")
    if not paystack_result.get("status"):
        transaction.provider_response = paystack_result
        transaction.status = "failed"
        db.commit()
        db.refresh(transaction)
        raise HTTPException(status_code=400, detail="provider verification failed")
    data = paystack_result.get("data", {})
    transaction.provider_reference = data.get("reference") or transaction.provider_reference
    transaction.provider_response = paystack_result
    if data.get("status") == "success":
        transaction.status = "success"
        paid_at_str = data.get("paid_at") or data.get("paidAt")
        if paid_at_str:
            try:
                transaction.paid_at = datetime.fromisoformat(paid_at_str.replace("Z", "+00:00"))
            except Exception:
                transaction.paid_at = datetime.utcnow()
        else:
            transaction.paid_at = datetime.utcnow()
        if transaction.order_id:
            order = db.query(Order).filter_by(id=transaction.order_id).first()
            if order:
                order.status = "paid"
    else:
        transaction.status=data.get("status") or "failed"
    db.commit()
    db.refresh(transaction)
    return{
        "status": transaction.status,
        "transaction_id": transaction.id,
        "provider_refrence": transaction.provider_refrence
    }