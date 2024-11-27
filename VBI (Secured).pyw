import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
import pymysql
from datetime import date
from tkinter.ttk import Style, Label, Button
from PIL import Image, ImageTk
from itertools import count, cycle
import math, random, smtplib


# Functions
def data_fetch(fetch_cmd):
    cur.execute(fetch_cmd)
    conn.commit()
    details = cur.fetchall()
    return details


def resource_path(relative_path):
    import os, sys

    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def loading(pur):
    global loading_win

    class ImageLabel(tk.Label):
        def load(self, im):
            if isinstance(im, str):
                im = Image.open(im)
            frames = []
            try:
                for i in count(1):
                    frames.append(ImageTk.PhotoImage(im.copy()))
                    im.seek(i)
            except EOFError:
                pass
            self.frames = cycle(frames)
            try:
                self.delay = im.info["duration"]
            except:
                self.delay = 100
            if len(frames) == 1:
                self.config(image=next(self.frames))
            else:
                self.next_frame()

        def unload(self):
            self.config(image=None)
            self.frames = None

        def next_frame(self):
            if self.frames:
                self.config(image=next(self.frames))
                self.after(self.delay, self.next_frame)

    # demo :
    loading_win = tk.Toplevel()
    loading_win.geometry("190x190+530+200")
    loading_win.config(bg="cyan")
    loading_win.title("Loading")
    lbl = ImageLabel(loading_win)
    lbl.pack()
    lbl.load(resource_path("Loading.gif"))

    if pur == "login":
        login()
    elif pur == "account_add":
        accno = int(accNo.get())
        if accno >= 1000000000 and accno <= 9999999999:
            otp_verification(new_email.get(), pur)
        else:
            messagebox.showerror(
                "Error", "Please Choose a correct ten digit Account No. "
            )
            loading_win.destroy()
    elif pur == "transact_dr":
        otp_verification(user_email.get(), pur)
    elif pur == "transact_cr":
        otp_verification(user_email.get(), pur)
    elif pur == "transact_tr":
        otp_verification(user_email.get(), pur)
    else:
        print("Hi")


def create_account():
    global top
    top = Toplevel(bg="#2E4A91")
    top.geometry("400x300+430+180")
    top.title("New Account")
    Label(
        top, text="Enter Details", justify="center", font="Century 16 bold italic"
    ).grid(row=1, column=1, pady=15, columnspan=2)
    Label(top, text="Your Name :").grid(row=2, column=1)
    Label(top, text="Your Email ID: ").grid(row=3, column=1, pady=20)
    Label(top, text="Enter Account No :\n      (10 digits)").grid(
        row=4, column=1, padx=15
    )
    # l = Label(top, text= '').grid(row=5,column=1)
    Label(top, text="Deposit Amount : \n     (Min. 10k)").grid(row=6, column=1, pady=10)
    # l = Label(top, text= '').grid(row=7,column=1)
    e_t1 = Entry(top, textvariable=cust_nm, width=21).grid(row=2, column=2)
    e_t2 = Entry(top, textvariable=new_email, width=21).grid(row=3, column=2)
    e_t3 = Spinbox(top, from_=1000000000, to=9999999999, textvariable=accNo).grid(
        row=4, column=2
    )
    e_t4 = Spinbox(top, textvariable=new_bal, from_=10000, to=1000000000).grid(
        row=6, column=2
    )
    Button(top, text="Create", command=lambda: [loading("account_add")]).grid(
        row=7, column=1, columnspan=2, pady=10
    )


def account_add():
    accno = int(accNo.get())
    cust_name = cust_nm.get()
    bal = new_bal.get()
    email = new_email.get()

    try:
        no = data_fetch("select serial from Accounts order by serial desc")
        no = int(no[0][0]) + 1
        cmd = "insert into Accounts values({},{},'{}','{}','{}',{})".format(
            no, accno, cust_name, email, date.today(), bal
        )
        cur.execute(cmd)
        conn.commit()

        dot, amt, mode = date.today(), bal, "CR"
        i_bal, f_bal = 0, bal

        no = data_fetch("select serial from Transactions order by serial desc")
        no = int(no[0][0]) + 1
        cmd = 'insert into Transactions values ({},"{}",{},{},"{}",{},{})'.format(
            no, dot, accno, amt, mode, i_bal, f_bal
        )
        # print(cmd)
        cur.execute(cmd)
        conn.commit()

        cmd = 'update Accounts set bal=bal+{} where name="Admin"'.format(amt)
        cur.execute(cmd)
        conn.commit()
        top.destroy()
        loading_win.destroy()
        messagebox.showinfo("Success", "Account Created Successfully!!!")
        email_send(email, 3)
    except pymysql.err.IntegrityError:
        messagebox.showerror("Error", "Please Choose a different Account No.")


