import time
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pk_transactions"
)
cursor = conn.cursor()
print("WELCOME TO PK's Global Transaction")

def create_account():
    '''Create a new user account with unique pin'''
    while True:
        pin = input("Enter 4-digit pin:")
        if not pin.isdigit() or len(pin) != 4:
            print("Pin must be four")
            continue

        cursor.execute("SELECT pin FROM users WHERE pin = %s", (pin,))
        if cursor.fetchone():
            print("This PIN already exists! Choose a different one.")
            continue

        cursor.execute("INSERT INTO users (pin, balance) VALUES (%s, %s)", (pin, 0.0))
        conn.commit()
        print("Account created successfully!")
        return pin

def login():
    """Handles user login with PIN authentication."""
    attempts = 3
    while attempts > 0:
        pin = input("Enter your PIN: ")
        cursor.execute("SELECT pin FROM users WHERE pin = %s", (pin,))
        if cursor.fetchone():
            print("Login successful! Welcome to your account.")
            return pin
        else:
            attempts -= 1
            if attempts == 0:
                print("Too many incorrect attempts! \n Try again later.")
                exit()
            print(f"Incorrect PIN {attempts} attempts left.")

def get_balance(user_pin):
    """Fetches the user's balance from the database."""
    cursor.execute("SELECT balance FROM users WHERE pin = %s", (user_pin,))
    result = cursor.fetchone()
    return result[0] if result else 0.0

def deposit(user_pin):
    try:
        amount = float(input("Enter deposit amount: "))
        if amount <= 0:
            print("Invalid amount! Must be greater than 0.")
        else:
            cursor.execute("UPDATE users SET balance = balance + %s WHERE pin = %s", (amount, user_pin))
            cursor.execute("INSERT INTO transactions (pin, amount, type) VALUES (%s, %s, 'Deposit')", 
                           (user_pin, amount))
            conn.commit()
            print(f"Ksh {amount:,.2f} deposited successfully! New balance: Ksh {get_balance(user_pin):,.2f}")
    except ValueError:
        print("Invalid input! Enter a numeric value.")

def withdraw(user_pin):
    try:
        amount = float(input("Enter withdrawal amount: "))
        balance = get_balance(user_pin)
        if amount <= 0:
            print("Invalid amount!")
        elif amount > balance:
            print("Insufficient funds!")
        else:
            cursor.execute("UPDATE users SET balance = balance - %s WHERE pin = %s", (amount, user_pin))
            cursor.execute("INSERT INTO transactions (pin, amount, type) VALUES (%s, %s, 'Withdrawal')", 
                           (user_pin, -amount))
            conn.commit()
            print(f"Ksh {amount:,.2f} withdrawn successfully! New balance: Ksh {get_balance(user_pin):,.2f}")
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
            sign = "+" if type == "Deposit" else "-"
            print(f"{i}. [{timestamp}] {sign}Ksh {abs(amount):,.2f}")

def transaction_menu(user_pin):
    '''Displays the ATM menu for a logged-in user.'''
    while True:
        print("\nchoose option:")
        print("1. Check balance")
        print("2. Deposit money")
        print("3. Withdraw money")
        print("4. View transaction history ")
        print("5. Exit ")

        choice = input("Enter your choice:")

        if choice == "1":
            print(f"Your balance is Ksh:{get_balance(user_pin):,.2f}")

        elif choice =="2":
            deposit(user_pin)

        elif choice =="3":
           withdraw(user_pin)
        elif choice =="4":
           view_transactions(user_pin)

        elif choice =="5":
            print("Thanks for using PK's Global Transaction. See you soon ☺")
            time.sleep(1)
            break
        else:
            print("Invalid Enter options 1-5")
while True:
    print("\n WELCOME TO PK's Global Transaction")
    print("1.Create a New Account")
    print("2. Login to Existing Account")
    print("3. Exit")

    main_choice = input("Enter your choice: ")

    if main_choice == "1":
        new_pin = create_account()
        transaction_menu(new_pin)

    elif main_choice == "2":
        user_pin = login()
        transaction_menu(user_pin)

    elif main_choice == "3":
        print("Thanks for using PK's Global Transaction")
        cursor.close()
        conn.close()
        break

    else:
        print("Invalid Enter option 1-3.")