import smtplib
import time
import imaplib
import email
import re
import serial

ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "smartalarm42" + ORG_EMAIL
FROM_PWD = "SmartAlarm42!!"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993

ARD_PORT = "/dev/ttyACM0"

ard = serial.Serial(ARD_PORT, 9600, timeout=5)

# --- bow helper funcs --- #
# from https://medium.freecodecamp.org/an-introduction-to-bag-of-words-and-how-to-code-it-in-python-for-nlp-282e87a9da04

def word_extraction(sentence):
    ignore = ['a', "the", "is"]
    words = re.sub("[^\w]", " ",  sentence).split()
    cleaned_text = [w.lower() for w in words if w not in ignore]
    return cleaned_text

def tokenize(sentences):
    words = []
    for sentence in sentences:
        w = word_extraction(sentence)
        words.extend(w)
        
    words = sorted(list(set(words)))
    return words

def disaster_type(bow):
    max_count = 0
    d_type = ""
    if "wildfire" in bow:
        if bow["wildfire"] > max_count:
            d_type = "wildfire"
            max_count = bow["wildfire"]
    elif "tornado" in bow:
        if bow["tornado"] > max_count:
            d_type = "tornado"
            max_count = bow["wildfire"]
    elif "earthquake" in bow:
        if bow["earthquake"] > max_count:
            d_type = "earthquake"
            max_count = bow["earthquake"]
    return None if d_type == "" else d_type

def generate_bow(allsentences):
    sentences = allsentences.split('.')
    return tokenize(sentences)

# --- arduino alert --- #

def alert_arduino(d_type):
    ard.write(b'a')
    print("alerted arduino")
    

# --- main func --- #

def readmail():
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(FROM_EMAIL, FROM_PWD)
    mail.select("inbox")
    _, data = mail.search(None, "All")
    #print(data)
    mail_ids = data[0]
    id_list = mail_ids.split()

    first_id =  id_list[0]
    last_id = id_list[-1]
    
    typ, data = mail.fetch(last_id, '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            #print(response_part[1])
            msg = email.message_from_string(response_part[1])
            for part in msg.walk():
                #print(part.get_content_type())
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    print(body)
                    bow = generate_bow(body)
                    if ("evacuate" in bow or "evacuation" in bow or "emergency" in bow):# and "test" not in bow:
                        d_type = disaster_type(bow)
                        alert_arduino(d_type)
                else:
                    continue
if __name__ == "__main__":
    while True:            
        readmail()
    ard.close()
