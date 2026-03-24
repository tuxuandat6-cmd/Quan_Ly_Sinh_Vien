import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import pandas as pd
from database import get_connection


class LecturerApp(ctk.CTk):
    def __init__(self, magv):
        super().__init__()
        self.magv = magv
        self.title(f"CMC University - Giảng Viên [{self.magv}]")
        self.geometry("1150x700")
        self.main_color = "#1a3a8a"

        # Khai báo biến giao diện
        self.cb_classes = None
        self.cb_subjects = None  # Thêm ô chọn môn học
        self.lbl_sv = None
        self.ent_qt = None
        self.ent_thi = None
        self.grade_tree = None

        # Lưu trữ dữ liệu phân công để xử lý logic chọn lớp - môn
        self.assignments = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.main_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="CMC LECTURER", font=("Arial", 20, "bold"), text_color="white").pack(pady=30)

        self.create_menu_btn("Thông tin cá nhân", self.show_info)
        self.create_menu_btn("Lớp học phụ trách", self.show_classes)
        self.create_menu_btn("Quản lý điểm số", self.show_grading)

        ctk.CTkButton(self.sidebar, text="Đăng xuất", fg_color="#e74c3c", command=self.logout).pack(side="bottom",
                                                                                                    fill="x", padx=20,
                                                                                                    pady=20)

        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8f9fa")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.show_info()

    def create_menu_btn(self, text, command):
        ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", anchor="w", height=45, command=command).pack(
            fill="x", padx=10, pady=5)

    def clear_view(self):
        for widget in self.container.winfo_children(): widget.destroy()

    def show_info(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="THÔNG TIN GIẢNG VIÊN", font=("Arial", 22, "bold"),
                     text_color=self.main_color).pack(pady=20)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MaGV, TenGV, HocVi, Email FROM GiangVien WHERE MaGV=?", (self.magv,))
            r = cursor.fetchone()
            if r:
                card = ctk.CTkFrame(self.container, fg_color="white", corner_radius=15)
                card.pack(pady=10, padx=50, fill="both", expand=True)
                info = f"Mã GV: {r[0]}\n\nHọ tên: {r[1]}\n\nHọc vị: {r[2]}\n\nEmail: {r[3]}"
                ctk.CTkLabel(card, text=info, font=("Arial", 16), justify="left").pack(pady=40, padx=40)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_classes(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="DANH SÁCH LỚP DẠY", font=("Arial", 22, "bold"),
                     text_color=self.main_color).pack(pady=20)
        cols = ("Mã Lớp", "Tên Lớp", "Mã Môn", "Tên Môn Học")
        tree = self.create_tree(cols)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("{CALL sp_GiangVien_XemLopDay (?)}", (self.magv,))
            for r in cursor.fetchall(): tree.insert("", "end", values=(r[2], r[3], r[4], r[5]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_grading(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="QUẢN LÝ ĐIỂM SINH VIÊN", font=("Arial", 22, "bold"),
                     text_color=self.main_color).pack(pady=10)

        # --- Khung lọc (Lớp + Môn) ---
        f_top = ctk.CTkFrame(self.container, fg_color="transparent")
        f_top.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(f_top, text="Lớp:").pack(side="left", padx=5)
        self.cb_classes = ctk.CTkComboBox(f_top, width=150, command=self.on_class_selected)  # Gắn sự kiện khi chọn lớp
        self.cb_classes.pack(side="left", padx=5)

        ctk.CTkLabel(f_top, text="Môn:").pack(side="left", padx=5)
        self.cb_subjects = ctk.CTkComboBox(f_top, width=200)
        self.cb_subjects.pack(side="left", padx=5)

        ctk.CTkButton(f_top, text="Xem", width=70, command=self.load_students).pack(side="left", padx=2)
        ctk.CTkButton(f_top, text="Xuất Excel", fg_color="orange", width=90, command=self.export_excel).pack(
            side="left", padx=2)

        # --- Khung nhập điểm ---
        f_edit = ctk.CTkFrame(self.container, fg_color="white", corner_radius=10)
        f_edit.pack(fill="x", padx=20, pady=10)
        self.lbl_sv = ctk.CTkLabel(f_edit, text="Chọn SV trong bảng", text_color="gray", font=("Arial", 13, "bold"))
        self.lbl_sv.grid(row=0, column=0, padx=20, pady=10)

        self.ent_qt = ctk.CTkEntry(f_edit, width=70, placeholder_text="QT")
        self.ent_qt.grid(row=0, column=1, padx=5)
        self.ent_thi = ctk.CTkEntry(f_edit, width=70, placeholder_text="Thi")
        self.ent_thi.grid(row=0, column=2, padx=5)

        ctk.CTkButton(f_edit, text="LƯU ĐIỂM", fg_color="green", width=100, font=("Arial", 12, "bold"),
                      command=self.save_score).grid(row=0, column=3, padx=10)

        # Bảng điểm (Bỏ cột Môn vì đã chọn ở trên rồi cho đỡ rối)
        self.grade_tree = self.create_tree(("MaSV", "Họ Tên", "Lớp", "Điểm QT", "Điểm Thi", "Tổng Kết"))
        self.grade_tree.bind("<<TreeviewSelect>>", self.on_select_sv)

        self.get_initial_data()

    def get_initial_data(self):
        """Lấy toàn bộ dữ liệu phân công để nạp vào các ComboBox"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("{CALL sp_GiangVien_XemLopDay (?)}", (self.magv,))
            self.assignments = cursor.fetchall()
            conn.close()

            # Lấy danh sách Lớp duy nhất (Unique)
            class_list = sorted(list(set([r[3] for r in self.assignments])))
            if class_list:
                self.cb_classes.configure(values=class_list)
                self.cb_classes.set(class_list[0])
                self.on_class_selected(class_list[0])  # Tự động load môn cho lớp đầu tiên
        except:
            pass

    def on_class_selected(self, selected_class):
        """Khi chọn lớp, chỉ hiện những môn giảng viên dạy ở lớp đó"""
        subject_list = [r[5] for r in self.assignments if r[3] == selected_class]
        self.cb_subjects.configure(values=subject_list)
        if subject_list:
            self.cb_subjects.set(subject_list[0])

    def load_students(self):
        """Nạp danh sách SV, lọc theo đúng Lớp và đúng Môn đã chọn"""
        for r in self.grade_tree.get_children(): self.grade_tree.delete(r)
        selected_class = self.cb_classes.get()
        selected_sub = self.cb_subjects.get()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Gọi SP lấy điểm lớp, sau đó lọc thêm Môn ở phía Python để chính xác 100%
            cursor.execute("{CALL sp_GiangVien_XemDiemLop (?, ?)}", (selected_class, self.magv))
            for r in cursor.fetchall():
                # r[3] là TenMon trong View vw_SinhVien_Diem
                if r[3] == selected_sub:
                    # Chỉ lấy các cột: MaSV, HoTen, TenLop, DiemQT, DiemThi, DiemTongKet
                    row_data = (r[0], r[1], r[2], r[4] if r[4] is not None else "",
                                r[5] if r[5] is not None else "", r[6] if r[6] is not None else "")
                    self.grade_tree.insert("", "end", values=row_data)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_select_sv(self, _):
        sel = self.grade_tree.selection()
        if sel:
            v = self.grade_tree.item(sel)['values']
            self.lbl_sv.configure(text=f"SV: {v[1]}", text_color="#1a3a8a")
            self.ent_qt.delete(0, "end")
            self.ent_qt.insert(0, v[3])
            self.ent_thi.delete(0, "end")
            self.ent_thi.insert(0, v[4])

    def save_score(self):
        sel = self.grade_tree.selection()
        if not sel:
            messagebox.showwarning("Chú ý", "Vui lòng chọn sinh viên!")
            return
        v = self.grade_tree.item(sel)['values']
        selected_sub = self.cb_subjects.get()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Tìm MaMon từ TenMon
            cursor.execute("SELECT MaMon FROM MonHoc WHERE TenMon=?", (selected_sub,))
            mamon = cursor.fetchone()[0]

            # Gọi SP sp_Diem_Update (MaSV, MaMon, DiemQT, DiemThi, MaGV)
            cursor.execute("{CALL sp_Diem_Update (?,?,?,?,?)}",
                           (v[0], mamon, float(self.ent_qt.get()), float(self.ent_thi.get()), self.magv))
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", f"Đã lưu điểm môn {selected_sub}")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu: {e}")

    def export_excel(self):
        data = [self.grade_tree.item(r)['values'] for r in self.grade_tree.get_children()]
        df = pd.DataFrame(data, columns=["Mã SV", "Họ Tên", "Lớp", "QT", "Thi", "Tổng Kết"])
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            initialfile=f"Diem_{self.cb_classes.get()}_{self.cb_subjects.get()}.xlsx")
        if path:
            df.to_excel(path, index=False)
            messagebox.showinfo("Thành công", "Đã xuất file Excel!")

    def create_tree(self, cols):
        f = tk.Frame(self.container, bg="white")
        f.pack(fill="both", expand=True, padx=20, pady=10)
        # Căn giữa bảng và thiết kế tiêu đề
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        t = ttk.Treeview(f, columns=cols, show="headings", height=15)
        for c in cols:
            t.heading(c, text=c)
            t.column(c, anchor="center", width=130)
        t.pack(fill="both", expand=True)
        return t

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Đăng xuất hệ thống?"):
            self.destroy()
            import main
            main.LoginApp().mainloop()