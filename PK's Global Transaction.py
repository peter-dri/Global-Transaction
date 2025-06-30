# PK's Global Transaction System
import time
import mysql.connector

# --- Database Connection ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pk_transactions"
)
cursor = conn.cursor()

print("WELCOME TO PK's Global Transaction")

# --- Exchange Rates ---
EXCHANGE_RATES = {
    ('USD', 'KES'): 130.0,
    ('KES', 'USD'): 1/130.0,
    ('EUR', 'KES'): 145.0,
    ('KES', 'EUR'): 1/145.0,
    ('GBP', 'KES'): 160.0,
    ('KES', 'GBP'): 1/160.0,
    ('USD', 'EUR'): 0.93,
    ('EUR', 'USD'): 1/0.93,
    ('USD', 'GBP'): 0.80,
    ('GBP', 'USD'): 1/0.80,
    ('EUR', 'GBP'): 0.86,
    ('GBP', 'EUR'): 1/0.86,
}

# --- Constants ---
ADMIN_PIN = "9999"

# --- Utility Functions ---
def get_raw_balance(user_pin):
    """Fetches the user's raw balance as a float."""
    cursor.execute("SELECT balance FROM users WHERE pin = %s", (user_pin,))
    result = cursor.fetchone()
    return float(result[0]) if result else 0.0

def get_formatted_balance(user_pin):
    """Fetches the user's balance and formats it nicely with currency symbol."""
    cursor.execute("SELECT balance, currency FROM users WHERE pin = %s", (user_pin,))
    result = cursor.fetchone()
    if result:
        balance, currency = result
        symbols = {"KES": "Ksh", "USD": "$", "EUR": "€", "GBP": "£"}
        return f"{symbols.get(currency, '')} {balance:,.2f}"
    return "No balance found!"

# --- Account Management ---
def create_account():
    """Create a new user account with unique pin, name, and currency."""
    while True:
        pin = input("Enter 4-digit pin: ")
        if not pin.isdigit() or len(pin) != 4:
            print("Pin must be four numbers")
            continue
        cursor.execute("SELECT pin FROM users WHERE pin = %s", (pin,))
        if cursor.fetchone():
            print("This PIN already exists! Choose a different one.")
            continue
        # Name validation: not empty, no numbers
        while True:
            name = input("Enter your full name: ").strip()
            if not name:
                print("Name cannot be empty.")
            elif any(char.isdigit() for char in name):
                print("Name cannot contain numbers.")
            else:
                break
        print("Select your currency:")
        print("1. KES (Kenya Shillings)")
        print("2. USD (US Dollar)")
        print("3. EUR (Euro)")
        print("4. GBP (British Pound)")
        currency_choice = input("Enter option (1-4): ")
        currencies = {"1": "KES", "2": "USD", "3": "EUR", "4": "GBP"}
        currency = currencies.get(currency_choice, "KES")
        security_questions = input("Set your security questions (e.g. Your pet’s name): ")
        security_answer = input("Enter your answer: ")
        cursor.execute(
            "INSERT INTO users (pin, name, balance, currency, security_questions, security_answer, status) VALUES (%s, %s, %s, %s, %s, %s, 'active')",
            (pin, name, 0.0, currency, security_questions, security_answer.lower())
        )
        conn.commit()
        print(f"✅ Account created successfully! Welcome, {name}. Your currency is {currency}.")
        return pin

def forgot_pin():
    print("\n🔐 Forgot PIN - Reset Process")
    entered_pin = input("Enter your remembered PIN (or guess): ")
    cursor.execute("SELECT security_questions, security_answer FROM users WHERE pin = %s", (entered_pin,))
    result = cursor.fetchone()
    if result:
        question, correct_answer = result
        print(f"🧠 Security Question: {question}")
        answer = input("Your Answer: ").lower()
        if answer == correct_answer:
            new_pin = input("Enter new 4-digit PIN: ")
            if len(new_pin) == 4 and new_pin.isdigit():
                cursor.execute("UPDATE users SET pin = %s WHERE pin = %s", (new_pin, entered_pin))
                conn.commit()
                print("✅ PIN reset successfully!")
            else:
                print("❌ New PIN must be exactly 4 digits.")
        else:
            print("❌ Incorrect answer. Try again.")
    else:
        print("❌ No user found or PIN guess is wrong.")

