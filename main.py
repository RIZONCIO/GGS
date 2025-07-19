import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import assets.password_generator as password_generator


def main():
    window = tk.Tk()
    window.title("Gerador de Senhas")
    window.geometry("650x650")

    password_generator.setup_ui(window)

    window.mainloop()


if __name__ == "__main__":
    main()
