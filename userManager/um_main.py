from user_manager import UserDB

db = UserDB("UsersDB.db")

def login():
    print(50*"*")
    print('''
        Welcome to user manager - login to continue''')
    print('''
        Unesi tražene podatke''')
    print(50*"*")
    while True:
        email = input("Unesi email: ")
        password = input("Unesi password: ")

        select_user_query = 'SELECT * FROM users WHERE email=? AND password=?'
        db.cursor.execute(select_user_query, (email, password))
        user = db.cursor.fetchone()
        if user:
            if user[3] == "admin":
                admin_menu()
            elif user[3] == "korisnik":
                user_menu(email)
        else:
            print("Neispravno korisničko ime ili lozinka.")
            continue
    
def admin_menu():
    print(50*"*")
    print("Dobrodošli u admin izbornik")
    print(50*"*")
    print("1 - Izlistaj sve korisnike\n2 - Dodaj korisnika\n3 - Promijeni korisničku rolu\n4 - Izbriši korisnika\n5 - pročitaj poruke\n6 - izlaz\n")
    print("Odaberi akciju:\n")
    action = int(input())
    if action == 1:
        db.print_all()
        print()
        admin_menu()
    elif action == 2:
        db.create_user()
        print()
        admin_menu()
    elif action == 3:
        db.edit_user()
        print()
        admin_menu()
    elif action == 4:
        db.delete_user()
        print()
        admin_menu()
    elif action == 5:
        print()
        db.read_msg()
        admin_menu()
    else:
        db.close_connection()
        exit()

def user_menu(email):
    print(50*"*")
    print("Dobrodošli u korisnički izbornik")
    print(50*"*")
    print("1 - Izlistaj sve korisnike\n2 - Pošalji adminu poruku\n3 - Izlaz")
    print("Odaberi akciju:\n")
    action = int(input())
    if action == 1:
        db.print_all()
        print()
        user_menu(email)
    elif action == 2:
        db.send_mg(email)
        print()
        user_menu(email)
    else:
        exit()
login()