def admin_shortcut():
    acc.set("5490816372")
    nm.set("Admin")
    loading("login")


def sample_shortcut():
    acc.set("1" + ("0" * 9))
    nm.set("Hi")
    loading("login")


def personal_shortcut():
    acc.set("1" + ("0" * 7) + "26")
    nm.set("Vishesh")
    loading("login")


def login():
    check_acc = int(acc.get())
    if check_acc == 5490:
        check_acc = 5490816372
        acc.set("5490816372")
    check_name = nm.get()
    accounts_data = data_fetch(" Select name,AccNo,Email from Accounts")
    global admin_stat

    for data in accounts_data:
        if check_acc == int(data[1]) and check_name == data[0]:
            user_email.set(data[2])
            print(data[2])
            l2.config(text="    Hello, {} ".format(check_name))
            l25.config(text=check_name)
            l26.config(text=check_acc)
            bal = data_fetch(
                "select Bal from Accounts where AccNo={}".format(check_acc)
            )
            doa = data_fetch(
                "select DAO from Accounts where AccNo={}".format(check_acc)
            )
            # print(bal)
            l27.config(text=f"{int(bal[0][0]):,}")
            l28.config(text=doa)
            l21.grid(row=2, column=1, padx=35)
            l22.grid(row=3, column=1, pady=15)
            l23.grid(row=4, column=1)
            l25.grid(row=2, column=2, columnspan=2)
            l26.grid(row=3, column=2, columnspan=2)
            l27.grid(row=4, column=2, columnspan=2)
            l24.grid(row=5, column=1, pady=10, padx=20)
            l28.grid(row=5, column=2, columnspan=2)
            b21.grid(row=6, column=1, pady=30)
            b22.grid(row=6, column=2)
            b23.grid(row=6, column=3, padx=50)
            if check_name == "Admin":
                b21.grid_forget()
                b22.grid_forget()
                b23.grid_forget()
                open_treeview("")
                but_admin.grid(row=8, column=2, columnspan=3, pady=20, ipadx=2)
                admin_stat = 1
            else:
                open_treeview("where t.accNo={}".format(check_acc))
                if admin_stat == 1:
                    but_admin.grid_forget()
                    admin_stat = 0
            loading_win.destroy()
            messagebox.showinfo("Success", "Login Successful!")
            break
    else:
        messagebox.showerror(
            "Error",
            "Your Name is not registered with this Account No. !!! \nCheck your details \nor \nKindly Open a New Account \n",
        )


def transact(mode):
    global top
    top = Toplevel(bg="#243665")
    top.geometry("400x300+430+180")
    top.config(bg="#2E4A91")
    top.title("New Transaction")
    ttk.Label(top, text="Enter Details", justify="center", font="Georgia 20").place(
        x=130, y=5
    )

    if mode == "C":  # CREDIT
        Label(top, text="Deposit Amount :").place(x=10, y=50)
        Label(top, text="(Min. 100)").place(x=20, y=75)

        Spinbox(top, textvariable=transact_bal, from_=100, to=1000000000).place(
            x=150, y=50
        )
        Button(top, text="DEPOSIT", command=lambda: loading("transact_cr")).place(
            x=150, y=230
        )

    elif mode == "D":  # DEBIT
        Label(top, text="Withdrawal Amount :").place(x=10, y=50)
        Label(top, text="(Min. 100)").place(x=20, y=75)

        Spinbox(
            top, textvariable=transact_bal, from_=100, to=1000000000, width=18
        ).place(x=180, y=50)
        Button(top, text="WITHDRAW", command=lambda: loading("transact_dr")).place(
            x=150, y=230
        )

    elif mode == "T":
        Label(top, text="Recipient's AccNo :").place(x=10, y=50)
        Label(top, text="Transfer Amount :").place(x=10, y=100)

        Spinbox(
            top, from_=1000000000, to=9999999999, textvariable=rc_acc, width=20
        ).place(x=150, y=50)
        Spinbox(top, textvariable=tr_amt, from_=100, to=1000000000).place(x=150, y=100)

        Button(top, text="Transfer", command=lambda: loading("transact_tr")).place(
            x=150, y=200
        )

    else:
        print("error")


