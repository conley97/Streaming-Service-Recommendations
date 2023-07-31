import io

import pandas as pd
import sqlite3
import pickle

class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.login_status = False
        self.watchlist = []

        # Connect to the database
        con = sqlite3.connect('userDB.db')
        c = con.cursor()

        # Check if the username exists in the database
        c.execute("SELECT password, watchlist FROM user WHERE username = ?", (self.username,))
        db_user = c.fetchone()
        if db_user is not None:
            # If the username exists, check if the password matches
            db_pass = db_user[0]
            if db_pass == self.password:
                print('Login successful')
                self.login_status = True
                # If the password matches, set the watchlist to the watchlist from the database
                watchlist_file = io.BytesIO(db_user[1])

                # Load the watchlist from the file-like object
                self.watchlist = pickle.load(watchlist_file)
            else:
                print('Login failed: password did not match database')
        else:
            # If the username does not exist, insert a new user into the database
            watchlist_bytes = pickle.dumps(self.watchlist)
            c.execute("INSERT INTO user (username, password, watchlist) VALUES (?, ?, ?)",
                      (self.username, self.password, watchlist_bytes))
            con.commit()
            print('New profile created. Welcome!')
            self.login_status = True

        # Close the connection to the database
        con.close()

    def getLoginStatus(self):
        return self.login_status

    def append_watchlist(self, api_id, name):
        # Check if the new entry already exists in the watchlist
        if [api_id, name] not in self.watchlist:
            # Append the new entry to the watchlist
            self.watchlist.append([api_id, name])

            # Connect to the database
            con = sqlite3.connect('userDB.db')
            c = con.cursor()

            # Update the watchlist in the database
            watchlist_bytes = pickle.dumps(self.watchlist)
            c.execute("UPDATE user SET watchlist = ? WHERE username = ?", (watchlist_bytes, self.username))
            con.commit()

            # Close the connection to the database
            con.close()

        print(self.watchlist)

    def get_watchlist(self):
        # Check if the new entry already exists in the watchlist
        return self.watchlist

