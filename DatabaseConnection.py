import pyodbc

SERVER = 'DESKTOP-57DHS0S'
database = "News"
userName = "sa"
password = '123456'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={database};UID={userName};PWD={password}'


class Database:
    def init(self):
        self.connection = pyodbc.connect(connectionString)
        self.cursor = self.connection.cursor()

    def db_execute(self, query):

        if "SELECT" in query:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        try:
            self.cursor.execute(query)
            self.connection.commit()
            return
        except Exception as e:
            print(e)

    def db_close(self):
        self.connection.close()
