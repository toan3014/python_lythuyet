import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        operation = operator.get()
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 == 0:
                raise ZeroDivisionError
            result = num1 / num2
        else:
            raise ValueError("Phép toán không hợp lệ!")
        result_label.config(text=f"Kết quả: {result}")
    except ZeroDivisionError:
        messagebox.showerror("Lỗi", "Không thể chia cho 0!")
    except ValueError as e:
        messagebox.showerror("Lỗi", f"Lỗi nhập liệu: {e}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

# Tạo giao diện chính
window = tk.Tk()
window.title("Máy Tính Đơn Giản")

# Nhập số thứ nhất
tk.Label(window, text="Số thứ nhất:").grid(row=0, column=0, padx=5, pady=5)
entry1 = tk.Entry(window)
entry1.grid(row=0, column=1, padx=5, pady=5)

# Nhập số thứ hai
tk.Label(window, text="Số thứ hai:").grid(row=1, column=0, padx=5, pady=5)
entry2 = tk.Entry(window)
entry2.grid(row=1, column=1, padx=5, pady=5)

# Chọn phép toán
tk.Label(window, text="Phép toán:").grid(row=2, column=0, padx=5, pady=5)
operator = tk.StringVar(value="+")
tk.OptionMenu(window, operator, "+", "-", "*", "/").grid(row=2, column=1, padx=5, pady=5)

# Nút tính toán
tk.Button(window, text="Tính toán", command=calculate).grid(row=3, column=0, columnspan=2, pady=10)

# Hiển thị kết quả
result_label = tk.Label(window, text="Kết quả:")
result_label.grid(row=4, column=0, columnspan=2, pady=10)

# Chạy chương trình
window.mainloop()
