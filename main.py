import sqlite3
import os
import getpass

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Database connection
conn = sqlite3.connect('vehicle_rental.db')
cursor = conn.cursor()

# Create tables if they don't exist
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        owner_id INTEGER,
                        vehicle_name TEXT,
                        vehicle_type TEXT,
                        availability TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id INTEGER,
                        vehicle_id INTEGER,
                        status TEXT)''')

    # Admin user (default)
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    conn.commit()

# User Registration
def register():
    clear_console()
    print("=== User Registration ===")
    
    while True:
        username = input("Enter a unique username: ")
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            print("Username already taken. Try another.")
        else:
            break

    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match! Please try again.")
        return

    print("Select Role:")
    print("1. Customer")
    print("2. Vehicle Owner")
    role_choice = input("Enter the number corresponding to your role: ")

    role = 'customer' if role_choice == '1' else 'owner'

    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

    print(f"User '{username}' registered successfully as {role}!")

# Authentication
def login():
    clear_console()
    print("=== Login ===")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    
    if user:
        print('login successful!')
        return user
    else:
        print("Invalid credentials!")
        return None

# Admin Functions
def admin_menu():
    while True:
        clear_console()
        print("=== Admin Menu ===")
        print("1. Add Vehicle")
        print("2. View All Vehicles")
        print("3. Logout")

        choice = input("Choose an option: ")
        
        if choice == "1":
            add_vehicle()
        elif choice == "2":
            view_vehicles()
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

def add_vehicle():
    clear_console()
    print("=== Add Vehicle ===")
    owner_id = int(input("Enter Owner ID: "))
    vehicle_name = input("Enter Vehicle Name: ")
    vehicle_type = input("Enter Vehicle Type: ")
    cursor.execute("INSERT INTO vehicles (owner_id, vehicle_name, vehicle_type, availability) VALUES (?, ?, ?, 'available')", 
                   (owner_id, vehicle_name, vehicle_type))
    conn.commit()
    print(f"Vehicle '{vehicle_name}' added successfully!")

def view_vehicles():
    clear_console()
    print("=== All Vehicles ===")
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    for vehicle in vehicles:
        print(f"ID: {vehicle[0]}, Owner ID: {vehicle[1]}, Name: {vehicle[2]}, Type: {vehicle[3]}, Availability: {vehicle[4]}")
    input("\nPress Enter to go back...")

# Customer Functions
def customer_menu(user_id):
    while True:
        clear_console()
        print("=== Customer Menu ===")
        print("1. View Available Vehicles")
        print("2. Book Vehicle")
        print("3. View My Bookings")
        print("4. Logout")

        choice = input("Choose an option: ")
        
        if choice == "1":
            view_available_vehicles()
        elif choice == "2":
            book_vehicle(user_id)
        elif choice == "3":
            view_my_bookings(user_id)
        elif choice == "4":
            break
        else:
            print("Invalid choice!")

def view_available_vehicles():
    clear_console()
    print("=== Available Vehicles ===")
    cursor.execute("SELECT * FROM vehicles WHERE availability='available'")
    vehicles = cursor.fetchall()
    for vehicle in vehicles:
        print(f"ID: {vehicle[0]}, Name: {vehicle[2]}, Type: {vehicle[3]}")
    input("\nPress Enter to go back...")

def book_vehicle(user_id):
    clear_console()
    print("=== Book Vehicle ===")
    vehicle_id = int(input("Enter Vehicle ID to book: "))
    cursor.execute("SELECT availability FROM vehicles WHERE id=?", (vehicle_id,))
    vehicle = cursor.fetchone()

    if vehicle and vehicle[0] == 'available':
        cursor.execute("INSERT INTO bookings (customer_id, vehicle_id, status) VALUES (?, ?, 'booked')", (user_id, vehicle_id))
        cursor.execute("UPDATE vehicles SET availability='booked' WHERE id=?", (vehicle_id,))
        conn.commit()
        print(f"Vehicle {vehicle_id} booked successfully!")
    else:
        print("Vehicle is not available!")

def view_my_bookings(user_id):
    clear_console()
    print("=== My Bookings ===")
    cursor.execute("SELECT b.id, v.vehicle_name, b.status FROM bookings b JOIN vehicles v ON b.vehicle_id = v.id WHERE b.customer_id=?", (user_id,))
    bookings = cursor.fetchall()
    for booking in bookings:
        print(f"Booking ID: {booking[0]}, Vehicle: {booking[1]}, Status: {booking[2]}")
    input("\nPress Enter to go back...")

# Vehicle Owner Functions
def owner_menu(user_id):
    while True:
        clear_console()
        print("=== Owner Menu ===")
        print("1. View My Vehicles")
        print("2. Logout")

        choice = input("Choose an option: ")
        
        if choice == "1":
            view_my_vehicles(user_id)
        elif choice == "2":
            break
        else:
            print("Invalid choice!")

def view_my_vehicles(owner_id):
    clear_console()
    print("=== My Vehicles ===")
    cursor.execute("SELECT * FROM vehicles WHERE owner_id=?", (owner_id,))
    vehicles = cursor.fetchall()
    for vehicle in vehicles:
        print(f"ID: {vehicle[0]}, Name: {vehicle[2]}, Type: {vehicle[3]}, Availability: {vehicle[4]}")
    input("\nPress Enter to go back...")

# Main Program
def main():
    create_tables()
    
    while True:
        clear_console()
        print("=== Vehicle Rental System ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            user = login()
            if user:
                user_id, username, password, role = user
                if role == 'admin':
                    admin_menu()
                elif role == 'customer':
                    customer_menu(user_id)
                elif role == 'owner':
                    owner_menu(user_id)
        elif choice == "2":
            register()
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

if __name__ == '__main__':
    main()