def transfer():
    RcAcc, TrAmt = rc_acc.get(), tr_amt.get()
    org_acc = int(acc.get())
    accounts_data = data_fetch(" Select name,AccNo from Accounts")
    for data_accNos in accounts_data:
        if RcAcc == int(data_accNos[1]) and RcAcc != org_acc:
            no = len(data_fetch("select serial from Transactions")) + 1

            i_bal = data_fetch(
                "select Bal from Accounts where AccNo={}".format(org_acc)
            )
            int_bal_org = i_bal[0][0]

            i_bal = data_fetch("select Bal from Accounts where AccNo={}".format(RcAcc))
            int_bal_rc = i_bal[0][0]

            # Sender-DEBIT HERE-ORIGNAL
            cmd = "update Accounts set bal=bal-{} where accNo={}".format(TrAmt, org_acc)
            cur.execute(cmd)
            conn.commit()
            # Reciptient-CREDIT HERE
            cmd = "update Accounts set bal=bal+{} where accNo={}".format(TrAmt, RcAcc)
            cur.execute(cmd)
            conn.commit()

            # Final Balences
            final_bal_org = data_fetch(
                "select Bal from Accounts where AccNo={}".format(org_acc)
            )[0][0]
            final_bal_rc = data_fetch(
                "select Bal from Accounts where AccNo={}".format(RcAcc)
            )[0][0]

            cmd = 'insert into Transactions values ({},"{}",{},{},"{}",{},{})'.format(
                no, date.today(), org_acc, TrAmt, "TDR", int_bal_org, final_bal_org
            )
            cur.execute(cmd)
            conn.commit()
            cmd = 'insert into Transactions values ({},"{}",{},{},"{}",{},{})'.format(
                no + 1, date.today(), RcAcc, TrAmt, "TCR", int_bal_rc, final_bal_rc
            )
            cur.execute(cmd)
            conn.commit()

            l27.config(text=final_bal_org)
            if nm.get() == "Admin":
                cmd = ""
            else:
                cmd = "where t.accNo={}".format(acc.get())
            open_treeview(cmd)
            top.destroy()
            loading_win.destroy()
            messagebox.showinfo("Success", "Transaction Complete!")
            email_send(user_email.get(), 2, "Transfer")
            break
        elif RcAcc == org_acc:
            loading_win.destroy()
            messagebox.showerror(
                "Error",
                "Please Note: \nYour own account can't be same as the Reciptient. ",
            )
            break
    else:
        loading_win.destroy()
        messagebox.showerror(
            "Error",
            "The aforementioned account doesn't belong to our bank. Please remember the Recptient must be from our bank. \n Thank You ",
        )


def bal_update(type, mode):
    bal = transact_bal.get()
    no = data_fetch("select serial from Transactions")
    no = len(no) + 1
    i_bal = data_fetch("select Bal from Accounts where AccNo={}".format(acc.get()))
    int_bal = i_bal[0][0]

    cmd = 'update Accounts set bal=bal{}{} where name="Admin"'.format(type, bal)
    cur.execute(cmd)
    conn.commit()

    cmd = "update Accounts set bal=bal{}{} where accNo={}".format(type, bal, acc.get())
    cur.execute(cmd)
    conn.commit()

    final_bal = data_fetch("select Bal from Accounts where AccNo={}".format(acc.get()))[
        0
    ][0]
    cmd = 'insert into Transactions values ({},"{}",{},{},"{}",{},{})'.format(
        no, date.today(), acc.get(), bal, mode, int_bal, final_bal
    )
    cur.execute(cmd)
    conn.commit()

    l27.config(text=final_bal)
    if nm.get() == "Admin":
        cmd = ""
    else:
        cmd = "where t.accNo={}".format(acc.get())
    open_treeview(cmd)
    top.destroy()
    loading_win.destroy()
    messagebox.showinfo("Success", "Transaction Complete!")
    email_send(user_email.get(), 2, mode, bal=final_bal, amt=bal)


