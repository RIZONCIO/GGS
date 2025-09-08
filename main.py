import tkinter as tk
import ttkbootstrap as ttkb
from ui.main_window import MainWindow
from utils.caminhos import get_pasta_cofre


def main():
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Erro", f"Erro ao iniciar FortiCore Sentinel:\n{e}")
        root.destroy()


if __name__ == "__main__":
    main()
