import sqlite3 as lite
import sys

class Database():
    def __init__(self, database, debug=False):
        # We initate the database connection
        self.connection = None
        self.debug = debug
        try:
            self.database = database
            self.connection = lite.connect(database)
            self.cursor = self.connection.cursor()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
        self.errMsg = ""

    def create(self):
        # Temporary function to allow me to create a dummy table
        if (self.table == None): self.table = "Signs"
        self.cursor.execute("DROP TABLE IF EXISTS ?;", self.table)
        self.cursor.execute("CREATE TABLE ? (Id INT, EngRepr TEXT, Data TEXT)",
            self.table)
        self.cursor.execute("INSERT INTO Signs VALUES(1, 'hello', 52642)")
        self.cursor.execute("INSERT INTO Signs VALUES(2, 'how', 57127)")
        self.cursor.execute("INSERT INTO Signs VALUES(3, 'are', 9000)")
        self.cursor.execute("INSERT INTO Signs VALUES(4, 'you', 29000)")
        self.cursor.execute("INSERT INTO Signs VALUES(5, 'today', 350000)")
        self.cursor.execute("INSERT INTO Signs VALUES(6, 'my', 21000)")
        self.cursor.execute("INSERT INTO Signs VALUES(7, 'name', 41400)")
        self.cursor.execute("INSERT INTO Signs VALUES(8, 'is', 21600)")

    def initDB(self, tablesDict):
        # Checks if tables declared in tablesDict exist. If they do not, we
        # create them according to the fields list mapped to that table.
        # Mapping format: <table name>: [(<field1 name>, <field1 type>), ...]
        for table, fields in tablesDict.iteritems():
            query = "SELECT name FROM sqlite_master WHERE type='table' AND \
            name=?;"
            self.cursor.execute(query, (table,))
            result = self.cursor.fetchall()
            if (len(result) == 0):
                query = "CREATE TABLE %s ("
                fieldsSQL = []
                for i in xrange(len(fields)):
                    separator = ", " if (i != 0) else ""
                    query += separator+"%s"
                    fieldsSQL.append(str(fields[i][0])+" "+str(fields[i][1]))
                query += ")"
                self.cursor.execute(query % tuple([table]+fieldsSQL))
        self.connection.commit()

    def query(self, query):
        # Generic query. No return.
        self.cursor.execute(query)
        self.connection.commit()

    def get(self, cols, table, where=None):
        # Get the columns in cols list from table
        query = 'SELECT %s FROM %s'
        if (where != None):
            query += " WHERE "
            for i in xrange(len(where)):
                separator = " AND " if (i != 0) else ""
                query += separator+where[i]
        if self.debug: print query % (str.join(',', cols), table)
        self.result = self.cursor.execute(query % (str.join(',', cols), table))
        dataList = self.cursor.fetchall()
        result = []
        for data in dataList:
            result.append(data)
        self.connection.commit()
        return result

    def store(self, table, values):
        # Store data in table
        dataSQL = ""
        #for i in xrange(len(fields)):
        #    separator = ", " if (i != 0) else ""
        #    fieldsSQL += separator+"'"+str(fields[i])+"'"
        for i in xrange(len(values)):
            separator = ", " if (i != 0) else ""
            dataSQL += separator+"'"+str(values[i])+"'"
        query = "INSERT INTO %s VALUES(%s);" % (table, dataSQL)
        result = self.cursor.execute(query)
        self.connection.commit()
        if (result != []):
            return True
        else:
            self.errMsg = "Failed. Don't know why."
            return False


    def close(self):
        # Closes the connection.
        if self.connection:
            self.connection.close()
