# user_service.py

import sqlite3

DB_NAME = "dummy.db"

class UserService:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def add_user(self, name, email):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            return {"status": "success", "name": name, "email": email}
        except sqlite3.IntegrityError:
            return {"status": "failed", "reason": "Email already exists"}
        finally:
            conn.close()

    def get_users(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_user(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        if deleted:
            return {"status": "success", "deleted_id": user_id}
        else:
            return {"status": "failed", "reason": "User not found"}


# Example usage
if __name__ == "__main__":
    service = UserService()

    print(service.add_user("David", "david@example.com"))
    print(service.get_users())
    print(service.delete_user(1))  # try deleting user with id=1
