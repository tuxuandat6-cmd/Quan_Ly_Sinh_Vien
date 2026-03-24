import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from student_gui import StudentApp
from lecturer_gui import LecturerApp
from admin_gui import PDTApp

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CMC University - Login")
        self.geometry("1000x600")
        self.configure(fg_color="#1a3a8a")


        # Khung đăng nhập bo tròn
        self.frame = ctk.CTkFrame(self, width=380, height=450, corner_radius=30, fg_color="white")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.frame, text="ĐĂNG NHẬP", font=("Arial", 26, "bold"), text_color="#1a3a8a").place(relx=0.5,
                                                                                                           rely=0.15,
                                                                                                           anchor="center")

        self.user = ctk.CTkEntry(self.frame, width=300, height=45, placeholder_text="Tài khoản", corner_radius=10)
        self.user.place(relx=0.5, rely=0.35, anchor="center")

        self.pwd = ctk.CTkEntry(self.frame, width=300, height=45, placeholder_text="Mật khẩu", show="*",
                                corner_radius=10)
        self.pwd.place(relx=0.5, rely=0.48, anchor="center")

        self.btn = ctk.CTkButton(self.frame, text="ĐĂNG NHẬP", width=300, height=45, corner_radius=10,
                                 fg_color="#1a3a8a", font=("Arial", 16, "bold"), command=self.login)
        self.btn.place(relx=0.5, rely=0.65, anchor="center")
    def login(self):
        u, p = self.user.get(), self.pwd.get()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MaVaiTro, MaSV, MaGV FROM dbo.TaiKhoan WHERE TenDangNhap=? AND MatKhau=?", (u, p))
            row = cursor.fetchone()
            conn.close()

            if row:
                role_id = row[0]
                ma_sv = row[1]
                ma_gv = row[2]
                self.destroy() # Đóng Login

                if role_id == 1:
                    StudentApp(ma_sv).mainloop()
                elif role_id == 2:
                    LecturerApp(ma_gv).mainloop()
                elif role_id == 3:
                    PDTApp().mainloop()
            else:
                messagebox.showerror("Thất bại", "Sai tài khoản hoặc mật khẩu!")
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = LoginApp()
    app.mainloop()