def open_treeview(command):
    treev.pack(side="left", fill="both")
    scroll_bar = Scrollbar(frame3, command=treev.yview, orient="vertical")
    scroll_bar.pack(side="right", fill="y", ipady=40, ipadx=20)
    treev.config(yscrollcommand=scroll_bar.set)
    l3.config(text="Your Transactions: ")

    for item in treev.get_children():
        treev.delete(item)

    transact_data = data_fetch(
        "select t.Serial, Name, t.AccNo, DOT,t.Amt, Mode, Int_Bal, Final_Bal from Accounts a JOIN Transactions t on a.accno=t.accno {} order by t.serial asc".format(
            command
        )
    )

    a = 1
    for i in transact_data:

        # print(i[2])
        treev.insert(
            "",
            "end",
            values=(a, i[1], i[2], i[3], f"{i[4]:,}", i[5], f"{i[6]:,}", f"{i[7]:,}"),
        )
        a += 1


def accounts_view():
    top = Toplevel()
    top.geometry("550x300")
    top.title("All Accounts and Profiles")
    top.config(bg="cyan")
    tk.Label(
        top,
        text="All User Accounts:",
        justify="center",
        font="Century 16 bold italic",
        bg="cyan",
    ).pack(ipady=10)
    treeve = ttk.Treeview(top, selectmode="browse")
    treeve.pack()
    # verscrlbar = ttk.Scrollbar(frame3,orient ="vertical",command = treev.xview)
    # verscrlbar.pack(side ='right', fill ='y')
    # treev.configure(xscrollcommand = verscrlbar.set)
    treeve["columns"] = ("1", "2", "3", "4", "5", "6")
    treeve["show"] = "headings"
    treeve.column("1", width=30, anchor="center")
    treeve.column("2", width=80, anchor="center")
    treeve.column("3", width=90, anchor="w")
    treeve.column("4", width=190, anchor="center")
    treeve.column("5", width=80 - 7, anchor="center")
    treeve.column("6", width=60 + 7, anchor="center")
    treeve.heading("1", text="Sr.")
    treeve.heading("2", text="Account No.")
    treeve.heading("3", text="Name")
    treeve.heading("4", text="Email")
    treeve.heading("5", text="DOA")
    treeve.heading("6", text="Balence")
    acc_data = data_fetch("select * from Accounts order by serial")
    # print(acc_data)
    for i in acc_data:
        treeve.insert("", "end", values=(i[0], i[1], i[2], i[3], i[4], f"{i[5]:,}"))


def settings():
    import contextlib
    import io

    win = Tk()
    win.title("Console")
    win.geometry("415x475")
    win.config(bg="cyan", relief="raised")

    win.option_add("*font", "georgia 12 ")

    def prin():
        output_stream = io.StringIO()

        with contextlib.redirect_stdout(output_stream):
            try:
                exec(e1.get("1.0", "end-1c"))
            except Exception as e:
                print(str(e).title() + ".")

        a = output_stream.getvalue()
        if a == "":
            a = "Success."
        e2.delete("1.0", END)
        e2.insert(END, a)

    l = tk.Label(
        win,
        text="Debug Console",
        font="georgia 18 bold italic",
        justify=CENTER,
        bg="cyan",
    )
    l.grid(row=0, column=1)
    e1 = Text(win, width=40, height=15)
    e1.grid(row=2, column=1, padx=5)
    e1.insert(END, "#Enter Python Program here. \n\n")
    b1 = tk.Button(win, text="Execute", command=prin)
    b1.grid(row=3, column=1, pady=5)
    la = tk.Label(win, text="Output:", bg="cyan")
    la.grid(row=4, column=1)
    e2 = Text(win, width=40, height=5)
    e2.grid(row=5, column=1, padx=5)
    win.mainloop()


def email_send(email_id, pur, sub_pur="", bal=0, amt=0):
    name = nm.get() if sub_pur != "account_add" else cust_nm.get()
    bal_msg = "" if sub_pur != "account_add" else f" of Rs.{amt:,}"
    if pur == 1:
        msg = f"""From:  VBI VirtualBankofIndia@gmail.com
Subject: Your One-Time Password for a Seamless Experience
Dear {name},

To proceed with your {d[sub_pur]}{bal_msg}, please use the unique One-Time Password mentioned below:

OTP: {OTP}\n
This code is crafted for your exclusive use. If this action was not intended, you may simply disregard this message.\n
Thank you for allowing us to be part of your journey.\n
Warm regards,
VBI"""

    elif pur == 2:
        msg = f"""From:  VBI VirtualBankofIndia@gmail.com
Subject: Transaction Confirmation
Dear {name},

Your {d[sub_pur]} of Rs.{amt:,} has been successfully processed.\n
Updated Balance: Rs.{bal:,}\n
We are grateful for the opportunity to serve you, and we look forward to your continued journey with us.\n
Yours faithfully,
VBI """

    elif pur == 3:
        msg = f"""From:  VBI VirtualBankofIndia@gmail.com
Subject: Welcome Aboard
Dear {cust_nm.get()},

With your account now established, a world of secure and sophisticated banking opens before you.

As you begin this journey with us, may your path be paved with effortless transactions and peace of mind. We are delighted to be a part of your aspirations.

Thank you for your trust.

Warmly,
VBI"""

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login("virtualbankofIndia@gmail.com", "origyhytrxaalaxl")
    s.sendmail("&&&&&&&&&&&", email_id, msg)


