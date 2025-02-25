from datetime import datetime
import json
import sqlite3


class Searcher:
    """ A Python class to search an SQLite database based on a JSON file structure """

    def __init__(self):
        self.db_file_path = './data/contacts.db'
        self.table_name = 'contacts'
        self.json_file_path = './data/contacts.json'
        self.column_names = self.get_column_names()

    def basic_logger(self, message):
        """ Logs messages to a text file """
        with open('searcher_log.txt', 'a') as f:
            f.write(message + '\n')

    def create_table(self):
        """ Checks and creates (if needed) the table in the db """
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()
            cursor.execute(f"select name from sqlite_master where name = '{self.table_name}'")
            result = cursor.fetchone()
            
            if result is None:
                data_json = json.load(open(self.json_file_path))
                for row in data_json:
                    age = datetime.now().year - datetime.fromisoformat(row['birthday']).year
                    row['age'] = str(age)

                data_list = [list(row.values()) for row in data_json]
                column_names = list(data_json[0].keys())

                create_table_sql = f"create table {self.table_name} ({', '.join(f'{name} TEXT' for name in column_names)})"
                cursor.execute(create_table_sql)
                conn.commit()

                placeholders = ', '.join(['?'] * len(column_names)) 
                insert_data_sql = f"insert into {self.table_name} ({', '.join(column_names)}) values ({placeholders})"

                cursor.executemany(insert_data_sql, data_list)
                conn.commit()
                
            conn.close()
            return True
        
        except sqlite3.Error as e:
            conn.close()
            msg = f"Error creating table: {e}"
            self.basic_logger(msg)
            return False            

    def get_column_names(self):
        """ Retrieves column names from the table """
        if self.create_table():
            try:
                conn = sqlite3.connect(self.db_file_path)
                cursor = conn.cursor()
                cursor.execute(f"pragma table_info({self.table_name})")
                columns = [row[1] for row in cursor.fetchall()]  
                conn.close()
                return columns
            except sqlite3.Error as e:
                msg = f"Error retrieving column names from database: {e}"
                self.basic_logger(msg)
                return []

    def search_contacts(self, search_criteria):
        """ Searches the database based on the provided search criteria """

        if not self.column_names:
            msg = "Error: No column names available. Cannot perform search"
            self.basic_logger(msg)
            return []

        # Remove whitespceas from the values, plus filter out empty values
        clean_search_criteria = {k: v.strip() for k, v in search_criteria.items() if len(v) > 0}

        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()

        where_clauses = []
        for column, value in clean_search_criteria.items():\
        
            if column in self.column_names:
                where_clauses.append(f"{column} like '%{value}%'")

            else:
                msg = f"Warning: Column '{column}' not found in the table. Ignoring this criteria"
                self.basic_logger(msg)
                return []

        if not where_clauses:
            msg = "Warning: No valid search criteria provided. Returning all rows."
            self.basic_logger(msg)
            return []
        
        else:
            where_clause = " or ".join(where_clauses)
            sql = f"select * from {self.table_name} where {where_clause}"
            print(sql)

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.close()

            contacts = [dict(zip(self.column_names, row)) for row in results]
            return contacts
        
        except sqlite3.Error as e:
            msg = f"Error executing search query: {e}"
            self.basic_logger(msg)
            conn.close()
            return []
        

if __name__ == "__main__":
    # d = {'name': 'Lou Gardner', 'age': '', 'phone_number': '(052) 5851056', 'address': ''}
    # searcher = Searcher()
    # contacts = searcher.search_contacts(d)
    # import pandas as pd
    # df = pd.DataFrame(contacts)
    # df['picture'] = df['picture'].apply(lambda picture: f'<img src="./assets/images/{picture}" width="60">')
    # print(df)
    pass