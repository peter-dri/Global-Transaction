import time
print("WELCOME TO PK's Global Transaction")
balance=1000.0
pin="2222"
transaction_history = []
attempts = 3

while attempts >0:
    user_pin = input("Enter your Pin:")
    if user_pin == pin:
        print("Login successful in your account")
        break
    else:
        attempts -=1
        if attempts ==0:
            print("Too many attempts! Account locked")
            exit()
        print(f"Incorrect pin {attempts} attempts left")

while True:
    print("\nchoose option:")
    print("1. Check balance")
    print("2. Deposit money")
    print("3. Withdraw money")
    print("4. View transaction history ")
    print("5. Exit")

    choice = input("Enter your choice:")

    if choice == "1":
        print(f"Your balance is Ksh:{balance:,.2f}")
    elif choice =="2":
        amount = float(input("Enter deposit amount:"))
        if amount<=0:
            print("Invalid amount. Deposit amount greater than 0")
        else:
            balance += amount
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            transaction_history.append(f"[{timestamp}]+ Ksh {amount:,.2f}")
            print(f"Ksh{amount:,.2f} deposited successfully New balance: Ksh{balance:,.2f}")

    elif choice =="3":
        amount = float(input("Enter amount to withdraw:"))
        if amount<=0:
            print("Invalid amount")
        elif amount > balance:
            print("Insufficient funds in the account!")
        else:
            balance -=amount
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
        print("Thanks for using PK's Global Transaction. See you soon")
        time.sleep(1)
        break
    else:
        print("Invalid choice! Enter options 1-5")