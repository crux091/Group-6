sessions = {}

def add_session():
    date = input("Enter the date of the month (MM-DD): ")
    time = input("Enter the time of the day (e.g. 5:30 - 6:00): ")

    if date not in sessions:
        sessions[date] = [time]
        print(f"Session scheduled on {date} from {time}.")
    else:
        if time in sessions[date]:
            print(f"The time slot {time} is already taken on {date}.")
        else:
            sessions[date].append(time)
            print(f"Session scheduled on {date} from {time}.")

def check_session():
    date = input("Enter the date to check (MM-DD): ")
    if date in sessions:
        print(f"Sessions scheduled on {date}:")
        for time in sessions[date]:
            print(f"- {time}")
    else:
        print(f"No sessions are scheduled on {date}.")

def menu():
    while True:
        print("\n--- Gym Session Scheduler ---")
        print("1. Add a new session")
        print("2. Check if a session is scheduled")
        print("3. Exit")

        choice = input("Choose an option (1-3): ")

        if choice == "1":
            add_session()
        elif choice == "2":
            check_session()
        elif choice == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please choose a valid option (1-3).")

# Start the menu-driven program
menu()
