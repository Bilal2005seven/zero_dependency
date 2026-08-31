# main.py

# pyrefly: ignore [missing-import]
from services.user_service import UserService
# pyrefly: ignore [missing-import]
from services.payment_service import PaymentService

def main():
    print("🚀 Starting dummy app...")

    # Initialize services
    user_service = UserService()
    payment_service = PaymentService()

    # Add a sample user
    result = user_service.add_user("SampleUser", "sample@example.com")
    print("Add user result:", result)

    # List users
    users = user_service.get_users()
    print("Current users:", users)

    # Make a payment
    payment_result = payment_service.make_payment(150, "SampleUser")
    print("Payment result:", payment_result)

    # Refund a payment
    refund_result = payment_service.refund_payment(50, "SampleUser")
    print("Refund result:", refund_result)

    print("✅ Dummy workflow complete.")

if __name__ == "__main__":
    main()
