import tkinter as tk
from tkinter import ttk, messagebox, Menu, Toplevel
from tkcalendar import Calendar
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(   
            dbname="postgres",
            user="postgres",
            password="toan3014",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Bán Hàng Thiết Bị Máy In")
        self.root.geometry("400x300")
        icon = None
        self.root.iconbitmap("icon.ico")
        if icon:
            self.root.iconphoto(True, icon)

        self.current_employee_id = None
        self.create_login_widgets()

    def create_login_widgets(self):
        self.root.configure(bg="#97FFFF")

        title_label = tk.Label(self.root, text="Đăng Nhập", font=("Arial", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)
        tk.Label(self.root, text="Tài Khoản:", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
        self.username_entry = tk.Entry(self.root, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Mật Khẩu:", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
        self.password_entry = tk.Entry(self.root, show='*', font=("Arial", 12), width=30)
        self.password_entry.pack(pady=5)

        login_button = tk.Button(self.root, text="Đăng Nhập", command=self.authenticate, 
                             font=("Arial", 12), bg="#4CAF50", fg="white")
        login_button.pack(pady=20)
        login_button.bind("<Enter>", lambda e: login_button.config(bg="#45a049"))
        login_button.bind("<Leave>", lambda e: login_button.config(bg="#4CAF50"))
        self.username_entry.bind("<Return>", lambda event: self.authenticate())
        self.password_entry.bind("<Return>", lambda event: self.authenticate())

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM employees WHERE username = %s AND password = %s", (username, password))
            employee = cur.fetchone()
            
            if employee:
                self.current_employee_id = employee[0]
                messagebox.showinfo("Thông Báo", "Đăng nhập thành công!")
                self.root.destroy()
                self.create_main_interface()
            else:
                messagebox.showerror("Thông báo", "Sai tài khoản hoặc mật khẩu.")
            cur.close()
            conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")

    def create_main_interface(self):
        self.root = tk.Tk()
        self.root.title("Quản Lý Bán Hàng Thiết Bị Máy In")
        self.root.geometry("800x600")  # Điều chỉnh kích thước cửa sổ chính

        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        inventory_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Kho Hàng", menu=inventory_menu)
        inventory_menu.add_command(label="Thêm Thiết Bị", command=self.add_device)
        inventory_menu.add_command(label="Xuất Hàng", command=self.export_product)
        inventory_menu.add_separator()
        inventory_menu.add_command(label="Đăng Xuất", command=self.logout)
        
        # Bạn có thể thêm các menu khác nếu cần

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Danh Sách Máy In", font=("Arial", 16 ),background="#CD853F")
        self.label.pack(pady=20)

        # Tạo Treeview để hiển thị danh sách sản phẩm
        self.product_tree = ttk.Treeview(self.root)
        self.product_tree["columns"] = ("id", "name", "model", "serial_number", "price", "stock", "entry_date")
        self.product_tree.column("#0", width=0, stretch=tk.NO)
        self.product_tree.column("id", anchor=tk.CENTER, width=50)
        self.product_tree.column("name", anchor=tk.W, width=150)
        self.product_tree.column("model", anchor=tk.W, width=100)
        self.product_tree.column("serial_number", anchor=tk.W, width=100)
        self.product_tree.column("price", anchor=tk.E, width=100)
        self.product_tree.column("stock", anchor=tk.CENTER, width=80)
        self.product_tree.column("entry_date", anchor=tk.CENTER, width=100)

        self.product_tree.heading("#0", text="", anchor=tk.W)
        self.product_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.product_tree.heading("name", text="Tên", anchor=tk.W)
        self.product_tree.heading("model", text="Model", anchor=tk.W)
        self.product_tree.heading("serial_number", text="Số Seri", anchor=tk.W)
        self.product_tree.heading("price", text="Giá", anchor=tk.E)
        self.product_tree.heading("stock", text="Tồn Kho", anchor=tk.CENTER)
        self.product_tree.heading("entry_date", text="Ngày Nhập", anchor=tk.CENTER)

        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.product_tree.bind("<Button-3>", self.show_context_menu)  # Bắt sự kiện chuột phải
        self.load_products()

    def load_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)  # Xóa các dòng hiện tại

        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, model, serial_number, price, stock, entry_date FROM products ORDER BY id ASC")
            rows = cur.fetchall()
            for row in rows:
                self.product_tree.insert("", tk.END, values=row)
            cur.close()
            conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")

    def add_device(self):
        add_window = Toplevel(self.root)
        add_window.title("Thêm Thiết Bị")
        add_window.geometry("400x300")

        tk.Label(add_window, text="Tên Thiết Bị:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.device_name = tk.Entry(add_window)
        self.device_name.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Model:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.device_model = tk.Entry(add_window)
        self.device_model.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Số Seri:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.device_serial = tk.Entry(add_window)
        self.device_serial.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Giá:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.device_price = tk.Entry(add_window)
        self.device_price.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Tồn Kho:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.device_stock = tk.Entry(add_window)
        self.device_stock.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Ngày Nhập:").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        self.device_date = tk.Entry(add_window)
        self.device_date.grid(row=5, column=1, padx=10, pady=10)
        tk.Button(add_window, text="Chọn Ngày", command=lambda: self.show_calendar(self.device_date, add_window)).grid(row=5, column=2, padx=5, pady=10)

        tk.Button(add_window, text="Lưu", command=self.save_device).grid(row=6, column=0, padx=10, pady=20)
        tk.Button(add_window, text="Hủy", command=add_window.destroy).grid(row=6, column=1, padx=10, pady=20)

    def show_calendar(self, entry_widget, parent_window):
        def select_date():
            date_str = cal.get_date()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, date_str)
            cal_window.destroy()

        cal_window = Toplevel(parent_window)
        cal_window.title("Chọn Ngày")
        cal = Calendar(cal_window, selectmode='day', year=2023, month=10, day=10)
        cal.pack(pady=20)
        tk.Button(cal_window, text="Chọn", command=select_date).pack(pady=10)

    def save_device(self):
        name = self.device_name.get().strip()
        model = self.device_model.get().strip()
        serial = self.device_serial.get().strip()
        price = self.device_price.get().strip()
        stock = self.device_stock.get().strip()
        entry_date = self.device_date.get().strip()

        if not all([name, model, serial, price, stock, entry_date]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá phải là số và Tồn Kho phải là số nguyên.")
            return
        formatted_price = f"{price:,.0f} VND"
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO products (name, model, serial_number, price, stock, entry_date, employee_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, model, serial, price, stock, entry_date, self.current_employee_id))
                conn.commit()
                messagebox.showinfo("Thông báo", "Thêm thiết bị thành công!")
                self.load_products()
                add_window = self.device_name.master
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm thiết bị: {e}")
            finally:
                cur.close()
                conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")

    def export_product(self):
        export_window = Toplevel(self.root)
        export_window.title("Xuất Hàng")
        export_window.geometry("400x250")

        # Chọn khách hàng từ cơ sở dữ liệu
        tk.Label(export_window, text="Chọn Khách Hàng:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.customer_combo = ttk.Combobox(export_window, values=self.get_customers(), state='readonly')
        self.customer_combo.grid(row=0, column=1, padx=10, pady=10)

        # Chọn thiết bị từ cơ sở dữ liệu (chỉ sản phẩm có tồn kho > 0)
        tk.Label(export_window, text="Chọn Thiết Bị Model :").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.product_combo = ttk.Combobox(export_window, values=self.get_available_products(), state='readonly')
        self.product_combo.grid(row=1, column=1, padx=10, pady=10)

        # Nhập số lượng muốn xuất
        tk.Label(export_window, text="Số Lượng Xuất:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.export_quantity = tk.Entry(export_window)
        self.export_quantity.grid(row=2, column=1, padx=10, pady=10)

        # Nút xuất hàng
        tk.Button(export_window, text="Xuất Hàng", command=self.process_export).grid(row=3, column=0, columnspan=2, pady=20)

    def get_customers(self):
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id, name FROM customers")
                customers = [f"{row[1]} (ID: {row[0]})" for row in cur.fetchall()]
                return customers
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lấy danh sách khách hàng thất bại: {e}")
                return []
            finally:
                cur.close()
                conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")
            return []

    def get_available_products(self):
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT model FROM products WHERE stock > 0")
                products = [row[0] for row in cur.fetchall()]
                return products
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lấy danh sách sản phẩm thất bại: {e}")
                return []
            finally:
                cur.close()
                conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")
            return []

    def process_export(self):
        customer = self.customer_combo.get()
        model = self.product_combo.get()
        quantity = self.export_quantity.get().strip()

        if not all([customer, model, quantity]):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin xuất hàng.")
            return

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng xuất phải là số nguyên dương.")
            return

        # Tách ID khách hàng từ combobox
        try:
            customer_id = int(customer.split("(ID: ")[1][:-1])
        except (IndexError, ValueError):
            messagebox.showerror("Lỗi", "Định dạng khách hàng không hợp lệ.")
            return

        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                # Kiểm tra tồn kho của sản phẩm
                cur.execute("SELECT stock FROM products WHERE model = %s", (model,))
                result = cur.fetchone()
                if not result:
                    messagebox.showerror("Lỗi", "Sản phẩm không tồn tại.")
                    return
                stock = result[0]

                if stock >= quantity:
                    # Cập nhật tồn kho
                    cur.execute("UPDATE products SET stock = stock - %s WHERE model = %s", (quantity, model))
                    
                    # Ghi vào bảng orders (Đơn hàng)
                    cur.execute("""
                        INSERT INTO orders (customer_id, product_name, quantity, employee_id) 
                        VALUES (%s, %s, %s, %s)
                    """, (customer_id, model, quantity, self.current_employee_id))
                    
                    conn.commit()
                    messagebox.showinfo("Thông báo", "Xuất hàng thành công!")
                    self.load_products()
                    export_window = self.export_quantity.master
                    export_window.destroy()
                else:
                    messagebox.showerror("Lỗi", "Số lượng tồn kho không đủ.")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Lỗi", f"Xuất hàng thất bại: {e}")
            finally:
                cur.close()
                conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")

    def show_context_menu(self, event):
        selected_item = self.product_tree.identify_row(event.y)
        if selected_item:
            self.product_tree.selection_set(selected_item)
            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="Xem Chi Tiết", command=self.view_device_details)
            menu.add_command(label="Chỉnh Sửa", command=self.edit_selected_device)
            menu.post(event.x_root, event.y_root)

    def view_device_details(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn một thiết bị để xem chi tiết.")
            return
        item_values = self.product_tree.item(selected_item, "values")
        price = float(item_values[4])
        details_message = (
            f"ID: {item_values[0]}\n"
            f"Tên: {item_values[1]}\n"
            f"Model: {item_values[2]}\n"
            f"Số Seri: {item_values[3]}\n"
            f"Giá: {item_values[4]} VND\n"
            f"Tồn Kho: {item_values[5]}\n"
            f"Ngày Nhập: {item_values[6]}"
        )
        messagebox.showinfo("Chi Tiết Thiết Bị", details_message)

    def edit_selected_device(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn một thiết bị để chỉnh sửa.")
            return
        item_values = self.product_tree.item(selected_item, "values")
        self.edit_device(item_values)

    def edit_device(self, item_values):
        edit_window = Toplevel(self.root)
        edit_window.title("Chỉnh Sửa Thiết Bị")
        edit_window.geometry("400x350")

        tk.Label(edit_window, text="Tên Thiết Bị:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        device_name = tk.Entry(edit_window)
        device_name.insert(0, item_values[1])
        device_name.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Model:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        device_model = tk.Entry(edit_window)
        device_model.insert(0, item_values[2])
        device_model.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Số Seri:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        device_serial = tk.Entry(edit_window)
        device_serial.insert(0, item_values[3])
        device_serial.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Giá:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        device_price = tk.Entry(edit_window)
        device_price.insert(0, item_values[4])
        device_price.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Tồn Kho:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        device_stock = tk.Entry(edit_window)
        device_stock.insert(0, item_values[5])
        device_stock.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Ngày Nhập:").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        device_date = tk.Entry(edit_window)
        device_date.insert(0, item_values[6])
        device_date.grid(row=5, column=1, padx=10, pady=10)
        tk.Button(edit_window, text="Chọn Ngày", command=lambda: self.show_calendar(device_date, edit_window)).grid(row=5, column=2, padx=5, pady=10)

        tk.Button(edit_window, text="Lưu", command=lambda: self.update_device(
            item_values[0],
            device_name,
            device_model,
            device_serial,
            device_price,
            device_stock,
            device_date,
            edit_window
        )).grid(row=6, column=0, padx=10, pady=20)
        tk.Button(edit_window, text="Hủy", command=edit_window.destroy).grid(row=6, column=1, padx=10, pady=20)

    def update_device(self, device_id, name_entry, model_entry, serial_entry, price_entry, stock_entry, date_entry, window):
        name = name_entry.get().strip()
        model = model_entry.get().strip()
        serial = serial_entry.get().strip()
        price = price_entry.get().strip()
        stock = stock_entry.get().strip()
        entry_date = date_entry.get().strip()

        if not all([name, model, serial, price, stock, entry_date]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá phải là số và Tồn Kho phải là số nguyên.")
            return
        formatted_price = f"{price:,.0f} VND"

        conn = connect_db()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE products 
                    SET name = %s, model = %s, serial_number = %s, price = %s, stock = %s, entry_date = %s 
                    WHERE id = %s
             
                """, (name, model, serial, price, stock, entry_date, device_id))
                conn.commit()
                messagebox.showinfo("Thông báo", "Cập nhật thiết bị thành công!")
                self.load_products()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Cập nhật thiết bị thất bại: {e}")
            finally:
                cur.close()
                conn.close()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cơ sở dữ liệu.")

    def logout(self):
        if messagebox.askyesno("Đăng Xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            self.root.destroy()
            root = tk.Tk()
            app = MainApplication(root)
            root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()