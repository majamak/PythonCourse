import random
import tkinter as tk

def joker():
    joker_nr = random.randint(100000, 999999)
    joker_label = tk.Label(window, text="Joker broj: " + str(joker_nr))
    joker_label.pack()


numbers_5_50 = []
numbers_2_12 = []

def choose_number_5_50(number):
    if number not in numbers_5_50:
        numbers_5_50.append(number)
        button = number_buttons_5_50[number - 1]
        button.config(bg="green")  

def choose_number_2_12(number):
    if number not in numbers_2_12:
        numbers_2_12.append(number)
        button = number_buttons_2_12[number - 1]
        button.config(bg="green")  

def clear_selection():
    for number in numbers_5_50:
        button = number_buttons_5_50[number - 1]
        button.config(bg="SystemButtonFace")
    numbers_5_50.clear()
    
    for number in numbers_2_12:
        button = number_buttons_2_12[number - 1]
        button.config(bg="SystemButtonFace")
    numbers_2_12.clear()

def submit_selection():

    if len(numbers_5_50) == 5 and len(numbers_2_12) == 2:
        label_result.config(text="Odabrani loto brojevi (5/50): " + str(numbers_5_50) + "\nDodatni brojevi  (2/12): " + str(numbers_2_12))
    else:
        label_result.config(text="Molimo označite minimalno 5 brojeva i dva dodatna.")

window = tk.Tk()
window.title("Eurojackpot")
window.geometry("700x600")
label=tk.Label(window, text="Eurojackpot igra", font=("Segoe UI",16))
label.pack()

frame_5_50 = tk.Frame(window)
frame_5_50.pack()
label=tk.Label(window, text="Dodatni brojevi", font=("Segoe UI",12))
label.pack()
frame_2_12 = tk.Frame(window)
frame_2_12.pack()

number_buttons_5_50 = []
number_buttons_2_12 = []

for i in range(1, 51):
    button = tk.Button(frame_5_50, text=str(i), width=4, command=lambda num=i: choose_number_5_50(num))
    button.grid(row=(i - 1) // 10, column=(i - 1) % 10, padx=5, pady=5)
    number_buttons_5_50.append(button)

for i in range(1, 13):
    button = tk.Button(frame_2_12, text=str(i), width=4, command=lambda num=i: choose_number_2_12(num))
    button.grid(row=(i - 1) // 6, column=(i - 1) % 6, padx=5, pady=5)
    number_buttons_2_12.append(button)

clear_button = tk.Button(window, text="Obriši sve", command=clear_selection)
clear_button.pack(pady=10)

joker_button = tk.Button(window, text="Želim joker broj", command=joker)
joker_button.pack(pady=10)

submit_button = tk.Button(window, text="Uplati odabrane brojeve", command=submit_selection)
submit_button.pack(pady=10)

label_result = tk.Label(window, text="")
label_result.pack()

window.mainloop()
