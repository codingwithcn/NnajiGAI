from imap_client import ImapClient
import datetime
from datetime import timedelta
import sqlite3
import time
def main(helper):
    print(helper.name + " email: "+ helper.email)
    while helper.end == False:
        time.sleep(20)
        """
        You will need to store your email password in your environment, e.g.
        export mailpwd=password
        """
        imap = ImapClient(recipient=helper.email, server='imap.mail.me.com')
        try:
            imap.login(helper.password)
            # retrieve messages from a given sender
            messages = imap.get_messages(sender=helper.num_complete)
            # Do something with the messages
            recents =  []
            if messages != None:
                for msg in messages:
                    print(msg)
                    # msg is a dict of {'num': num, 'body': body}
                    recents.append(msg['body'])
                    # you could delete them after viewing
                    imap.delete_message(msg['num'])
                # when done, you should log out
                message = " ".join(recents)
                print(helper.name + " message", recents)
                stuff = ''
                reply = helper.chat(message, stuff)
                print("Computer reply", reply)
                if message != '':
                    helper.send_text('Robot Assitant', helper.email, helper.password, helper.only_num, helper.provider, reply)
            imap.logout()
            del imap
        except Exception as e:
            print(e)
            print("Problem with client thread for", helper.name)
            helper.send_text('Robot Assitant', helper.email, helper.password, helper.only_num, helper.provider, e)
            del imap

def get_grocery_date():
        today = datetime.date.today()
        # dd/mm/YY
        d1 = today.strftime("%d %m %Y")
        date_string = ''
        operation = {'Monday':[0, 6], 'Tuesday':[-1, 5], 'Wednesday':[-2, 4], 'Thursday':[-3,3], 'Friday':[-4, 2], 'Saturday':[-5, 1],'Sunday':[-6, 0]}
        day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
        day = datetime.datetime.strptime(d1, '%d %m %Y').weekday()
        for i in operation:
            if i == day_name[day]:
                print(i)
                # Getting Mondays date
                monday_date = date = datetime.datetime.strptime(d1, '%d %m %Y')
                monday_date = monday_date + timedelta(days=operation[i][0])
                monday_date = datetime.datetime.strftime(monday_date, '%d %m %Y')
                # Setting Sunday date
                sunday_date = date = datetime.datetime.strptime(d1, '%d %m %Y') + timedelta(days=operation[i][1])
                sunday_date = datetime.datetime.strftime(sunday_date, '%d %m %Y')
                print("Date time span", monday_date, '-', sunday_date)
                date_string = monday_date + ' - '+sunday_date
                return date_string
def grab_dates():
        time_line = get_grocery_date()
        query = """select date from groccery_weeks 
        where date = "{}" """.format(time_line)
        print(query)
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        try:
            dates = cursor.fetchone()[0]
        except Exception as e:
            print(e)
            dates = None
        conn.close()
        return dates
def add_dates():
    time_line = get_grocery_date()
    query = """insert into groccery_weeks (date) values ("{}");""".format(time_line)
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()
def date_watcher(Chat):
    while Chat.end == False:
        time.sleep(6)
        dates = grab_dates()
        if dates == None:
            query = """select id from groccery_weeks;"""
            conn = sqlite3.connect('server.db')
            cursor = conn.cursor()
            cursor.execute(query)
            ids =  cursor.fetchall()[-1]
            print(ids)
            query = """select name, item_name from grocceries 
            join users on user_who_added = users.id
            join items on item = items.id
            join groccery_weeks on groccery_week = groccery_weeks.id
            where groccery_weeks.id={};""".format(ids[0])
            cursor.execute(query)
            infor =cursor.fetchall()
            reply = ''
            for i in infor:
                reply += i[0] +" wants "+ i[1]+'\n'
            statement = "Reminder to get the following grocceries this week:\n\t"+ reply
            email = '' # your email
            passw = '' # your password
            name ='' # name, it could be anything
            number=''# your number
            provider_server = '' # your provider server yours is @mymetropcs.com if you use metropcs
            Chat(None, email,
                passw, name, number, provider
            ).send_text('Robot Assitant', email, passw, 
            number, provider, statement)
            print("Its a new week adding a new date")
            add_dates()