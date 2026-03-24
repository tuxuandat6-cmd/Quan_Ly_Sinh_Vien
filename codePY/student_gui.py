import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class StudentApp(ctk.CTk):
    def __init__(self, masv):
        super().__init__()
        self.masv = masv
        self.title(f"CMC University - Dashboard Sinh Viên [{self.masv}]")
        self.geometry("1100x600")

        # Cấu hình Layout Sidebar
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a3a8a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="CMC STUDENT", font=("Arial", 20, "bold"), text_color="white").pack(pady=30)

        ctk.CTkButton(self.sidebar, text="Thông tin cá nhân", fg_color="transparent", anchor="w",
                      command=self.show_info).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Kết quả học tập", fg_color="transparent", anchor="w",
                      command=self.show_diem).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Học phần đăng ký", fg_color="transparent", anchor="w",
                      command=self.show_hp).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Đăng ký học ", fg_color="transparent", anchor="w",
                      command=self.show_registration).pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Đăng xuất", fg_color="#e74c3c",
                      command=self.logout).pack(side="bottom", fill="x", padx=20, pady=20)

        # Vùng nội dung
        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8f9fa")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.show_info()  # Mặc định hiện thông tin

        # ham xoa du lieu cũ

    def clear_view(self):
        for widget in self.container.winfo_children(): widget.destroy()
        # hàm show thông tin cá nhân

    def show_info(self):
        self.clear_view()

        # Tiêu đề trang
        ctk.CTkLabel(self.container, text="THÔNG TIN CHI TIẾT SINH VIÊN",
                     font=("Arial", 24, "bold"), text_color="#1a3a8a").pack(pady=(20, 10))

        try:
            # kết nối database
            conn = get_connection()  # kết nối sql server
            cursor = conn.cursor()  # để thực thi câu lệnh sql

            # Truy vấn đầy đủ các cột từ bảng SinhVien
            query = """
                    SELECT MaSV, \
                           HoTen, \
                           NgaySinh, \
                           GioiTinh, \
                           DiaChi, \
                           SoDienThoai, \
                           Email, \
                           TrangThai, \
                           MaLop
                    FROM dbo.SinhVien
                    WHERE MaSV = ? \
                    """
            cursor.execute(query, (self.masv,))
            row = cursor.fetchone()
            conn.close()

            if row:
                # Tạo khung chứa thông tin
                info_card = ctk.CTkFrame(self.container, fg_color="white", corner_radius=20, border_width=1,
                                         border_color="#e0e0e0")
                info_card.pack(pady=10, padx=40, fill="both", expand=True)

                # Danh sách các nhãn hiển thị tương ứng với các cột
                labels = [
                    "Mã sinh viên:", "Họ và tên:", "Ngày sinh:",
                    "Giới tính:", "Địa chỉ:", "Số điện thoại:",
                    "Email:", "Trạng thái:", "Mã lớp:"
                ]

                # Xử lý dữ liệu hiển thị (đề phòng dữ liệu NULL hoặc định dạng ngày tháng)
                data = list(row)
                if data[2]:  # Định dạng lại Ngày sinh
                    data[2] = data[2].strftime("%d/%m/%Y")

                # Hiển thị thông tin theo hàng
                for i in range(len(labels)):
                    # Khung nhỏ cho mỗi dòng thông tin
                    row_frame = ctk.CTkFrame(info_card, fg_color="transparent")
                    row_frame.pack(fill="x", padx=30, pady=8)

                    # Nhãn tiêu đề (bên trái)
                    lbl_title = ctk.CTkLabel(row_frame, text=labels[i], font=("Arial", 14, "bold"),
                                             text_color="#555555", width=150, anchor="w")
                    lbl_title.pack(side="left")

                    # Nhãn nội dung (bên phải) - Sử dụng text_color khác nhau cho Trạng thái
                    val_color = "#1a3a8a"
                    if labels[i] == "Trạng thái:":
                        val_color = "green" if str(data[i]) == "Đang học" else "#e67e22"

                    lbl_value = ctk.CTkLabel(row_frame, text=str(data[i]) if data[i] else "Chưa cập nhật",
                                             font=("Arial", 14), text_color=val_color, anchor="w")
                    lbl_value.pack(side="left", padx=10)

                    # Dấu gạch ngang phân cách nhẹ giữa các dòng
                    if i < len(labels) - 1:
                        line = ctk.CTkFrame(info_card, height=1, fg_color="#f0f0f0")
                        line.pack(fill="x", padx=30)

        except Exception as e:
            messagebox.showerror("Lỗi dữ liệu", f"Không thể hiển thị thông tin: {e}")
        # hàm show điểm

    def show_diem(self):
        self.clear_view()
        # 1. Hiện tiêu đề
        ctk.CTkLabel(self.container, text="KẾT QUẢ HỌC TẬP",
                     font=("Arial", 22, "bold"), text_color="#1a3a8a").pack(pady=20)

        # 2.tạo khung và bảng trước
        cols = ("Tên Môn", "Điểm QT", "Điểm Thi", "Tổng Kết", "Kết Quả")
        frame = tk.Frame(self.container, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=120)
        tree.pack(fill="both", expand=True)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Sử dụng Stored Procedure
            cursor.execute("{CALL sp_SinhVien_XemDiem (?)}", (self.masv,))
            rows = cursor.fetchall()

            for r in rows:
                # r[3]: TenMon, r[4]: DiemQT, r[5]: DiemThi, r[6]: DiemTongKet
                diem_tk = r[6]
                if diem_tk is None:
                    ket_qua = "Chưa có"
                elif diem_tk >= 4.0:
                    ket_qua = "Đạt"
                else:
                    ket_qua = "Học lại"

                row_data = [
                    r[3],  # Tên môn
                    r[4] if r[4] is not None else "",  # Điểm QT
                    r[5] if r[5] is not None else "",  # Điểm Thi
                    r[6] if r[6] is not None else "",  # Tổng kết
                    ket_qua  # Kết quả vừa tính ở trên
                ]
                tag = ""
                if ket_qua == "Đạt":
                    tag = "dong_dat"
                elif ket_qua == "Học lại":
                    tag = "dong_hoclai"

                tree.insert("", "end", values=row_data, tags=(tag,))

            conn.close()
            tree.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        # hàm show học phần đã đăng ký

    def show_hp(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="HỌC PHẦN ĐÃ ĐĂNG KÝ",
                     font=("Arial", 22, "bold"), text_color="#1a3a8a").pack(pady=20)

        # Tạo bảng trước
        cols = ("Mã Môn", "Tên Môn Học", "Mã Lớp", "Tên Lớp")
        frame = tk.Frame(self.container, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=150)
        tree.pack(fill="both", expand=True)

        # gọi database
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Query từ View
            query = "SELECT MaMon, TenMon, MaLop, TenLop FROM dbo.vw_SinhVien_MonHoc WHERE MaSV = ?"
            cursor.execute(query, (self.masv,))
            for r in cursor.fetchall():
                tree.insert("", "end", values=tuple(r))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi SQL", f"Không thể lấy học phần: {e}")
        # hàm hiển thị các học phần chưa đăng ký

    def show_registration(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="ĐĂNG KÝ HỌC PHẦN MỚI",
                     font=("Arial", 22, "bold"), text_color="#1a3a8a").pack(pady=20)
        # tao bang hien thi cac mon chua dang ky
        cols = ("Mã Môn", "Tên Môn Học", "Số Tín Chỉ")
        frame = tk.Frame(self.container, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.reg_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.reg_tree.heading(c, text=c)
            self.reg_tree.column(c, width=150, anchor="center")
        self.reg_tree.pack(fill="both", expand=True)

        # Nut xac nhan dang ky
        self.btn_confirm = ctk.CTkButton(self.container, text="XÁC NHẬN ĐĂNG KÝ",
                                         fg_color="#27ae60", hover_color="219150",
                                         font=("Arial", 14, "bold"), command=self.perform_registration)
        self.btn_confirm.pack(pady=20)

        # tai du lieu mon hoc
        self.load_availabel_courses()
        # hàm tải danh sách các môn học chưa đky

    def load_availabel_courses(self):
        """Chỉ hiện những môn thuộc Khoa của sinh viên và SV chưa đăng ký"""
        for r in self.reg_tree.get_children():
            self.reg_tree.delete(r)
        try:
            conn = get_connection()
            cursor = conn.cursor()


            query = """
                    SELECT mh.MaMon, mh.TenMon, mh.SoTinChi
                    FROM dbo.MonHoc mh
                    WHERE mh.MaKhoa = (SELECT l.MaKhoa \
                                       FROM dbo.SinhVien sv \
                                                JOIN dbo.Lop l ON sv.MaLop = l.MaLop \
                                       WHERE sv.MaSV = ?)
                      AND mh.MaMon NOT IN (SELECT MaMon \
                                           FROM dbo.DangKyHoc \
                                           WHERE MaSV = ?) \
                    """

            cursor.execute(query, (self.masv, self.masv))
            for row in cursor.fetchall():
                self.reg_tree.insert("", "end", values=(row[0], row[1], row[2]))
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải môn học theo khoa: {e}")

    def perform_registration(self):
        """Luu dang ky hoc vao database"""
        selected = self.reg_tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn môn học muốn đăng ký!")
            return

        item_value = self.reg_tree.item(selected)['values']
        ma_mon = item_value[0]
        ten_mon = item_value[1]

        if messagebox.askyesno("Xác nhận", f"Bạn muốn đăng ký: {ten_mon}?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                # chen vao bang Dangkyhoc
                sql = """
                      INSERT INTO dbo.DangKyHoc(MaSV, MaMon, HocKy, NamHoc)
                      Values (?, ?, ?, ?) \
                      """
                cursor.execute(sql, (self.masv, ma_mon, 1, "2023-2024"))

                conn.commit()
                conn.close()

                messagebox.showinfo("Thành công", f"Đã đăng ký thành công môn: {ten_mon}")
                self.load_availabel_courses()
            except Exception as e:
                # neu loi trung lap (Da dang ky roi), sql se bao loi vi pham khoa chinh
                messagebox.showerror("Lỗi", f"Không thể đăng ký: {e}")
        # hàm tạo 1 bảng trên giao diện và hiển thị dữ liệu lấy từ database

    def create_table(self, cols, query):
        frame = tk.Frame(self.container, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c); tree.column(c, width=150, anchor="center")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (self.masv,))
            for r in cursor.fetchall(): tree.insert("", "end", values=tuple(r))
            conn.close()
        except:
            pass
        tree.pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn muốn đăng xuất?"):
            self.destroy()
            # Gọi lại main để hiện login (Import cục bộ để tránh lỗi vòng lặp)
            import main
            main.LoginApp().mainloop()