def login():
    """Handles user login with PIN authentication and forgot PIN option. Prompts for security question or name if missing."""
    attempts = 3
    while attempts > 0:
        pin = input("Enter your PIN (or type 'f' for Forgot PIN): ").strip()
        if pin.lower() in ("f", "forgot"):
            forgot_pin()
            attempts = 3
            continue
        cursor.execute("SELECT pin FROM users WHERE pin = %s", (pin,))
        if cursor.fetchone():
            # Check if security question/answer or name is missing/invalid
            cursor.execute("SELECT security_questions, security_answer, name FROM users WHERE pin = %s", (pin,))
            sq, sa, name = cursor.fetchone()
            # Name validation for older users
            while not name or name.strip() == "" or any(char.isdigit() for char in name):
                print("\nYour account does not have a valid name set.")
                new_name = input("Please enter your full name (no numbers): ").strip()
                if not new_name:
                    print("Name cannot be empty.")
                    continue
                if any(char.isdigit() for char in new_name):
                    print("Name cannot contain numbers.")
                    continue
                cursor.execute("UPDATE users SET name = %s WHERE pin = %s", (new_name, pin))
                conn.commit()
                name = new_name
                print("Name set successfully!\n")
            if not sq or not sa:
                print("\nYour account does not have a security question set.")
                new_sq = input("Set your security question (e.g. Your pet’s name): ")
                new_sa = input("Enter your answer: ")
                cursor.execute("UPDATE users SET security_questions = %s, security_answer = %s WHERE pin = %s", (new_sq, new_sa.lower(), pin))
                conn.commit()
                print("Security question set successfully!\n")
            print("Login successful! Welcome to your account.")
            return pin
        else:
            attempts -= 1
            if attempts == 0:
                print("Too many incorrect attempts! \nTry again later.")
                exit()
            print(f"Incorrect PIN. {attempts} attempts left.")

# --- Admin Functions ---
def admin_login():
    pin = input("Enter Admin PIN: ")
    if pin == ADMIN_PIN:
        print("Admin login successful! 🧠💼")
        admin_menu()
    else:
        print("Wrong Admin PIN! 🚫")

def view_all_users():
    cursor.execute("SELECT pin, balance, currency, status FROM users")
    users = cursor.fetchall()
    print("\n--- All Users ---")
    for user in users:
        pin, balance, currency, status = user
        print(f"PIN: {pin}, Balance: {balance:,.2f} {currency}, Status: {status}")

def search_user():
    pin = input("Enter PIN to search: ")
    cursor.execute("SELECT pin, balance, currency, status FROM users WHERE pin = %s", (pin,))
    user = cursor.fetchone()
    if user:
        pin, balance, currency, status = user
        print(f"User Found: PIN: {pin}, Balance: {balance:,.2f} {currency}, Status: {status}")
    else:
        print("User not found.")

def view_user_transactions():
    pin = input("Enter user PIN: ")
    cursor.execute("SELECT timestamp, amount, type FROM transactions WHERE pin = %s", (pin,))
    transactions = cursor.fetchall()
    if not transactions:
        print("No transactions found for this user.")
    else:
        print(f"\n--- Transactions for {pin} ---")
        for i, (timestamp, amount, type) in enumerate(transactions, start=1):
            sign = "+" if amount >= 0 else "-"
            print(f"{i}. [{timestamp}] {sign}{abs(amount):,.2f} ({type})")

def reset_user_pin():
    pin = input("Enter user PIN to reset: ")
    new_pin = input("Enter new PIN: ")
    if len(new_pin) == 4 and new_pin.isdigit():
        cursor.execute("UPDATE users SET pin = %s WHERE pin = %s", (new_pin, pin))
        conn.commit()
        print(f"PIN for {pin} reset successfully!")
    else:
        print("New PIN must be 4 digits!")

def delete_user():
    pin = input("Enter PIN to delete: ")
    confirm = input(f"Are you sure you want to DELETE user {pin}? (yes/no): ")
    if confirm.lower() == "yes":
        cursor.execute("DELETE FROM users WHERE pin = %s", (pin,))
        cursor.execute("DELETE FROM transactions WHERE pin = %s", (pin,))
        conn.commit()
        print(f"User {pin} deleted successfully.")
    else:
        print("Deletion canceled.")

def add_new_user():
    pin = input("Enter new user's PIN: ")
    balance = float(input("Enter initial balance: "))
    print("Select currency:")
    print("1. KES")
    print("2. USD")
    print("3. EUR")
    print("4. GBP")
    choice = input("Choice: ")
    currencies = {"1": "KES", "2": "USD", "3": "EUR", "4": "GBP"}
    currency = currencies.get(choice, "KES")
    cursor.execute("INSERT INTO users (pin, balance, currency, status) VALUES (%s, %s, %s, 'active')", (pin, balance, currency))
    conn.commit()
    print("New user added successfully!")