def otp_verification(email_id, purpose):
    global OTP

    # OTP Generation
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]

    def verify_otp():
        a = otp_entry.get()
        if a == OTP:
            messagebox.showinfo("Success", "Successfully Verified!")
            top1.destroy()
            if purpose == "account_add":
                account_add()
            elif purpose == "transact_dr":
                bal_update("-", "DR")
            elif purpose == "transact_cr":
                bal_update("+", "CR")
            elif purpose == "transact_tr":
                transfer()
            else:
                print("Why")
        else:
            messagebox.showerror("Error", " Please Check your OTP again.")

    # Hi
    if purpose == "account_add":
        amt = 0
    elif purpose == "transact_dr" or purpose == "transact_cr":
        amt = transact_bal.get()
    elif purpose == "transact_tr":
        amt = tr_amt.get()
    print("OTP Process")
    email_send(email_id, 1, purpose, amt=amt)
    top1 = Toplevel()
    top1.geometry("300x150")
    top1.title("Verification")
    top1.config(bg="cyan")
    l = tk.Label(
        top1,
        text="Enter your OTP:",
        justify="center",
        font="Century 16 ",
        bg="cyan",
        foreground="#A020F0",
    )
    l.place(x=60, y=15)

    otp_entry = Entry(top1, width=20)
    otp_entry.place(x=50, y=60)
    verify_but = tk.Button(
        top1, text="Verify", command=verify_otp, bg="cyan", fg="#A020F0"
    )
    verify_but.place(x=60, y=100 - 5)

    def appear():
        otp_resend = tk.Button(
            top1,
            text="Resend OTP",
            bg="cyan",
            fg="#A020F0",
            command=lambda: email_send(email_id, 1, purpose),
        )
        otp_resend.place(x=135, y=95)

    from threading import Timer

    t = Timer(10.0, appear)
    t.start()


