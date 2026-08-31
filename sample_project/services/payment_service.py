# payment_services.py

class PaymentService:
    def __init__(self):
        # pretend we have a balance
        self.balance = 1000  

    def make_payment(self, amount, user_id):
        if amount <= 0:
            return {"status": "failed", "reason": "Invalid amount"}
        if amount > self.balance:
            return {"status": "failed", "reason": "Insufficient funds"}
        
        # simulate deduction
        self.balance -= amount
        return {
            "status": "success",
            "user_id": user_id,
            "amount": amount,
            "remaining_balance": self.balance
        }

    def refund_payment(self, amount, user_id):
        if amount <= 0:
            return {"status": "failed", "reason": "Invalid refund amount"}
        
        # simulate refund
        self.balance += amount
        return {
            "status": "success",
            "user_id": user_id,
            "amount_refunded": amount,
            "new_balance": self.balance
        }


# Example usage
if __name__ == "__main__":
    service = PaymentService()

    print(service.make_payment(200, "user123"))
    print(service.refund_payment(50, "user123"))
    print(service.make_payment(2000, "user456"))  # should fail