def freeze_unfreeze_user():
    pin = input("Enter PIN to freeze/unfreeze: ")
    cursor.execute("SELECT status FROM users WHERE pin = %s", (pin,))
    user = cursor.fetchone()
    if not user:
        print("User not found.")
        return
    status = user[0]
    new_status = "frozen" if status == "active" else "active"
    cursor.execute("UPDATE users SET status = %s WHERE pin = %s", (new_status, pin))
    conn.commit()
    print(f"User {pin} status changed to {new_status}.")

def view_system_stats():
    cursor.execute("SELECT COUNT(*), SUM(balance) FROM users")
    count, total_balance = cursor.fetchone()
    print(f"\n--- System Stats ---")
    print(f"Total Users: {count}")
    print(f"Total Money in System: {total_balance:,.2f}")

def view_login_logs():
    cursor.execute("SELECT pin_attempted, success, timestamp FROM login_logs ORDER BY id DESC")
    logs = cursor.fetchall()
    print("\n--- Login Logs ---")
    if not logs:
        print("No login attempts logged yet.")
    else:
        for i, (pin_attempted, success, timestamp) in enumerate(logs, start=1):
            status = "✅ SUCCESS" if success else "❌ FAIL"
            print(f"{i}. [{timestamp}] PIN: {pin_attempted} ({status})")

def admin_menu():
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. View all users")
        print("2. Search user by PIN")
        print("3. View user's transactions")
        print("4. Reset user's PIN")
        print("5. Delete user")
        print("6. Add new user")
        print("7. Freeze/Unfreeze user account")
        print("8. View system stats")
        print("9. View login logs")
        print("10. Exit Admin Mode")
        choice = input("Choice: ")
        if choice == "1":
            view_all_users()
        elif choice == "2":
            search_user()
        elif choice == "3":
            view_user_transactions()
        elif choice == "4":
            reset_user_pin()
        elif choice == "5":
            delete_user()
        elif choice == "6":
            add_new_user()
        elif choice == "7":
            freeze_unfreeze_user()
        elif choice == "8":
            view_system_stats()
        elif choice == "9":
            view_login_logs()
        elif choice == "10":
            print("Exiting Admin Mode 🚪✨")
            break
        else:
            print("Invalid choice. Try again!")

# --- User Transaction Functions ---
def deposit(user_pin):
    try:
        amount = float(input("Enter deposit amount: "))
        if amount <= 0:
            print("Invalid amount! Must be greater than 0.")
        else:
            cursor.execute("UPDATE users SET balance = balance + %s WHERE pin = %s", (amount, user_pin))
            cursor.execute("INSERT INTO transactions (pin, amount, type) VALUES (%s, %s, 'Deposit')", (user_pin, amount))
            conn.commit()
            print(f"Ksh {amount:,.2f} deposited successfully! New balance: Ksh {get_raw_balance(user_pin):,.2f}")
    except ValueError:
        print("Invalid input! Enter a numeric value.")

def withdraw(user_pin):
    try:
        amount = float(input("Enter withdrawal amount: "))
        balance = get_raw_balance(user_pin)
        if amount <= 0:
            print("Invalid amount!")
        elif amount > balance:
            print("Insufficient funds!")
        else:
            cursor.execute("UPDATE users SET balance = balance - %s WHERE pin = %s", (amount, user_pin))
            cursor.execute("INSERT INTO transactions (pin, amount, type) VALUES (%s, %s, 'Withdrawal')", (user_pin, -amount))
            conn.commit()
            print(f"Ksh {amount:,.2f} withdrawn successfully! New balance: Ksh {get_raw_balance(user_pin):,.2f}")
    except ValueError:
        print("Invalid input! Enter a numeric value.")

def view_transactions(user_pin):
    cursor.execute("SELECT timestamp, amount, type FROM transactions WHERE pin = %s ORDER BY id DESC", (user_pin,))
    transactions = cursor.fetchall()
    print("\nTransaction History:")
    if not transactions:
        print("No transactions yet!")
    else:
        for i, (timestamp, amount, type) in enumerate(transactions, start=1):
            sign = "+" if type in ("Deposit", "Received") else "-"
            print(f"{i}. [{timestamp}] {sign}Ksh {abs(amount):,.2f} ({type})")

