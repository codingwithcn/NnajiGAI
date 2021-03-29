from collections import Counter
from cj_fun import preprocess, compare_overlap, pos_tag, extract_nouns, compute_similarity
import spacy
import re
import sqlite3
import os
import smtplib, ssl
import random
from email.mime.text import MIMEText
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from datetime import timedelta
import datetime

class ChatBot:
    end = False
    def __init__(self, user_id, email, password, name, only_num, provider):
        self.word2vec = spacy.load('en_core_web_sm')
        self.exit_commands = ('Program End Password: Legacy')
        self.commands = open('cj_commands.text', 'r', encoding='utf-8').readlines()
        self.user_message = ''
        self.entity = ''
        self.blank_spots = ["Nothing"

        ]
        self.name = name
        self.user_id = user_id
        self.email = email
        self.password =password
        self.only_num= only_num
        self.provider = provider
        self.num_complete = self.only_num + self.provider
        self.responses = ["I can {}", "Show groceries", "Add to groceries:", "Delete from groceries:"]
        

    # define .make_exit() below:
    def make_exit(self, user_message):
        self.user_message = user_message
        if self.exit_commands == self.user_message:
            self.end = True
            ChatBot.end = True
            return True
        return False
        # define .chat() below:

    def chat(self, user_message, text):
        self.user_message = user_message
        if not self.make_exit(self.user_message):
            self.user_message = self.respond(self.user_message, text)
            return self.user_message
        return 'Alright sir have a good day'

    # define .find_intent_match() below:
    def find_intent_match(self, responses, user_message):
        result = Counter(preprocess(user_message))
        respon = [Counter(preprocess(response)) for response in responses]
        similarity_list = [compare_overlap(result, res) for res in respon]
        return responses[similarity_list.index(max(similarity_list))]

    # define .find_entities() below:
    def find_entities(self, user_message):
        tag = pos_tag(preprocess(user_message))
        print('tag', tag)
        nouns = extract_nouns(tag)
        print('nouns', nouns)
        tokens = self.word2vec(' '.join(nouns))
        category = self.word2vec(" ".join(self.blank_spots))
        word2vec_result = compute_similarity(tokens, category)
        word2vec_result.sort(key=lambda x: x[2])
        if word2vec_result:
            return word2vec_result[-1][0]
        return self.blank_spots

    # define .respond() below:
    def respond(self, user_message, text):
        best_response = self.find_intent_match(self.responses, user_message)
        response = self.make_connection(best_response, user_message, text)
        return response

    def command(self):
        return random.choice(self.commands)

    def send_email(self, subject, message, email, emailer, emailer_pass):
        port = 587  # For starttls
        smtp_server = "smtp.mail.me.com"
        sender_email = emailer
        receiver_email = email
        password = emailer_pass
        messages = MIMEMultipart()
        messages['From'] = sender_email
        messages['To'] = receiver_email
        messages['Subject'] = subject
        messages['Bcc'] = receiver_email
        messages.attach(MIMEText(message, 'plain'))
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, messages.as_string())

    # Sending a text
    def send_text(self, subject, emailer, emailer_pass, number, number_provider, bod):
        email = emailer
        pas = emailer_pass
        sms_gateway = number
        sms_gateway = sms_gateway + number_provider #'@tmomail.net'
        smtp = 'smtp.mail.me.com'
        port = 587
        server = smtplib.SMTP(smtp, port)
        server.starttls()
        server.login(email, pas)
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = sms_gateway
        msg['Subject'] = subject
        body = bod
        msg.attach(MIMEText(body, 'plain'))
        sms = msg.as_string()
        server.sendmail(email, sms_gateway, sms)
        server.quit()

    def get_grocery_date(self):
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
                    
    def make_connection(self, best, user_message, text):
        if best == "I can {}":
            return self.command()
        elif best == "Show groceries":
            time_span = self.get_grocery_date()
            query = """select name, item_name from grocceries 
            join groccery_weeks on groccery_week = groccery_weeks.id
            join users on user_who_added = users.id
            join items on item = items.id
            where date = "{}";""".format(time_span)
            conn = sqlite3.connect("server.db")
            cursor = conn.cursor()
            cursor.execute(query)
            infor = cursor.fetchall()
            reply = ''
            for i in infor:
                reply += i[0] +" wants "+ i[1]+'\n'
            print(reply)
            conn.close()
            return "List of this weeks groceries:\n\t"+reply
        elif best == "Add to groceries:":
            today = datetime.date.today()
            # dd/mm/YY
            d1 = today.strftime("%d %m %Y")
            output = re.split(r'add to groceries:', user_message.lower())
            print(output)
            query = """insert into items (item_name, picture, who_added, date_item_created) values ('{}', 'none',{}, "{}");""".format(output[1], self.user_id, d1)
            print(query)
            conn = sqlite3.connect("server.db")
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            query = """select id from items where date_item_created = "{}" and who_added={}""".format(d1, self.user_id)
            conn = sqlite3.connect("server.db")
            cursor = conn.cursor()
            cursor.execute(query)
            ids = cursor.fetchone()[0]
            time_span = self.get_grocery_date()
            query = """select id from groccery_weeks where date = "{}" """.format(time_span)
            cursor.execute(query)
            go_ids = cursor.fetchone()[0]
            query = """insert into grocceries (groccery_week, user_who_added, item) values ({},{},{});""".format(
                go_ids, self.user_id, ids
            )
            cursor.execute(query)
            conn.commit()
            conn.close()
            return  output[1] +" successfully added to this week groccery list"

        elif best == "Delete from groceries:":
            today = datetime.date.today()
            # dd/mm/YY
            d1 = today.strftime("%d %m %Y")
            output = re.split(r'delete from groceries:',user_message.lower())
            query = """select id from items where item_name="{}" """.format(output[1])
            conn = sqlite3.connect("server.db")
            cursor = conn.cursor()
            cursor.execute(query)
            ids = cursor.fetchone()[0]
            query="""DELETE from grocceries 
            where item= {} and user_who_added={}""".format(ids, self.user_id)
            conn = sqlite3.connect("server.db")
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return output[1] +" successfully deleted from this week groccery list"