def Calc():
    win = tk.Toplevel()
    win.title("Calculator")
    win.configure(bg="cyan")

    input_var = StringVar()

    def equal():
        try:
            input_var.set(str(eval(input_var.get())))

        except ZeroDivisionError:
            messagebox.showinfo("Import Notice", "Can't divide by zero")

        except SyntaxError:
            messagebox.showerror("Error", "Please write correctly")

        except TclError:
            messagebox.showerror("Error", "Error")

        else:
            print("no error")

    def clear():
        input_var.set("")

    def click(item):
        input_var.set(input_var.get() + str(item))

    dis_frame = Frame(
        win, width=100, height=50, highlightthickness=1, highlightcolor="Grey"
    )
    dis_frame.pack(side=TOP, padx=5, pady=5)

    dis_box = Entry(dis_frame, width=20, textvariable=input_var, justify=RIGHT)
    dis_box.pack(ipady=1)

    but_frame = Frame(win)
    but_frame.pack(side=BOTTOM, pady=5, padx=5)

    b1 = tk.Button(
        but_frame, text="1", width=5, height=2, cursor="hand2", command=lambda: click(1)
    ).grid(row=1, column=0, padx=1, pady=1)

    b2 = tk.Button(
        but_frame, text="2", width=5, height=2, cursor="hand2", command=lambda: click(2)
    ).grid(row=1, column=1, padx=1, pady=1)

    b3 = tk.Button(
        but_frame, text="3", width=5, height=2, cursor="hand2", command=lambda: click(3)
    ).grid(row=1, column=2, padx=1, pady=1)

    b4 = tk.Button(
        but_frame, text="4", width=5, height=2, cursor="hand2", command=lambda: click(4)
    ).grid(row=2, column=0, padx=1, pady=1)

    b5 = tk.Button(
        but_frame, text="5", width=5, height=2, cursor="hand2", command=lambda: click(5)
    ).grid(row=2, column=1, padx=1, pady=1)

    b6 = tk.Button(
        but_frame, text="6", width=5, height=2, cursor="hand2", command=lambda: click(6)
    ).grid(row=2, column=2, padx=1, pady=1)

    b7 = tk.Button(
        but_frame, text="7", width=5, height=2, cursor="hand2", command=lambda: click(7)
    ).grid(row=3, column=0, padx=1, pady=1)

    b8 = tk.Button(
        but_frame, text="8", width=5, height=2, cursor="hand2", command=lambda: click(8)
    ).grid(row=3, column=1, padx=1, pady=1)

    b9 = tk.Button(
        but_frame, text="9", width=5, height=2, cursor="hand2", command=lambda: click(9)
    ).grid(row=3, column=2, padx=1, pady=1)

    b0 = tk.Button(
        but_frame, text="0", width=5, height=2, cursor="hand2", command=lambda: click(0)
    ).grid(row=4, column=1, padx=1, pady=1)

    bclear = tk.Button(
        but_frame,
        text="C",
        width=5,
        height=2,
        cursor="hand2",
        command=lambda: input_var.set(""),
    ).grid(row=4, column=0, padx=1, pady=1)

    bequal = tk.Button(
        but_frame, text="=", width=5, height=2, cursor="hand2", command=lambda: equal()
    ).grid(row=4, column=2, padx=1, pady=1)

    bplus = tk.Button(
        but_frame,
        text="+",
        width=5,
        height=2,
        cursor="hand2",
        command=lambda: click("+"),
    ).grid(row=1, column=3, padx=1, pady=1)

    bsubract = tk.Button(
        but_frame,
        text="-",
        width=5,
        height=2,
        cursor="hand2",
        command=lambda: click("-"),
    ).grid(row=2, column=3, padx=1, pady=1)

    bmultiply = tk.Button(
        but_frame,
        text="x",
        width=5,
        height=2,
        cursor="hand2",
        command=lambda: click("*"),
    ).grid(row=3, column=3, padx=1, pady=1)

    bdivide = tk.Button(
        but_frame,
        text="÷",
        width=5,
        height=2,
        cursor="hand2",
        command=lambda: click("/"),
    ).grid(row=4, column=3, padx=1, pady=1)

    # win.mainloop()


def emi_cal():
    # Dictionary of loan purposes and their respective annual interest rates
    interest_rates = {
        "Home Loan": 7.0,
        "Car Loan": 8.5,
        "Personal Loan": 12.0,
        "Education Loan": 6.5,
        "Other": None,  # Placeholder for custom purpose and rate
    }

    # Function to calculate EMI
    def calculate_emi():
        try:
            principal = float(principal_entry.get())
            tenure = int(tenure_entry.get()) * 12  # Loan tenure in months

            # Get the selected loan purpose and corresponding rate
            purpose = purpose_var.get()
            if purpose == "Other":
                # Use the custom interest rate entered by the user
                rate = float(custom_rate_entry.get()) / 12 / 100
            else:
                rate = interest_rates[purpose] / 12 / 100  # Monthly interest rate

            # EMI formula
            emi = principal * rate * (1 + rate) ** tenure / ((1 + rate) ** tenure - 1)

            # Display result
            emi_result.config(text=f"Monthly EMI: ₹{emi:.2f}")
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter valid numbers for all fields."
            )

    # Show/hide custom purpose and rate entry based on loan purpose
    def update_custom_fields(*args):
        if purpose_var.get() == "Other":
            custom_purpose_label.pack(pady=5)
            custom_purpose_entry.pack(pady=5)
            custom_rate_label.pack(pady=5)
            custom_rate_entry.pack(pady=5)
        else:
            custom_purpose_label.pack_forget()
            custom_purpose_entry.pack_forget()
            custom_rate_label.pack_forget()
            custom_rate_entry.pack_forget()

    # Setting up the Tkinter window
    root = tk.Tk()
    root.title("EMI Calculator")
    root.geometry("300x300")
    root.configure(bg="#2E4A91")  # Set background color

    # Define widget styling
    label_fg = "#FFFFFF"  # White color for labels
    entry_bg = "#FFFFFF"  # White background for entry fields
    button_bg = "#1C3557"  # Darker shade for button background
    button_fg = "#FFFFFF"  # White text on button

    # Principal amount input
    tk.Label(root, text="Principal Amount (₹):", fg=label_fg, bg="#2E4A91").pack(pady=5)
    principal_entry = tk.Entry(root, bg=entry_bg)
    principal_entry.pack(pady=5)

    # Purpose dropdown menu
    tk.Label(root, text="Purpose of Loan:", fg=label_fg, bg="#2E4A91").pack(pady=5)
    purpose_var = tk.StringVar(root)
    purpose_var.set("Select Purpose")  # Default option
    purpose_menu = tk.OptionMenu(root, purpose_var, *interest_rates.keys())
    purpose_menu.config(bg=button_bg, fg=button_fg)
    purpose_menu.pack(pady=5)
    purpose_var.trace("w", update_custom_fields)  # Trace changes to purpose selection

    # Custom purpose and interest rate for "Other" option
    custom_purpose_label = tk.Label(
        root, text="Custom Loan Purpose:", fg=label_fg, bg="#2E4A91"
    )
    custom_purpose_entry = tk.Entry(root, bg=entry_bg)
    custom_rate_label = tk.Label(
        root, text="Custom Interest Rate (% per annum):", fg=label_fg, bg="#2E4A91"
    )
    custom_rate_entry = tk.Entry(root, bg=entry_bg)

    # Tenure input
    tk.Label(root, text="Loan Tenure (years):", fg=label_fg, bg="#2E4A91").pack(pady=5)
    tenure_entry = tk.Entry(root, bg=entry_bg)
    tenure_entry.pack(pady=5)

    # Calculate button
    calculate_button = tk.Button(
        root, text="Calculate EMI", command=calculate_emi, bg=button_bg, fg=button_fg
    )
    calculate_button.pack(pady=10)

    # Result display
    emi_result = tk.Label(
        root, text="Monthly EMI: ₹0.00", font=("Arial", 14), fg=label_fg, bg="#2E4A91"
    )
    emi_result.pack(pady=10)

    # Run the application
    root.mainloop()


