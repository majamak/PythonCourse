import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import requests
import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sense_emu import SenseHat
circle = "•"
uvjet=False

row=0
col=0
col1=7

R = (255,0,0)
G = (0,255,0)
B = (0,0,255)
Y = (255,255,0)
O=(255,165,0)

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.last_record = (None, None, None, None, None, None)
        self.connect() 
        self.create_table_history()    
        
    def connect(self):
        global uvjet
        try:
            self.conn = sqlite3.connect(self.db_name)
            uvjet=True
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")

    def disconnect(self):
        global uvjet
        if self.conn:
            uvjet=False
            self.conn.close()

    def create_table_history(self):
        global uvjet
        if not self.conn:
            uvjet=False
            return

        try:
            uvjet=True
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    temp_in INTEGER,
                    temp_out INTEGER,
                    humidity_in INTEGER,
                    humidity_out INTEGER,
                    pressure_in INTEGER,
                    pressure_out INTEGER
)
            """)#polja u bazi moraju biti REAL zbog decimala, INTEGER su cijeli brojevi
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error creating 'history' table: {e}")#Ovdje cu ostaviti showerror jer moze biti neka druga, ne samo db disconnection

    def is_table_empty(self):
        global uvjet
        uvjet = True
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM history")
        self.count = cursor.fetchone()[0]
        if self.count <0:
            return False

    def insert_data(self, data):
        global uvjet
        if not self.conn:
            uvjet=False
            return

        try:
            uvjet=True
            cursor = self.conn.cursor()
            if self.is_table_empty() or self.has_values_changed(data):
                insert_sql = "INSERT INTO history (timestamp, temp_in, temp_out, humidity_in, humidity_out, pressure_in, pressure_out) VALUES (?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(insert_sql, data)
                self.conn.commit()
                self.last_record = (
                data[0],  # timestamp
                data[1],  # temp_in
                data[2],  # temp_out
                data[3],    # humidity_in
                data[4],  # humidity_out
                data[5],    # pressure_in
                data[6]   # pressure_out
            )
                return data

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error inserting data: {e}") #takoder ostavjam messagebox jer mogu biti razne greske

    def has_values_changed(self, data):
        global uvjet
        if not self.conn:
            uvjet=False
            return

        try:
            uvjet=True
            cursor = self.conn.cursor()
            select_sql = f"SELECT * FROM history ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(select_sql)
            row = cursor.fetchone()
            if row is None:
                return True
            last_record = (
            row[2],  # temp_in
            row[3],  # temp_out
            row[4],  # humidity_in
            row[5],  # humidity_out
            row[6],  # pressure_in
            row[7]   # pressure_out
        )
            if data[1] != last_record[0] or data[2] != last_record[1] or data[3] != last_record[2] or data[4] != last_record[3] or data[5] != last_record[4] or data[6] != last_record[5]:
                return True 
            return False 
        except sqlite3.Error as e:

            messagebox.showerror("Error", f"Error fetching data: {e}")

    def all_records(self, tree):
        global uvjet
        try:
            uvjet=True
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM history")
            records = cursor.fetchall()

            for item in tree.get_children():
                tree.delete(item)

            for record in records:
                timestamp = record[1]
                formatted_timestamp = timestamp[:-7]
                record = record[0], formatted_timestamp, record[2], record[3], record[4], record[5], record[6], record[7]
                tree.insert("", "end", values=record)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching data: {e}")

    def graph(self):
        global uvjet
        try:
            uvjet=True
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM history")
            records = cursor.fetchall()
            timestamps = []
            temp_in_values = []
            temp_out_values = []
            humidity_in_values = []
            humidity_out_values = []
            pressure_in_values = []
            pressure_out_values = []

            for record in records:
                timestamp = record[1]
                formatted_timestamp = timestamp[:-13]
                timestamps.append(formatted_timestamp)
                temp_in_values.append(record[2])
                temp_out_values.append(record[3])
                humidity_in_values.append(record[4])
                humidity_out_values.append(record[5])
                pressure_in_values.append(record[6])
                pressure_out_values.append(record[7])

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(timestamps, temp_in_values, label='Temperature In')
            ax.plot(timestamps, temp_out_values, label='Temperature Out')
            ax.plot(timestamps, humidity_in_values, label='Humidity In')
            ax.plot(timestamps, humidity_out_values, label='Humidity Out')
            ax.plot(timestamps, pressure_in_values, label='Pressure In')
            ax.plot(timestamps, pressure_out_values, label='Pressure Out')

            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Values')
            ax.set_title('Weather Data Over Time')
            ax.legend()

            return fig
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching data: {e}")

class SmartHomeMeteoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("650x450")
        self.root.title("Smart Home Meteo")
        self.label = tk.Label(self.root, text="Podaci o temperaturi, tlaku i vlažnosti zraka", font=('Arial', 11))
        self.label.pack()
        self.db = Database("SmartHomeMeteo.db")
        self.temp_in, self.humi_in, self.pres_in = None, None, None
        self.root.after(5000, self.refresh_data)
        global circle
        global string_var
        global uvjet
        string_var = tk.StringVar(value=circle)
        self.fig = self.db.graph()

        self.sense=SenseHat()
        self.sense.clear()

        def display_chart_window():
            chart_window = tk.Toplevel(self.root)
            chart_window.geometry("800x600")
            chart_window.title("Grafički prikaz")
            canvas = FigureCanvasTkAgg(self.fig, master=chart_window)
            canvas.get_tk_widget().pack()

        self.time_label = tk.Label(self.root, text="", font=("Arial", 11))
        self.time_label.pack(side="bottom")

        self.label_left_frame = tk.Frame(self.root)
        self.label_left_frame.pack(side="left", fill="both", expand=True, padx=50)

        self.empty_label_out = tk.Label(self.label_left_frame, text="")
        self.grad_label = tk.Label(self.label_left_frame, text="")
        self.temp_label_out = tk.Label(self.label_left_frame, text="")
        self.vlaga_label_out = tk.Label(self.label_left_frame, text="")
        self.tlak_label_out = tk.Label(self.label_left_frame, text="")
        self.vrijeme_label_out = tk.Label(self.label_left_frame, text="")

        self.empty_label_out.grid(row=0, column=0, sticky="w")
        self.grad_label.grid(row=1, column=0, sticky="w")
        self.temp_label_out.grid(row=2, column=0, sticky="w")
        self.vlaga_label_out.grid(row=3, column=0, sticky="w")
        self.tlak_label_out.grid(row=4, column=0, sticky="w")
        self.vrijeme_label_out.grid(row=5, column=0, sticky="w")

        self.label_right_frame = tk.Frame(self.root)
        self.label_right_frame.pack(side="right", fill="both", expand=True)

        self.temp_label_in = tk.Label(self.label_right_frame, text="")
        self.temp_label_in.grid(row=2, column=1, sticky="w")
        self.vlaga_label_in = tk.Label(self.label_right_frame, text="")
        self.vlaga_label_in.grid(row=3, column=1, sticky="w")
        self.tlak_label_in = tk.Label(self.label_right_frame, text="")
        self.tlak_label_in.grid(row=4, column=1, sticky="w")
        self.poruka_label_in = tk.Label(self.label_right_frame, text="")
        self.poruka_label_in.grid(row=5, column=1, sticky="w")
        self.circle_label = tk.Label(self.label_right_frame, font=('Arial', 30), text="",textvariable=string_var)
        
        if uvjet:
            self.circle_label.config(fg="green")
        else:
            self.circle_label.config(fg="red")
        self.circle_label.grid(row=0, column=1, sticky="e")
        self.poruka1_label_in = tk.Label(self.label_left_frame, text="")
        self.poruka1_label_in.grid(row=6, column=0, sticky="w")
        self.poruka2_label_in = tk.Label(self.label_left_frame, text="")
        self.poruka2_label_in.grid(row=7, column=0, sticky="w")
    
        self.label_image_frame = tk.Frame(self.root)
        self.label_image_frame.config(width=400, height=200)
        self.label_image_frame.place(x=150, y=250)

        self.history_button = tk.Button(self.root, text="Povijest", command=self.new_window)
        self.history_button.place(x=250, y=370)
        self.graph_button = tk.Button(self.root, text="Grafički prikaz", command=display_chart_window)
        self.graph_button.place(x=350, y=370)

        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S") 
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    
    def new_window(self):
        top = tk.Toplevel()
        top.title("Povijest spremljenih vrijednosti")
        top.geometry("820x230") 
        tree = ttk.Treeview(top, columns=("ID", "Timestamp", "Temp In", "Temp Out", "Humidity In", "Humidity Out", "Pressure In", "Pressure Out"))
        tree.column("#0", width=0)
        tree.heading("#1", text="ID", anchor="center")
        tree.heading("#2", text="Timestamp", anchor="center")
        tree.heading("#3", text="Temp In", anchor="center")
        tree.heading("#4", text="Temp Out", anchor="center")
        tree.heading("#5", text="Humidity In", anchor="center")
        tree.heading("#6", text="Humidity Out", anchor="center")
        tree.heading("#7", text="Pressure In", anchor="center")
        tree.heading("#8", text="Pressure Out", anchor="center")

        tree.column("#1", width=50, stretch=tk.NO, anchor="center")
        tree.column("#2", width=160, stretch=tk.NO, anchor="center")
        tree.column("#3", width=80, stretch=tk.NO, anchor="center")
        tree.column("#4", width=90, stretch=tk.NO, anchor="center")
        tree.column("#5", width=100, stretch=tk.NO, anchor="center")
        tree.column("#6", width=110, stretch=tk.NO, anchor="center")
        tree.column("#7", width=95, stretch=tk.NO, anchor="center")
        tree.column("#8", width=130, stretch=tk.NO, anchor="center")

        tree.grid(row=0, column=0, sticky="nsew")

        self.db.all_records(tree)

    def inside(self, temp_in, pres_in, humi_in):
        self.temp_in=self.sense.get_temperature()
        self.temp_in=round(self.temp_in,0)
        self.temp_label_in.config(text=f"Temperatura u stanu: {self.temp_in}°C")

        self.pres_in=self.sense.get_pressure()
        self.pres_in=round(self.pres_in,0)
        self.tlak_label_in.config(text=f"Pritisak u stanu: {self.pres_in} hPa")
        
        self.humi_in=self.sense.get_humidity()
        self.humi_in=round(self.humi_in,0)
        self.vlaga_label_in.config(text=f"Vlaga u stanu: {self.humi_in}%")

        self.poruka(self.temp_in)

    def outside(self, temp_in, pres_in, humi_in):
        url = "https://vrijeme.hr/hrvatska_n.xml"#podaci se refreshaju svakih sat vremena
        response = requests.get(url)   
        if response.status_code == 200:
                xml_content = response.text
                root = ET.fromstring(xml_content)
                grad_element = root.find(".//Grad[GradIme='Zagreb-Maksimir']")
                if grad_element is not None:
                    grad_ime_element = grad_element.find(".//GradIme")
                    temp_element_out = grad_element.find(".//Temp")
                    vlaga_element_out = grad_element.find(".//Vlaga")
                    tlak_element_out = grad_element.find(".//Tlak")
                    vrijeme_element_out = grad_element.find(".//Vrijeme")
                    
                    grad_ime = grad_ime_element.text.strip()
                    self.grad_label.config(text=f"Grad: {grad_ime}")
                    
                    temp = float(temp_element_out.text.strip())
                    self.temp_label_out.config(text=f"Temperatura: {temp}°C")
                    
                    vlaga = float(vlaga_element_out.text.strip())
                    self.vlaga_label_out.config(text=f"Vlaga: {vlaga}%")
                    
                    tlak = float(tlak_element_out.text.strip())
                    self.tlak_label_out.config(text=f"Tlak: {tlak} hPa")
                    
                    vrijeme = vrijeme_element_out.text.strip()
                    self.vrijeme_label_out.config(text=f"Vrijeme: {vrijeme}")

                    self.display_image(temp, tlak, vlaga)

                    timestamp = datetime.now()
                    data = (timestamp, temp_in, temp, humi_in, vlaga, pres_in, tlak) 
                    self.db.insert_data(data)


    def display_image(self, temp, tlak, vlaga):
        global row
        global col
        if temp >= 30:
            path = "./images/AC.png"
            row=8
            for row in range(row):
                self.sense.set_pixel(col,row,R)
        elif 22 <= temp < 30:
            path = "./images/tshirt.png"
            row=6
            for row in range(row, col, -1):
                self.sense.set_pixel(col,row+1,O)
        elif 12 <= temp < 22:
            path = "./images/jacket.png"
            row=4
            for row in range(row):
                self.sense.set_pixel(col,row+4,Y)
        elif 0 <= temp < 12:
            path = "./images/winter_jacket.png"
            row=2
            for row in range(row):
                self.sense.set_pixel(col,row+6,B)
        else:
            path = "./images/winter.png"
        
        #vanjske vrijednoti koje mogu imati utjecaj na vrijednosti u stanu
        if tlak < 1010:
            path = "./images/storm.png"
            color = "red"
            self.poruka1_label_in.config(text="Oprez. Moguće nevrijeme", fg=color)
        elif tlak >=1010 and tlak <1020:
            color = "green"
            self.poruka1_label_in.config(text="Normalan tlak zraka", fg=color)
            color = "green"
        elif tlak > 1020:
            path = "./images/heavy.png"
            color = "red"
            self.poruka1_label_in.config(text="Povišeni tlak zraka može prouzročiti\nnizak krvni tlak što može dovesti\ndo nesvjestice. Postoji mogućnost\nda ćete se osjećati slabije.", fg=color)
        else:
            pass
        if vlaga <=42:
            pass
        elif vlaga > 42:
            path = "./images/AC.png"
            color = "red"
            self.poruka2_label_in.config(text="Povišena vlažnost zraka. Pokušajte\nboraviti u klimatiziranom prostoru", fg="red")
        else:
            pass

        image = Image.open(path)
        self.tk_image = ImageTk.PhotoImage(image)
        #ovo sprecava da se slika pomice
        if hasattr(self, 'image_label'):
            self.image_label.config(image=self.tk_image)
        else:
            self.image_label = tk.Label(self.label_image_frame, image=self.tk_image)
            self.image_label.pack()

    def poruka(self, temp_in):
        global row
        global col
        global col1
        temp_in = self.temp_in 
        if temp_in >= 30:
            self.poruka_label_in.config(text="Temperatura u stanu je previsoka.\nUključite klimu", fg="red")
            row=8
            for row in range(row):
                self.sense.set_pixel(col1,row,R)
        elif 22 <= temp_in < 30:
            self.poruka_label_in.config(text="Temperatura u stanu je ugodna", fg="green")
            row=6
            for row in range(row, col, -1):
                self.sense.set_pixel(col1,row+1,O)
        elif 12 <= temp_in < 22:
            self.poruka_label_in.config(text="Temperatura u stanu je preniska. \nPojačajte grijanje ili obucite duge rukave", fg="orange")
            row=4
            for row in range(row):
                self.sense.set_pixel(col1,row+4,Y)
        elif 0 <= temp_in < 12:
            self.poruka_label_in.config(text="Temperatura u stanu je niža.\nZa veću udobnost, uključite grijanje", fg="blue")
            row=2
            for row in range(row):
                self.sense.set_pixel(col1,row+6,B)
        else:
            self.poruka_label_in.config(text="Uključite grijanje ili zovite majstora", fg="blue")

    def refresh_data(self):
        self.outside(app.temp_in, app.pres_in, app.humi_in)  
        self.inside(app.temp_in, app.pres_in, app.humi_in)   

        self.root.after(5000, self.refresh_data)

    '''
    ovo je razlog zasto se podaci konstantno mijenjaju i pohranjuju, sense emulator ima odstupanja
    https://sense-emu.readthedocs.io/en/latest/sense_emu_gui.html#usage
    The emulation does not precisely reflect the settings of the temperature,
    pressure, and humidity sliders. Random errors are introduced that scale
    according to the sensor specifications, and as the sliders are adjusted,
    the sensor value will gradually drift towards the new setting at a similar
    rate to the sensors on the real HAT.
    '''

if __name__ == "__main__":
    app = SmartHomeMeteoApp()
    app.inside(app.temp_in, app.pres_in, app.humi_in)
    app.outside(app.temp_in, app.pres_in, app.humi_in)
    app.root.mainloop()