def change_account_details(user_pin):
    print("\nWhat would you like to change?")
    print("1. Change PIN")
    print("2. Change Currency")
    print("3. Cancel")
    choice = input("Enter your choice: ")
    if choice == "1":
        old_pin = input("Enter your current 4-digit PIN: ")
        if old_pin != user_pin:
            print("Incorrect PIN! Unable to change.")
            return
        new_pin = input("Enter your new 4-digit PIN: ")
        if len(new_pin) != 4 or not new_pin.isdigit():
            print("Invalid PIN. Must be 4 digits.")
            return
        cursor.execute("UPDATE users SET pin = %s WHERE pin = %s", (new_pin, user_pin))
        conn.commit()
        print("PIN updated successfully!")
    elif choice == "2":
        print("Select your new currency:")
        print("1. KES (Kenya Shillings)")
        print("2. USD (US Dollar)")
        print("3. EUR (Euro)")
        print("4. GBP (British Pound)")
        currency_choice = input("Enter option (1-4): ")
        currencies = {"1": "KES", "2": "USD", "3": "EUR", "4": "GBP"}
        new_currency = currencies.get(currency_choice)
        if new_currency:
            cursor.execute("UPDATE users SET currency = %s WHERE pin = %s", (new_currency, user_pin))
            conn.commit()
            print(f"Currency updated to {new_currency}!")
        else:
            print("Invalid choice, no changes made.")
    elif choice == "3":
        print("Account details update cancelled.")
    else:
        print("Invalid choice.")

def send_money(user_pin):
    try:
        receiver_pin = input("Enter receiver's PIN: ")
        if receiver_pin == user_pin:
            print("You can't send money to yourself!")
            return
        cursor.execute("SELECT pin FROM users WHERE pin = %s", (receiver_pin,))
        if not cursor.fetchone():
            print("Receiver account not found!")
            return
        amount = float(input("Enter amount to send: "))
        balance = get_raw_balance(user_pin)
        if amount <= 0:
            print("Invalid amount! Must be greater than 0.")
        elif amount > balance:
            print("Insufficient funds!")
        else:
            fee = amount * 0.02
            total_deducted = amount + fee
            cursor.execute("UPDATE users SET balance = balance - %s WHERE pin = %s", (total_deducted, user_pin))
            cursor.execute("UPDATE users SET balance = balance + %s WHERE pin = %s", (amount, receiver_pin))
            cursor.execute("INSERT INTO transactions (pin, amount, type) VALUES (%s, %s, 'Sent')", (user_pin, -total_deducted))
            cursor.execute("INSERT INTO transactions (pin, amount, type) VALUES (%s, %s, 'Received')", (receiver_pin, amount))
            conn.commit()
            print(f"Ksh {amount:,.2f} sent successfully to {receiver_pin} with a fee of Ksh {fee:,.2f}!")
            print(f"New balance: Ksh {get_raw_balance(user_pin):,.2f}")
    except ValueError:
        print("Invalid input! Enter a numeric value.")

def show_users():
    cursor.execute("SELECT pin, currency FROM users")
    users = cursor.fetchall()
    print("\n--- All Users ---")
    if not users:
        print("No users found!")
    else:
        for user in users:
            pin, currency = user
            print(f"PIN: {pin}, Currency: {currency}")

def view_profile(user_pin):
    cursor.execute("SELECT name, pin, currency FROM users WHERE pin = %s", (user_pin,))
    result = cursor.fetchone()
    if result:
        name, pin, currency = result
        print(f"\n--- User Profile ---\nName: {name}\nPIN: {pin}\nCurrency: {currency}")
    else:
        print("Profile not found.")

def transaction_menu(user_pin):
    while True:
        print("\nchoose option:")
        print("1. Check balance")
        print("2. Deposit money")
        print("3. Withdraw money")
        print("4. View transaction history")
        print("5. Send money to another user")
        print("6. Change account details")
        print("7. View profile")
        print("8. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            print(get_formatted_balance(user_pin))
        elif choice == "2":
            deposit(user_pin)
        elif choice == "3":
            withdraw(user_pin)
        elif choice == "4":
            view_transactions(user_pin)
        elif choice == "5":
            send_money(user_pin)
        elif choice == "6":
            change_account_details(user_pin)
        elif choice == "7":
            view_profile(user_pin)
        elif choice == "8":
            print("Thanks for using PK's Global Transaction. See you soon ☺")
            time.sleep(1)
            break
        else:
            print("Invalid. Enter options 1-8.")

# --- Main Program Loop ---
def main():
    while True:
        print("1. Create a New Account")
        print("2. Login to Existing Account")
        print("3. Admin Login")
        print("4. Forgot PIN?")
        print("5. Exit")
        main_choice = input("Enter your choice: ")
        if main_choice == "1":
            new_pin = create_account()
            transaction_menu(new_pin)
        elif main_choice == "2":
            user_pin = login()
            transaction_menu(user_pin)
        elif main_choice == "3":
            admin_login()
        elif main_choice == "4":
            forgot_pin()
        elif main_choice == "5":
            print("Thanks for using PK's Global Transaction. Goodbye 👋🏽")
            cursor.close()
            conn.close()
            break
        else:
            print("Invalid. Enter options 1-5.")

if __name__ == "__main__":
    main()