# root window
root = tk.Tk()
root.geometry("600x400+320+120")
root.title("VBI-Managment Software")
root.resizable(False, False)
root.option_add("*font", "Georgia 12 ")
root.config(bg="cyan", relief="raised")


# MySQL connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="vishesh14",
    database="bank",
)
cur = conn.cursor()

# create a notebook
notebook = ttk.Notebook(root, height=380, width=580)
notebook.pack(pady=10, expand=True)

# Varibles
acc = StringVar()
nm = StringVar()
accNo = StringVar()
cust_nm = StringVar()
new_bal = IntVar()
frame3_message = StringVar()
transact_bal = IntVar()
new_email = StringVar()
admin_stat = 0
rc_acc = IntVar()
tr_amt = IntVar()
user_email = StringVar()
d = {
    "account_add": "Account Opening",
    "transact_dr": "Withdrawal",
    "transact_cr": "Deposit",
    "transact_tr": "Transfer",
    "CR": "Deposit",
    "DR": "Withdrawal",
    "Transfer": "Transfer",
}


style = Style()
style.theme_use("default")
style.configure(
    "TButton",
    highlightcolor="gold",
    foreground="#A020F0",
    background="cyan",
    font="Times",
)
style.configure(
    "TSpinbox", height=20, highlightthickness=10, highlightcolor="gold", fg="cyan"
)
style.configure("TNotebook", background="cyan")
style.configure("TLabel", background="#2E4A91", foreground="cyan")
style.configure("TNotebook.Tab", background="#8AAAE5")
style.configure("Treeview", font="Century 10", border="cyan", width=560)
style.map(
    "TNotebook.Tab",
    foreground=[("active", "!background", "red"), ("selected", "cyan")],
    background=[("selected", "#A020F0")],
)

image_icon = PhotoImage(file=resource_path("Icon.png"))
root.iconphoto(False, image_icon)

# loan()
# create frames
frame0 = Frame(notebook, width=580, height=380)
frame1 = Frame(frame0, width=580, height=380, bg="#2E4A91")
frame1.pack(anchor="center")
frame2 = Frame(notebook, width=580, height=380, bg="#2E4A91")
frame3 = Frame(notebook, width=580, height=380, bg="#2E4A91", padx=10, pady=10)
frame1.pack(fill="both")
frame2.pack(fill="both")
frame3.pack(fill="both")

# add frames to notebook
notebook.add(frame0, text="Welcome")
notebook.add(frame2, text="Profile")
notebook.add(frame3, text="Past Transactions")

