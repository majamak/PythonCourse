import sqlite3

class UserDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.konekcija = sqlite3.connect(db_file)
        self.cursor = self.konekcija.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    role TEXT, 
                    password TEXT 
                )
            ''')
            self.konekcija.commit()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.konekcija.commit()
        except sqlite3.Error as error:
            print(f"An error occurred: {error}")

    def close_connection(self):
        self.cursor.close()
        self.konekcija.close()

    def create_user(self):
        name = input("Unesi Ime i prezime korisnika: ")
        email = input("Unesi email korisnika: ")
        role = input("Unesi korisničku rolu (admin / korisnik): ")
        password = input("Definiraj password: ")
        insert_data = (name, email, role, password)

        self.cursor.execute("INSERT INTO users (name, email, role, password) VALUES (?,?,?,?)", insert_data)
        self.konekcija.commit()
        print("Korisnik uspješno dodan")

    
    def print_all(self):
        select_table_query = 'SELECT id, name, email, role FROM users'
        self.cursor.execute(select_table_query)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def read_msg(self):
        try:
            select_table_query = 'SELECT * FROM message'
            self.cursor.execute(select_table_query)
            rows = self.cursor.fetchall()
            for row in rows:
                print(row)
        except sqlite3.Error as error:
            print(f"Dogodila se greška {error}")

    def edit_user(self):
        email = input("Unesi email korisnika za ažuriranje: ")
        new_role = input("Unesi novu rolu (admin / korisnik): ")
        new_password = input("Unesi novi password ili potvrdi stari: ")
        update_table_query = '''
            UPDATE users
            SET role = ?,
            password = ?
            WHERE email = ?
        '''
        self.cursor.execute(update_table_query, (new_role, new_password, email))
        self.konekcija.commit()
        print("Podaci uspješno ažurirani")

    def delete_user(self):
        email = input("Unesi email korisnika za brisanje: ")

        delete_table_query = '''
            DELETE FROM users
            WHERE email = ?
        '''
        self.cursor.execute(delete_table_query, (email,))
        self.konekcija.commit()
        print("Korisnik uspješno obrisan")
    
    def send_mg(self, email):
        message = input("Unesi poruku: ")
        insert_data = (message, email)
        self.cursor.execute("INSERT INTO message (message, email) VALUES (?, ?)", insert_data)
        self.konekcija.commit()
        print(50*"*")
        print("Poruka uspješno poslana")

