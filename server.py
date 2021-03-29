from main_func import main, date_watcher
from chatbot import ChatBot  
import sqlite3
import threading

if __name__ == "__main__":
    print('Starting....')
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select id, name, number, provider from users;"""
    cursor.execute(query)
    users = cursor.fetchall()
    email = '' # your email address
    passw = '' # your email address password
    for user in users:
        print("Creating thread for ", user[1])
        chatbot = ChatBot(user[0], email,
        passw, user[1], user[2], user[3])
        threading.Thread(target=main, args=(chatbot,)).start()
    conn.close()
    print("All user thread created")
    print("Starting date watcher thread")
    threading.Thread(target=date_watcher, args=(ChatBot,)).start()
    print("Date watcher thread started")

