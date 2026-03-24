import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import get_connection

class PDTApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.ent_ma = None
        self.ent_ten = None
        self.ent_ns = None
        self.ent_lop = None
        self.ent_search = None
        self.sv_tree = None
        self.class_tree = None
        self.ent_malop = None
        self.ent_tenlop = None
        self.dict_gv = {}
        self.dict_lop = {}
        self.dict_mon = {}
        self.title("CMC University- Hệ thống quản lý đào tạo")
        self.geometry("1250x800")

        # color layout
        self.main_color = "#1a3a8a"

        # cau hinh Layout: cot 0 la sidebar, cot 1 la noi dung chinh
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # thanh sidebar (menu ben trai)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.main_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="CMC ADMIN", font=("Arial", 24, "bold"), text_color="white").pack(pady=40)

        # cac nut menu dieu huong
        self.create_menu_btn("Trang Chủ (Dashboard) ", self.show_dashboard)
        self.create_menu_btn("Quản Lý Sinh Viên", self.show_manage_students)
        self.create_menu_btn("Báo Cáo Thống Kê", self.show_status)
        self.create_menu_btn("Quản Lý Lớp & Môn", self.show_manage_classes)
        self.create_menu_btn("Phân Công Giảng Dạy", self.show_assignments)

        # nut dang xuat dat duoi cung sidebar
        ctk.CTkButton(self.sidebar, text="Đăng xuất", fg_color="#e74c3c", hover_color="#c0392b",
                      command=self.logout).pack(side="bottom", fill="x", padx=20, pady=20)

        # Vung chua noi dung chinh o ben phai
        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color="#f8f9fa")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Mac dinh khi moi len se hien Dashboard dau tien
        self.show_dashboard()

        # ham ho tro nut menu nhanh

    def create_menu_btn(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent",
                            anchor="w", font=("Arial", 15), height=50, command=command)
        btn.pack(fill="x", padx=10, pady=5)

        # ham xoa noi dung cu de ve noi dung moi (chuyen trang)

    def clear_view(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        # chuc nang 1: trang chu voi cac the tom tat

    def show_dashboard(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="BÁO CÁO TỔNG QUAN HỆ THỐNG", font=("Arial", 26, "bold"),
                     text_color=self.main_color).pack(pady=20)

        # ---các thẻ thống kê
        card_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        card_frame.pack(fill="x", padx=50)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Lấy số liệu tổng quát
            cursor.execute("select count(*) from SinhVien")
            total_sv = cursor.fetchone()[0]
            cursor.execute("select count(*) from GiangVien")
            total_gv = cursor.fetchone()[0]
            cursor.execute("select count(*) from Lop")
            total_lop = cursor.fetchone()[0]

            self.create_card(card_frame, "TỔNG SINH VIÊN", total_sv, "#3498db").grid(row=0, column=0, padx=15)
            self.create_card(card_frame, "TỔNG GIẢNG VIÊN", total_gv, "#2ecc71").grid(row=0, column=1, padx=15)
            self.create_card(card_frame, "SỐ LƯỢNG LỚP", total_lop, "#f1c40f").grid(row=0, column=2, padx=15)

            # Khung chứa 2 biểu đồ tròn
            chart_container = ctk.CTkFrame(self.container, fg_color="white", corner_radius=20)
            chart_container.pack(fill="both", expand=True, padx=50, pady=20)

            # Lấy dữ liệu cho biểu đồ 1: Sĩ số lớp
            cursor.execute("{CALL sp_PDT_ThongKe_SiSo}")
            data_siso = cursor.fetchall()

            # Lấy dữ liệu cho biểu đồ 2: Tỷ lệ Đạt/Rớt
            cursor.execute("{CALL sp_PDT_ThongKe_KetQua}")
            data_kq = cursor.fetchall()
            conn.close()

            # Vẽ 2 biểu đồ nằm cạnh nhau
            self.draw_dual_pie_charts(chart_container, data_siso, data_kq)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải Dashboard: {e}")

    def draw_dual_pie_charts(self, parent_frame, data_siso, data_kq):
        """Vẽ 2 biểu đồ tròn: Phân bố lớp và Tỷ lệ Đạt/Rớt"""

        # 1. Khởi tạo Figure với 2 vùng vẽ (subplots) nằm ngang
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor('white')  # Nền trắng đồng bộ với khung

        # --- biểu đồ 1: phân bổ sinh viên theo lớp
        if data_siso:
            labels_l = [r[1] for r in data_siso]  # Tên lớp
            sizes_l = [r[2] for r in data_siso]  # Sĩ số
            colors_l = ['#1a3a8a', '#3498db', '#5dade2', '#aed6f1', '#154360']  # Tone xanh CMC

            # Vẽ biểu đồ tròn bên trái
            ax1.pie(sizes_l, labels=labels_l, autopct='%1.1f%%', startangle=140,
                    colors=colors_l, textprops={'fontsize': 8})
            ax1.set_title("Phân bố SV theo Lớp", fontdict={'fontsize': 12, 'weight': 'bold'})
        else:
            ax1.text(0.5, 0.5, 'Không có dữ liệu lớp', ha='center')

        # --- BIỂU ĐỒ 2: tổng hợp tỷ lệ dạt rớt
        if data_kq:
            # Cộng dồn tất cả các lớp để ra tổng số Đạt và Rớt toàn trường
            total_dat = sum(r[1] for r in data_kq)
            total_rot = sum(r[2] for r in data_kq)

            labels_k = ['Đạt (>=5)', 'Rớt (<5)']
            sizes_k = [total_dat, total_rot]
            colors_k = ['#2ecc71', '#e74c3c']  # Xanh lá - Đỏ

            # Vẽ biểu đồ tròn bên phải
            ax2.pie(sizes_k, labels=labels_k, autopct='%1.1f%%', startangle=90,
                    colors=colors_k, wedgeprops=dict(width=0.4), textprops={'fontsize': 8})
            ax2.set_title("Tỷ lệ Học lực Toàn trường", fontdict={'fontsize': 12, 'weight': 'bold'})
        else:
            ax2.text(0.5, 0.5, 'Không có dữ liệu điểm', ha='center')

        # Tối ưu hóa khoảng cách giữa 2 biểu đồ
        plt.tight_layout()


        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


    @staticmethod
    def create_card(parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=color, width=250, height=150, corner_radius=15)
        ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color="white").pack(pady=(20, 0))
        ctk.CTkLabel(card, text=str(value), font=("Arial", 45, "bold"), text_color="white").pack(pady=10)
        return card

    # chuc nang 2: quan ly sinh vien (crud)
    def show_manage_students(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="QUẢN LÝ DANH SÁCH SINH VIÊN", font=("Arial", 22, "bold")).pack(pady=10)

        # 2.1. Khung Nhập Liệu
        f_input = ctk.CTkFrame(self.container, fg_color="white", corner_radius=15)
        f_input.pack(fill="x", padx=20, pady=10)

        # Cấu hình để các cột trong khung này giãn nở đều nhau
        f_input.grid_columnconfigure((0, 2), weight=0)  # Cột chứa Label (không giãn)
        f_input.grid_columnconfigure((1, 3), weight=1)  # Cột chứa Entry (giãn đều)

        # Hàng 1
        ctk.CTkLabel(f_input, text="Mã sinh viên:", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=(20, 10),
                                                                                     pady=15, sticky="w")
        self.ent_ma = ctk.CTkEntry(f_input, placeholder_text="Nhập mã SV", height=35)
        self.ent_ma.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="ew")

        ctk.CTkLabel(f_input, text="Họ và Tên:", font=("Arial", 13, "bold")).grid(row=0, column=2, padx=(20, 10),
                                                                                  pady=15, sticky="w")
        self.ent_ten = ctk.CTkEntry(f_input, placeholder_text="Nhập họ tên đầy đủ", height=35)
        self.ent_ten.grid(row=0, column=3, padx=(0, 20), pady=15, sticky="ew")

        # Hàng 2
        ctk.CTkLabel(f_input, text="Ngày sinh:", font=("Arial", 13, "bold")).grid(row=1, column=0, padx=(20, 10),
                                                                                  pady=15, sticky="w")
        self.ent_ns = ctk.CTkEntry(f_input, placeholder_text="YYYY-MM-DD", height=35)
        self.ent_ns.grid(row=1, column=1, padx=(0, 20), pady=15, sticky="ew")

        ctk.CTkLabel(f_input, text="Lớp học:", font=("Arial", 13, "bold")).grid(row=1, column=2, padx=(20, 10), pady=15,
                                                                                sticky="w")
        self.ent_lop = ctk.CTkEntry(f_input, placeholder_text="Mã lớp (VD: 24IT4)", height=35)
        self.ent_lop.grid(row=1, column=3, padx=(0, 20), pady=15, sticky="ew")

        # 2.2 khung nut chuc nang (Them/sua/xoa/tim/Excel)
        f_btns = ctk.CTkFrame(self.container, fg_color="transparent")
        f_btns.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(f_btns, text="THÊM MỚI", fg_color="green", width=100, command=self.add_sv).pack(side="left",
                                                                                                      padx=5)
        ctk.CTkButton(f_btns, text="CẬP NHẬT", fg_color="blue", width=100, command=self.update_sv).pack(side="left",
                                                                                                        padx=5)
        ctk.CTkButton(f_btns, text="XÓA SV", fg_color="#e74c3c", width=100, command=self.delete_sv).pack(side="left",
                                                                                                         padx=5)
        # ô tim kiem
        self.ent_search = ctk.CTkEntry(f_btns, placeholder_text="Tìm theo tên/mã...", width=200)
        self.ent_search.pack(side="left", padx=20)
        ctk.CTkButton(f_btns, text="Tìm", width=60, command=self.search_sv).pack(side="left")

        ctk.CTkButton(f_btns, text="XUẤT EXCEL", fg_color="orange", width=120, command=self.export_excel).pack(
            side="right", padx=5)

        # 2.3 bang hien thi Treeview
        cols = ("MaSV", "Họ Tên", "Ngày Sinh", "Mã Lớp", "Trạng Thái")
        self.sv_tree = ttk.Treeview(self.container, columns=cols, show="headings")
        for c in cols:
            self.sv_tree.heading(c, text=c)
            self.sv_tree.column(c, anchor="center", width=120)
        self.sv_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # sự kiện click vào dòng bảng ->hiện lên ô nhâp
        self.sv_tree.bind("<<TreeviewSelect>>", self.on_select_sv)

        self.load_all_students()

    # hàm lấy dữ liệu tất cả sinh viên ( dùng store procedure sp_SinhVien_Select)
    def load_all_students(self, query=None, params=()):
        for r in self.sv_tree.get_children(): self.sv_tree.delete(r)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            if query:
                cursor.execute(query, params)
            else:
                cursor.execute("{CALL sp_SinhVien_Select}")

            for r in cursor.fetchall():
                # r[0]: MaSV, r[1]: HoTen, r[2]: NgaySinh, r[7]: TrangThai, r[8]: MaLop
                self.sv_tree.insert("", "end", values=(r[0], r[1], r[2], r[8], r[7]))
            conn.close()
        except:
            pass

    def add_sv(self):
        ma_sv = self.ent_ma.get().strip()
        ho_ten = self.ent_ten.get().strip()
        ngay_sinh = self.ent_ns.get().strip()
        ma_lop = self.ent_lop.get().strip()

        if not ma_sv or not ho_ten:
            messagebox.showwarning("Chú ý", "Vui lòng nhập Mã SV và Họ tên!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Thứ tự truyền vào: 1.Ma, 2.Ten, 3.NS, 4.GT, 5.DC, 6.Email, 7.SDT, 8.TrangThai, 9.Lop
            # Lưu ý: "0123456789" nằm ở vị trí số 7 (SDT)
            cursor.execute("{CALL sp_SinhVien_Insert (?,?,?,?,?,?,?,?,?)}",
                           (ma_sv, ho_ten, ngay_sinh, "Nam", "Hà Nội",
                            f"{ma_sv}@student.edu.vn", "0123456789", "Đang học", ma_lop))

            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã thêm sinh viên!")
            self.load_all_students()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # Xử lý khi nhấn nút xóa (gọi sp_SinhVien_Delete)
    def delete_sv(self):
        if not messagebox.askyesno("Xác nhận", "Xóa sinh viên này?"): return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("{CALL sp_SinhVien_Delete (?)}", (self.ent_ma.get(),))
            conn.commit()
            conn.close()
            self.load_all_students()
            messagebox.showinfo("Xong", "Đã xóa sinh viên khỏi hệ thống!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # Tìm kiếm sinh viên
    def search_sv(self):
        key = f"%{self.ent_search.get()}%"
        sql = "SELECT * FROM SinhVien WHERE MaSV LIKE ? OR HoTen LIKE ?"
        self.load_all_students(sql, (key, key))

    def update_sv(self):
        # 1. Lấy dữ liệu từ các ô nhập liệu (Entry)
        ma = self.ent_ma.get()
        ten = self.ent_ten.get()
        ngay_sinh = self.ent_ns.get()
        lop = self.ent_lop.get()

        # Kiểm tra nếu chưa chọn sinh viên hoặc để trống mã
        if not ma:
            messagebox.showwarning("Chú ý", "Vui lòng chọn sinh viên cần cập nhật từ bảng!")
            return

        try:
            # 2. Kết nối Database
            conn = get_connection()
            cursor = conn.cursor()

            # 3. Gọi Stored Procedure sp_SinhVien_Update
            # SP này yêu cầu 9 tham số :
            # MaSV, HoTen, NgaySinh, GioiTinh, DiaChi, Email, SoDienThoai, TrangThai, MaLop
            params = (
                ma,  # MaSV
                ten,  # HoTen
                ngay_sinh,  # NgaySinh
                "Nam",  # GioiTinh
                "Hà Nội",  # DiaChi
                "sv@cmc.edu.vn",  # Email
                "0123456789",  # SoDienThoai
                "Đang học",  # TrangThai
                lop  # MaLop
            )

            # Cú pháp gọi Stored Procedure
            cursor.execute("{CALL sp_SinhVien_Update (?,?,?,?,?,?,?,?,?)}", params)

            # 4. Xác nhận thay đổi và đóng kết nối
            conn.commit()
            conn.close()

            # 5. Thông báo thành công và load lại bảng dữ liệu
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin cho SV: {ten}")
            self.load_all_students()

        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể cập nhật dữ liệu: {e}")

    # chuc nang 3: báo cáo thống kê
        # --- CHỨC NĂNG 3: QUẢN LÝ ĐÀO TẠO (LỚP & MÔN HỌC) ---
    def show_manage_classes(self):
        """Hàm chính để hiển thị giao diện Quản lý Lớp và Môn học sử dụng Tabview"""
        self.clear_view()
        ctk.CTkLabel(self.container, text="QUẢN LÝ ĐÀO TẠO (LỚP & MÔN HỌC)",
                     font=("Arial", 24, "bold"), text_color=self.main_color).pack(pady=10)

        # Tạo Tabview để chia màn hình thành 2 phần: Quản lý Lớp và Quản lý Môn
        self.tabview_edu = ctk.CTkTabview(self.container, width=1100)
        self.tabview_edu.pack(padx=20, pady=10, fill="both", expand=True)

        tab_lop = self.tabview_edu.add("Quản lý Lớp học")
        tab_mon = self.tabview_edu.add("Môn học & Mở lớp học phần")

        # Gọi hàm vẽ giao diện cho từng Tab
        self.setup_tab_lop_view(tab_lop)
        self.setup_tab_mon_view(tab_mon)

    # --- PHẦN 1: GIAO DIỆN QUẢN LÝ LỚP HỌC
    def setup_tab_lop_view(self, parent):
        """Vẽ giao diện quản lý lớp học vào Tab 1"""
        # Khung nhập liệu cho Lớp
        f_input = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        f_input.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(f_input, text="Mã Lớp:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.ent_malop = ctk.CTkEntry(f_input)
        self.ent_malop.grid(row=0, column=1)

        ctk.CTkLabel(f_input, text="Tên Lớp:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10)
        self.ent_tenlop = ctk.CTkEntry(f_input)
        self.ent_tenlop.grid(row=0, column=3)

        # Nút bấm Thêm/Xóa lớp
        f_btns = ctk.CTkFrame(parent, fg_color="transparent")
        f_btns.pack(fill="x", padx=20)
        ctk.CTkButton(f_btns, text="THÊM LỚP", fg_color="green", width=120, command=self.add_class).pack(
            side="left", padx=5)
        ctk.CTkButton(f_btns, text="XÓA LỚP", fg_color="#e74c3c", width=120, command=self.delete_class).pack(
            side="left", padx=5)

        # Bảng hiển thị danh sách lớp
        cols = ("MaLop", "TenLop", "KhoaHoc", "MaKhoa")
        self.class_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for c in cols:
            self.class_tree.heading(c, text=c)
            self.class_tree.column(c, anchor="center")
        self.class_tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.class_tree.bind("<<TreeviewSelect>>", self.on_select_class)  # Click vào bảng hiện lên ô nhập

        self.load_classes()  # Nạp dữ liệu vào bảng lớp

    # --- PHẦN 2: GIAO DIỆN QUẢN LÝ MÔN HỌC & GIỚI HẠN LỚP ---
    def setup_tab_mon_view(self, parent):
        f_in = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        f_in.pack(fill="x", padx=20, pady=10)

        # Hàng 1: Thông tin cơ bản
        ctk.CTkLabel(f_in, text="Mã môn:").grid(row=0, column=0, padx=10, pady=10)
        self.ent_mamon = ctk.CTkEntry(f_in, width=100)
        self.ent_mamon.grid(row=0, column=1)

        ctk.CTkLabel(f_in, text="Tên môn:").grid(row=0, column=2, padx=10)
        self.ent_tenmon = ctk.CTkEntry(f_in, width=220)
        self.ent_tenmon.grid(row=0, column=3)

        ctk.CTkLabel(f_in, text="Tín chỉ:").grid(row=0, column=4, padx=10)
        self.ent_stc = ctk.CTkEntry(f_in, width=50)
        self.ent_stc.grid(row=0, column=5)

        # Hàng 2: Chọn Khoa (Để giới hạn đối tượng đăng ký)
        ctk.CTkLabel(f_in, text="Thuộc Khoa:").grid(row=1, column=0, padx=10, pady=10)
        self.cb_mon_khoa = ctk.CTkComboBox(f_in, width=200)
        self.cb_mon_khoa.grid(row=1, column=1, columnspan=2, sticky="w")

        ctk.CTkButton(parent, text="THÊM MÔN HỌC VÀO HỆ THỐNG", fg_color="#1a3a8a",
                      command=self.add_course_logic).pack(pady=10)

        # Bảng hiển thị
        cols = ("MaMon", "TenMon", "SoTinChi", "MaKhoa")
        self.mon_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for c in cols:
            self.mon_tree.heading(c, text=c)
            self.mon_tree.column(c, anchor="center")
        self.mon_tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_khoa_to_combobox()
        self.load_mon_table()

    def load_khoa_to_combobox(self):
        """Lấy danh sách các Khoa từ DB để Admin chọn"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MaKhoa, TenKhoa FROM Khoa")
            rows = cursor.fetchall()
            self.dict_khoa = {r[1]: r[0] for r in rows}  # {Tên Khoa: Mã Khoa}
            self.cb_mon_khoa.configure(values=list(self.dict_khoa.keys()))
            if rows: self.cb_mon_khoa.set(rows[0][1])
            conn.close()
        except:
            pass

    def add_course_logic(self):
        ma = self.ent_mamon.get().strip()
        ten = self.ent_tenmon.get().strip()
        stc = self.ent_stc.get().strip()
        ten_khoa = self.cb_mon_khoa.get()
        ma_khoa = self.dict_khoa.get(ten_khoa)

        if not ma or not ten:
            messagebox.showwarning("Chú ý", "Vui lòng nhập đủ thông tin!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Gọi SP thêm môn học với mã khoa đã chọn
            cursor.execute("{CALL sp_PDT_ThemMonHoc (?,?,?,?)}", (ma, ten, int(stc), ma_khoa))
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", f"Đã thêm môn {ten} thuộc khoa {ten_khoa}")
            self.load_mon_table()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    # --- CÁC HÀM XỬ LÝ NGHIỆP VỤ ---

    def load_classes_to_combobox(self):
        """Lấy danh sách các lớp hiện có trong trường để Admin chọn mở môn cho lớp đó"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT TenLop FROM Lop")
            classes = [r[0] for r in cursor.fetchall()]
            self.cb_mon_lop.configure(values=classes)
            if classes: self.cb_mon_lop.set(classes[0])  # Mặc định chọn lớp đầu tiên
            conn.close()
        except:
            pass

    def add_course_and_limit_to_class(self):
        """Thực hiện thêm môn vào Database và giới hạn môn đó cho lớp đã chọn"""
        ma = self.ent_mamon.get().strip()
        ten = self.ent_tenmon.get().strip()
        stc = self.ent_stc.get().strip()
        lop_chon = self.cb_mon_lop.get()  # Lớp được giới hạn môn này

        if not ma or not ten or not stc:
            messagebox.showwarning("Chú ý", "Vui lòng nhập đầy đủ Mã môn, Tên môn và Số tín chỉ!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # 1. Gọi Stored Procedure thêm môn học mới vào bảng MonHoc
            cursor.execute("{CALL sp_PDT_ThemMonHoc (?,?,?,?)}", (ma, ten, int(stc), "CNTT"))

            # 2. 'Giới hạn' bằng cách cập nhật môn này vào thông tin của Lớp
            # (Môn học này sẽ xuất hiện cho sinh viên lớp này đăng ký ở kỳ mới)
            cursor.execute("UPDATE Lop SET MaMon = ? WHERE TenLop = ?", (ma, lop_chon))

            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", f"Đã thêm môn {ten}\nVà mở lớp học phần cho lớp: {lop_chon}")
            self.load_mon_table()  # Cập nhật lại bảng môn học
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm môn học: {e}")

    def load_mon_table(self):
        """Hiển thị danh sách toàn bộ môn học và xem môn đó đang mở cho lớp nào"""
        for r in self.mon_tree.get_children(): self.mon_tree.delete(r)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Câu lệnh lấy môn học và tên lớp tương ứng (nếu có)
            query = """
                    SELECT m.MaMon, m.TenMon, m.SoTinChi, l.TenLop
                    FROM MonHoc m \
                             LEFT JOIN Lop l ON m.MaMon = l.MaMon \
                    """
            cursor.execute(query)
            for r in cursor.fetchall():
                self.mon_tree.insert("", "end", values=tuple(r))
            conn.close()
        except:
            pass


    def load_classes(self):
        for r in self.class_tree.get_children(): self.class_tree.delete(r)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MaLop, TenLop, KhoaHoc, MaKhoa FROM Lop")
            for r in cursor.fetchall(): self.class_tree.insert("", "end", values=tuple(r))
            conn.close()
        except:
            pass

    def add_class(self):
        ma = self.ent_malop.get().strip()
        ten = self.ent_tenlop.get().strip()
        if ma and ten:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("{CALL sp_Lop_Insert (?,?,?,?,?,?)}",
                               (ma, ten, "2024-2028", "CNTT", "Chưa có", "CMC123"))
                conn.commit()
                conn.close()
                messagebox.showinfo("Xong", f"Đã thêm lớp {ten}")
                self.load_classes()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def delete_class(self):
        sel = self.class_tree.selection()
        if sel:
            ma = self.class_tree.item(sel)['values'][0]
            if messagebox.askyesno("Xác nhận", f"Xóa lớp {ma}?"):
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("{CALL sp_Lop_Delete (?)}", (ma,))
                    conn.commit()
                    conn.close()
                    self.load_classes()
                except Exception as e:
                    messagebox.showerror("Lỗi", str(e))

    def on_select_class(self, _):
        sel = self.class_tree.selection()
        if sel:
            v = self.class_tree.item(sel)['values']
            self.ent_malop.delete(0, "end")
            self.ent_malop.insert(0, v[0])
            self.ent_tenlop.delete(0, "end")
            self.ent_tenlop.insert(0, v[1])

        # CHức năng quản lý phân công giảng dạy

    def show_assignments(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="PHÂN CÔNG GIẢNG DẠY",
                     font=("Arial", 22, "bold"), text_color=self.main_color).pack(pady=10)

        # khung nhập dữ liệu
        f_assign = ctk.CTkFrame(self.container, fg_color="white", corner_radius=15)
        f_assign.pack(fill="x", padx=20, pady=10)

        # Tạo từ điển để tra cứu Mã từ Tên
        self.dict_gv = {}
        self.dict_lop = {}
        self.dict_mon = {}

        # Hàng 1: Chọn Gv và Lớp
        ctk.CTkLabel(f_assign, text="Giảng viên:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10,
                                                                                    pady=15)
        self.cb_gv = ctk.CTkComboBox(f_assign, width=220)
        self.cb_gv.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(f_assign, text="Lớp học:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10)
        self.cb_lop = ctk.CTkComboBox(f_assign, width=180)
        self.cb_lop.grid(row=0, column=3, padx=5)

        # Hàng 2: Chọn Môn học và Nút bấm
        ctk.CTkLabel(f_assign, text="Môn học:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=15)
        self.cb_mon = ctk.CTkComboBox(f_assign, width=220)
        self.cb_mon.grid(row=1, column=1, padx=5)

        self.btn_do_assign = ctk.CTkButton(f_assign, text="XÁC NHẬN PHÂN CÔNG",
                                           fg_color="green", hover_color="#1e7e34",
                                           font=("Arial", 13, "bold"),
                                           command=self.perform_assign)
        self.btn_do_assign.grid(row=1, column=3, padx=20, pady=10)

        # 2. BẢNG HIỂN THỊ DANH SÁCH (Treeview)
        cols = ("Giảng Viên", "Lớp Học", "Môn Học")
        frame_table = tk.Frame(self.container, bg="white")
        frame_table.pack(fill="both", expand=True, padx=20, pady=10)

        self.assign_tree = ttk.Treeview(frame_table, columns=cols, show="headings")
        for c in cols:
            self.assign_tree.heading(c, text=c)
            self.assign_tree.column(c, anchor="center", width=250)
        self.assign_tree.pack(fill="both", expand=True)

        # nạp dữ liệu ban đầu
        self.load_assign_dropdowns()  # Đổ tên vào ComboBox
        self.load_assign_table()  # Đổ dữ liệu vào bảng

    def load_assign_dropdowns(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Lấy GV
            cursor.execute("SELECT MaGV, TenGV FROM GiangVien")
            self.dict_gv = {r[1]: r[0] for r in cursor.fetchall()}
            self.cb_gv.configure(values=list(self.dict_gv.keys()))
            # Lấy Lớp
            cursor.execute("SELECT MaLop, TenLop FROM Lop")
            self.dict_lop = {r[1]: r[0] for r in cursor.fetchall()}
            self.cb_lop.configure(values=list(self.dict_lop.keys()))
            # Lấy Môn
            cursor.execute("SELECT MaMon, TenMon FROM MonHoc")
            self.dict_mon = {r[1]: r[0] for r in cursor.fetchall()}
            self.cb_mon.configure(values=list(self.dict_mon.keys()))
            conn.close()
        except:
            pass

    def load_assign_table(self):
        # Xóa dữ liệu cũ trên bảng
        for r in self.assign_tree.get_children(): self.assign_tree.delete(r)
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("{CALL sp_PDT_PhanCong_Select}")
            for r in cursor.fetchall():
                self.assign_tree.insert("", "end", values=tuple(r))
            conn.close()
        except:
            pass

    def perform_assign(self):
        # Lấy tên được chọn từ giao diện
        tgv, tlp, tmh = self.cb_gv.get(), self.cb_lop.get(), self.cb_mon.get()

        # Kiểm tra xem đã chọn đủ chưa
        if not tgv or not tlp or not tmh:
            messagebox.showwarning("Chú ý", "Vui lòng chọn đầy đủ Giảng viên, Lớp và Môn!")
            return

        # Lấy Mã tương ứng từ từ điển (Dictionary)
        ma_gv = self.dict_gv.get(tgv)
        ma_lop = self.dict_lop.get(tlp)
        ma_mon = self.dict_mon.get(tmh)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Gọi SP phân công : tham số @MaGV, @MaLop, @MaMon
            cursor.execute("{CALL sp_PhanCongGiangDay (?, ?, ?)}", (ma_gv, ma_lop, ma_mon))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", f"Đã phân công {tgv} dạy lớp {tlp}")
            self.load_assign_table()  # Refresh lại bảng để thấy kết quả ngay
        except Exception as e:
            messagebox.showerror("Lỗi", f"Phân công thất bại (Có thể đã tồn tại):\n{e}")

    def show_status(self):
        self.clear_view()
        ctk.CTkLabel(self.container, text="THỐNG KÊ CHI TIẾT",
                     font=("Arial", 22, "bold"), text_color=self.main_color).pack(pady=10)

        # TabView để chia 2 loại thống kê
        tabview = ctk.CTkTabview(self.container, width=1000)
        tabview.pack(padx=20, pady=10, fill="both", expand=True)
        tab_siso = tabview.add("Sĩ số lớp học")
        tab_kq = tabview.add("Tỷ lệ Đạt/Rớt")

        # Bảng 1: Sĩ số lớp học
        cols_siso = ("Mã Lớp", "Tên Lớp", "Sĩ Số")
        tree_siso = ttk.Treeview(tab_siso, columns=cols_siso, show="headings")

        tree_siso.heading("Mã Lớp", text="Mã Lớp")
        tree_siso.column("Mã Lớp", anchor="center", width=200)  # Thêm anchor="center"

        tree_siso.heading("Tên Lớp", text="Tên Lớp")
        tree_siso.column("Tên Lớp", anchor="center", width=300)  # Thêm anchor="center"

        tree_siso.heading("Sĩ Số", text="Sĩ Số Sinh Viên")
        tree_siso.column("Sĩ Số", anchor="center", width=200)  # Thêm anchor="center"

        tree_siso.pack(fill="both", expand=True, padx=20, pady=20)

        # Bảng 2: tỷ lệ đâu/rớt
        cols_kq = ("Tên Lớp", "Số Đạt", "Số Rớt")
        tree_kq = ttk.Treeview(tab_kq, columns=cols_kq, show="headings")

        tree_kq.heading("Tên Lớp", text="Tên Lớp Học")
        tree_kq.column("Tên Lớp", anchor="center", width=300)

        tree_kq.heading("Số Đạt", text="Số SV Đạt (>=5)")
        tree_kq.column("Số Đạt", anchor="center", width=200)

        tree_kq.heading("Số Rớt", text="Số SV Rớt (<5)")
        tree_kq.column("Số Rớt", anchor="center", width=200)

        tree_kq.pack(fill="both", expand=True, padx=20, pady=20)

        # Nạp dữ liệu vào 2 bảng
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Nạp sĩ số
            cursor.execute("{CALL sp_PDT_ThongKe_SiSo}")
            for r in cursor.fetchall():
                tree_siso.insert("", "end", values=tuple(r))
            # Nạp đạt/rớt
            cursor.execute("{CALL sp_PDT_ThongKe_KetQua}")
            for r in cursor.fetchall():
                tree_kq.insert("", "end", values=tuple(r))
            conn.close()
        except:
            pass

        # Xử lý khi nhấn dòng trong bảng (tự động điền dữ liệu)

    def on_select_sv(self, _):
        sel = self.sv_tree.selection()
        if sel:
            v = self.sv_tree.item(sel)['values']
            self.ent_ma.delete(0, "end")
            self.ent_ma.insert(0, v[0])
            self.ent_ten.delete(0, "end")
            self.ent_ten.insert(0, v[1])
            self.ent_ns.delete(0, "end")
            self.ent_ns.insert(0, v[2])
            self.ent_lop.delete(0, "end")
            self.ent_lop.insert(0, v[3])

    # Xuất Excel bằng thư viện Pandas
    def export_excel(self):
        import pandas as pd
        data = [self.sv_tree.item(r)['values'] for r in self.sv_tree.get_children()]
        df = pd.DataFrame(data, columns=["Mã SV", "Họ Tên", "Ngày Sinh", "Mã Lớp", "Trạng Thái"])
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if path:
            df.to_excel(path, index=False)
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo ra file:\n{path}")

    def logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn muốn đăng xuất?"):
            self.destroy()
            import main
            main.LoginApp().mainloop()