# Frame-1
l1 = tk.Label(
    frame1,
    text="Welcome",
    font="Georgia 20 bold italic underline ",
    bg="#2E4A91",
    foreground="cyan",
    justify="center",
)
l1.place(x=350, y=20)

l11 = Label(frame1, text="Registered Name :").place(x=120 + 130, y=80)
l12 = Label(frame1, text="Account Number : ").place(x=120 + 130, y=130)
e1 = Entry(frame1, textvariable=nm, width=15).place(x=270 + 120, y=80)
e2 = Spinbox(frame1, from_=1000000000, to=9999999999, textvariable=acc, width=14).place(
    x=270 + 120, y=130
)

submit = Button(frame1, text="Submit", command=lambda: loading("login"))
submit.place(x=275 + 80, y=180)

l = Label(frame1, text="Don't have an account yet. Open one, Now!")
l.place(x=240, y=280)
acc_cr = Button(frame1, text="Open Account", command=create_account).place(x=240, y=310)

image2 = Image.open(resource_path("Picture2.png")).resize((220, 341))
img2 = ImageTk.PhotoImage(image2)
label2 = tk.Label(frame1, image=img2, bg="cyan").place(x=5, y=5)

image = Image.open(resource_path("settings.png")).resize((30, 30))
img = ImageTk.PhotoImage(image)
tk.Button(frame1, image=img, bg="cyan", command=settings).place(x=550 - 10, y=345 - 30)

image24 = Image.open(resource_path("cal3.png")).resize((30, 30))
img24 = ImageTk.PhotoImage(image24)
tk.Button(frame1, image=img24, bg="cyan", command=Calc).place(x=500, y=315)

# Frame-2
l2 = Label(
    frame2,
    text="\t Life is worthless.",
    font="Georgia 17 italic bold",
    justify="center",
)
l2.grid(row=1, column=1, columnspan=2, padx=20, pady=15)

image55 = Image.open(resource_path("Icon.png")).resize((60, 60))
img55 = ImageTk.PhotoImage(image55)
label5 = tk.Label(frame2, image=img55, bg="#2E4A91")
label5.place(x=2, y=2)

l21 = Label(frame2, text="Registered Name :")
l22 = Label(frame2, text="Account Number : ")
l23 = Label(frame2, text="Current Balence : ")
l24 = Label(frame2, text="Date of Account Opening : ")
l25 = Label(frame2)
l26 = Label(frame2)
l27 = Label(frame2)
l28 = Label(frame2)

b21 = Button(frame2, text="Deposit Money", command=lambda: transact("C"))  # CREDIT
b22 = Button(frame2, text="Withdraw Money", command=lambda: transact("D"))  # DEBIT
b23 = Button(frame2, text="Bank Transfer", command=lambda: transact("T"))  # DEBIT

but_admin = Button(frame2, text="Check all Users ", command=accounts_view)

l3 = Label(frame3, text="Past is forgotten", font="Georgia 17 italic bold")
l3.pack(side="top", ipady=5)

image5 = Image.open(resource_path("Icon.png")).resize((55, 55))
img5 = ImageTk.PhotoImage(image5)
label6 = tk.Label(frame3, image=img5, bg="#2E4A91").place(x=-2, y=-5)

l = Label(frame3).pack()
treev = ttk.Treeview(frame3, selectmode="browse", height=13)

treev["columns"] = ("1", "2", "3", "4", "5", "6", "7", "8")
treev["show"] = "headings"
treev.column("1", width=40 - 5, anchor="center")
treev.column("2", width=80 - 10, anchor="w")
treev.column("3", width=90, anchor="center")
treev.column("4", width=90 - 15, anchor="center")
treev.column("5", width=60 + 20, anchor="center")
treev.column("6", width=60 - 5, anchor="center")
treev.column("7", width=60 + 5, anchor="center")
treev.column("8", width=60 + 10, anchor="center")
treev.heading("1", text="Serial")
treev.heading("2", text="Name")
treev.heading("3", text="Account No")
treev.heading("4", text="DOT")
treev.heading("5", text="Amount")
treev.heading("6", text="Mode")
treev.heading("7", text="Prev. Bal")
treev.heading("8", text="Final Bal")

root.bind("<Return>", lambda event: login(), add="+")
root.bind("<Control-a><KeyPress-d>", lambda event: admin_shortcut())
root.bind("<Control-a><KeyPress-s>", lambda event: sample_shortcut())
root.bind("<Control-a><KeyPress-v>", lambda event: personal_shortcut())

root.mainloop()
