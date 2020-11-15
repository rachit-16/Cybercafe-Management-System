import sqlite3
import datetime
import calendar


class Base:
    name = "Name"
    email = "Email"
    phone = "ContactNo"
    password = "Password"


class Date:
    join_date = "JoinDate"
    join_day = "JoinDay"

    def findDay(self, date):
        day = datetime.datetime.strptime(date, '%d/%m/%Y').weekday()
        return calendar.day_name[day]


class User(Base, Date):
    duration = "MembershipPeriod"
    balance = "Balance"
    security = "Security"

    def __init__(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        table_string = f'''CREATE TABLE IF NOT EXISTS Users(
                        {self.email} TEXT PRIMARY KEY,
                        {self.name} TEXT,
                        {self.phone} TEXT,
                        {self.password} TEXT,
                        {self.join_date} TEXT,
                        {self.join_day} TEXT,
                        {self.duration} TEXT,
                        {self.security} TEXT,
                        {self.balance} TEXT)'''
        cur.execute(table_string)
        dbase.commit()
        dbase.close()

    def insert_data(self, vals):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()

        date = vals["Join Date"].get()
        day = self.findDay(date)
        sec_deposit = {"0 months": "20", "1 month": "2000", "3 months": "5000", "6 months": "9500", "12 months": "18000"}
        sec_dep = sec_deposit[vals["Membership"].get()]

        cur.execute(''' INSERT INTO Users
                    (Email, Name, ContactNo, Password, JoinDate, JoinDay, MembershipPeriod, Security, Balance)
                    VALUES(?,?,?,?,?,?,?,?,?) ''',
                    (vals["Email"].get(), vals["Name"].get(), vals["Contact Number"].get(), vals["Password"].get(),
                     date, day, vals["Membership"].get(), sec_dep, sec_dep)
                    )

        dbase.commit()
        dbase.close()

    def search_data(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''SELECT * FROM Users WHERE Email=?''', (email,))
        rows = cur.fetchall()
        dbase.close()
        return rows

    def check_data(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''SELECT Name FROM Users WHERE Email=?''', (email, ))
        rows = cur.fetchall()
        dbase.close()
        return rows

    def view_data(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute(''' SELECT * FROM Users ''')
        rows = cur.fetchall()
        dbase.close()
        return rows

    def update_data(self, email, vals):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''UPDATE Users SET Name=?, ContactNo=?, Password=? WHERE Email=?''',
                    (vals["Name"].get(), vals["Contact Number"].get(), vals["Password"].get(), email))
        dbase.commit()
        dbase.close()

    def delete_data(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''DELETE FROM Users WHERE Email=?''', (email,))
        dbase.commit()
        dbase.close()

    def delete_all_data(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''DELETE FROM Users''')
        dbase.commit()
        dbase.close()

    def check_balance(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()

        cur.execute(''' SELECT Balance FROM Users WHERE Email=?''', (email,))
        data = cur.fetchall()
        balance = int(data[0][0])

        dbase.commit()
        dbase.close()
        return balance

    def deduct_fees(self, email, fees):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()

        balance = self.check_balance(email)
        balance -= fees

        cur.execute('''UPDATE Users SET Balance=? WHERE Email=?''',
                    (str(balance), email))
        dbase.commit()
        dbase.close()
        return balance


class Staff(Base, Date):
    salary = "Salary"

    def __init__(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        table_string = f'''CREATE TABLE IF NOT EXISTS Staff(
                        {self.email} TEXT PRIMARY KEY,
                        {self.name} TEXT,
                        {self.phone} TEXT,
                        {self.password} TEXT,
                        {self.join_date} TEXT,
                        {self.join_day} TEXT,
                        {self.salary} TEXT)'''
        cur.execute(table_string)
        dbase.commit()
        dbase.close()

    def insert_data(self, vals):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()

        date = vals["Join Date"].get()
        day = self.findDay(date)

        cur.execute(''' INSERT INTO Staff
                    (Email, Name, ContactNo, Password, JoinDate, JoinDay, Salary)
                    VALUES(?,?,?,?,?,?,?) ''',
                    (vals["Email"].get(), vals["Name"].get(), vals["Contact Number"].get(), vals["Password"].get(),
                     date, day, vals["Salary"].get()))

        dbase.commit()
        dbase.close()

    def search_data(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute(''' SELECT * FROM Staff WHERE Email=?''', (email, ))
        rows = cur.fetchall()
        dbase.close()
        return rows

    def check_data(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''SELECT Name FROM Staff WHERE Email=?''', (email, ))
        rows = cur.fetchall()
        dbase.close()
        return rows

    def view_data(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute(''' SELECT * FROM Staff ''')
        rows = cur.fetchall()
        dbase.close()
        return rows

    def update_data(self, email, vals):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''UPDATE Staff SET Name=?, ContactNo=?, Password=?, Salary=? WHERE Email=?''',
                    (vals["Name"].get(), vals["Contact Number"].get(), vals["Password"].get(), vals["Salary"].get(), email))
        dbase.commit()
        dbase.close()

    def delete_data(self, email):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''DELETE FROM Staff WHERE Email=?''', (email,))
        dbase.commit()
        dbase.close()

    def delete_all_data(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''DELETE FROM Staff''')
        dbase.commit()
        dbase.close()


class Machine(Date):
    model = "ModelNo"
    item = "Item"
    brand = "Brand"
    price = "Price"
    warranty = "Warranty"

    def __init__(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        table_string = f'''CREATE TABLE IF NOT EXISTS Machine(
                        {self.model} TEXT PRIMARY KEY,
                        {self.item} TEXT,
                        {self.brand} TEXT,
                        {self.price} TEXT,
                        {self.warranty} TEXT,
                        {self.join_date} TEXT,
                        {self.join_day} TEXT)'''
        cur.execute(table_string)
        dbase.commit()
        dbase.close()

    def insert_data(self, vals):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()

        date = vals["Buy Date"].get()
        day = self.findDay(date)

        cur.execute(''' INSERT INTO Machine
                    (ModelNo, Item, Brand, Price, Warranty, JoinDate, JoinDay) 
                    VALUES(?,?,?,?,?,?,?) ''',
                    (vals["Model"].get(), vals["Item"].get(), vals["Brand"].get(), vals["Price"].get(), vals["Warranty"].get(),
                     date, day))
        dbase.commit()
        dbase.close()

    def search_data(self, model):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute(''' SELECT * FROM Machine WHERE ModelNo=?''', (model,))
        rows = cur.fetchall()
        dbase.close()
        return rows

    def check_data(self, model):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''SELECT ModelNo FROM Machine WHERE ModelNo=?''', (model,))
        rows = cur.fetchall()
        dbase.close()
        return rows

    def view_data(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute(''' SELECT * FROM Machine ''')
        rows = cur.fetchall()
        dbase.close()
        return rows

    def update_data(self, model, vals):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()

        cur.execute(''' SELECT Price, Warranty, JoinDate, JoinDay FROM Machine WHERE ModelNo=?''',
                    (model, ))

        prev_data = cur.fetchall()
        price, warranty, date, day = prev_data[0]

        date1 = vals['Buy Date'].get()
        day1 = self.findDay(date1)

        price = f"{price}+{vals['Price'].get()}"
        warranty = f"{warranty}+{vals['Warranty'].get()}"
        date = f"{date}--{date1}"
        day = f"{day}+{day1}"

        cur.execute('''UPDATE Machine SET Price=?, Warranty=?, JoinDate=?, JoinDay=? WHERE ModelNo=?''',
                    (price, warranty, date, day, model))
        print(model, prev_data, type(prev_data))
        print(price, warranty, date, day)
        dbase.commit()
        dbase.close()

    def delete_data(self, model):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''DELETE FROM Machine WHERE ModelNo=?''', (model,))
        dbase.commit()
        dbase.close()

    def delete_all_data(self):
        dbase = sqlite3.connect('Our_data.db')
        cur = dbase.cursor()
        cur.execute('''DELETE FROM Machine''')
        dbase.commit()
        dbase.close()
