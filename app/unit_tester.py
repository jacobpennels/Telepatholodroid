import unittest
from app import database_connector, user
import sqlite3

class DatabaseTest(unittest.TestCase):

    def test_access(self):
        filename = 'test_database.db'
        db = database_connector.DatabaseConnector(filename)
        self.assertEqual(type(db.c), sqlite3.Cursor)
        db.close()

    def test_execute(self):
        filename='test_database.db'
        db = database_connector.DatabaseConnector(filename)
        try:
            db.execute_statement("drop table test")
        except sqlite3.OperationalError:
            pass
        db.execute_statement("create table test (cola text, colb text, colc text)")
        db.execute_statement("insert into test values ('hi', 'hello', 'goodbye')")
        rows = db.execute_query("select * from test")
        self.assertEqual(len(rows), 1)
        for row in rows:
            self.assertEqual(row[0], "hi")
            self.assertEqual(row[1], "hello")
            self.assertEqual(row[2], "goodbye")
        db.execute_statement("drop table test")
        db.close()

    def test_script(self):
        filename = 'test_database.db'
        db = database_connector.DatabaseConnector(filename)
        db.run_script('schema.sql')
        db.execute_statement("INSERT INTO users VALUES ('dr', 'bob', 'smith', 'b@dr.com', '10-10-2017', 'hospital', 'US', 'abc123', NULL )")
        rows = db.execute_query("SELECT * FROM users WHERE(title=?)", "dr")
        self.assertEqual(len(rows), 1)
        for row in rows:
            self.assertEqual(row[0], "dr")
            self.assertEqual(row[2], "smith")
        db.close()

    def test_get_user_by_id(self):
        filename= 'test_database.db'
        db = database_connector.DatabaseConnector(filename)
        db.run_script('schema.sql')
        db.run_script('populate_database.sql')
        user = db.get_user_by_id(1)
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.fname, "Bob")
        self.assertEqual(user.email, "bsmith@dr.com")
        self.assertEqual(user.title, "Dr")
        db.close()

    def test_log_user_in(self):
        filename='test_database.db'
        db = database_connector.DatabaseConnector(filename)
        db.run_script('schema.sql')
        db.run_script('populate_database.sql')
        user_email = "bsmith@dr.com"
        user_pword = "abc123"
        self.assertTrue(db.log_user_in(user_email, user_pword))
        self.assertFalse(db.log_user_in(user_email, "abc1234"))


if __name__ == '__main__':
    unittest.main()