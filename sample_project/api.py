# api.py

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from services.user_service import UserService
# pyrefly: ignore [missing-import]
from services.payment_service import PaymentService

app = FastAPI()
user_service = UserService()
payment_service = PaymentService()

@app.get("/")
def root():
    return {"message": "Dummy API is running!"}

@app.post("/users/")
def create_user(name: str, email: str):
    result = user_service.add_user(name, email)
    return result

@app.get("/users/")
def list_users():
    users = user_service.get_users()
    return {"users": users}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    result = user_service.delete_user(user_id)
    return result

@app.post("/payments/")
def make_payment(amount: float, user_id: str):
    result = payment_service.make_payment(amount, user_id)
    return result

@app.post("/refunds/")
def refund_payment(amount: float, user_id: str):
    result = payment_service.refund_payment(amount, user_id)
    return result
