import time
print("WELCOME TO PK's Global Transaction")
users = {}

def create_account():
    '''Create a new user account with unique pin'''
    while True:
        pin = input("Enter 4-digit pin:")
        if not pin.isdigit() or len(pin) != 4:
            print("Pin must be four")
            continue
        users[pin] = {"balance": 0.0, "transactions": []}
        print(f"Account Created successfully")
        return pin

def login():
    """Handles user login with PIN authentication."""
    attempts = 3
    while attempts > 0:
        pin = input("Enter your PIN: ")
        if pin in users:
            print("Login successful! Welcome to your account.")
            return pin
        else:
            attempts -= 1
            if attempts == 0:
                print("Too many incorrect attempts! \n Try again later.")
                exit()
            print(f"Incorrect PIN {attempts} attempts left.")

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
            print(f"Your balance is Ksh:{users[user_pin]['balance'}")
        elif choice =="2":
            amount = float(input("Enter deposit amount:"))
            if amount<=0:
                print("Invalid amount. Deposit amount greater than 0")
            else:
                users[user_pin]["balance"] += amount
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                transaction_history.append(f"[{timestamp}]+ Ksh {amount:,.2f}")
                print(f"Ksh{amount:,.2f} deposited successfully New balance: Ksh{balance:,.2f}")

        elif choice =="3":
            amount = float(input("Enter amount to withdraw:"))
            if amount<=0:
                print("Invalid amount")
            elif amount > users[user_pin]["balance"]:
                print("Insufficient funds in the account!")
            else:
                users[user_pin]["balance"] -=amount
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                transaction_history.append(f"[{timestamp}]- Ksh{amount:,.2f}")
                print(f"Ksh{amount} Withdrawn successfully New balance:Ksh{balance:,.2f}")

        elif choice =="4":
            print("\n Transaction history ")
            if not transaction_history:
                print("No Transaction yet")
            else:
                for i, transaction in enumerate(transaction_history, start=1):
                    print(f"{i}.{transaction}")

        elif choice =="5":
            print("Thanks for using PK's Global Transaction. See you soon ☺")
            time.sleep(1)
        else:
            print("Invalid choice! Enter options 1-5")
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
        if not users:
            print("No accounts exist yet! Please create an account first.")
            continue
        user_pin = login()
        transaction_menu(user_pin)

    elif main_choice == "3":
        print("Thanks for using PK's Global Transaction")
        break

    else:
        print("Invalid choice! Please enter 1, 2, or 3.")