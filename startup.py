import sqlite3

"""
This will need to be the first file executed when the project is being set up, it will handle setting up the database, 
tables and relationships, and running the aggregator function that will populate it with beginning data
"""

print('Creating database structures for Government Stock Portfolio project.')
# Establish connection/create if not already exists
conn = sqlite3.connect('gov_stock_portfolio.db')
# Create cursor object
cursor = conn.cursor()

print('Creating Representatives table.')
# Execute command to create representatives table
cursor.execute('''CREATE TABLE IF NOT EXISTS representatives 
       (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
print('Completed creating Representatives table.')

print('Creating PTR Filings table.')
# Execute command to create ptr_filings table
cursor.execute('''CREATE TABLE IF NOT EXISTS ptr_filings
       (ptr_id INTEGER PRIMARY KEY NOT NULL, rep_id INTEGER NOT NULL, date TIMESTAMP NOT NULL,
       FOREIGN KEY (rep_id) REFERENCES representatives (id))''')
print('Completed creating PTR Filings table.')

print('Creating Transactions table.')
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
        (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        ptr_id INTEGER NOT NULL,  
        asset_type TEXT NOT NULL, 
        owner TEXT, 
        asset_name TEXT NOT NULL, 
        ticker TEXT,  
        description TEXT,
        nickname TEXT, 
        type CHAR NOT NULL, 
        minimum INTEGER NOT NULL, 
        maximum INTEGER NOT NULL, 
        executed TIMESTAMP NOT NULL, 
        notified TIMESTAMP NOT NULL, 
        FOREIGN KEY(ptr_id) REFERENCES ptr_filings (ptr_id)) ''')
print('Completed creating Transactions table.')

print('**Complete**')
conn.close()
