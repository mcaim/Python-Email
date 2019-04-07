__author__ = 'Aidan McRitchie, mcaim@live.unc.edu, Onyen = mcaim'
'''
PROGRAM GOALS:

Read in file location from command line
Open and read file
If error in file, just terminate
Parse file line to check for 'From:' + msg => output: 'MAIL FROM:' + msg
Input 250 ok or error...if error then print 'QUIT' and terminate program
    if not error (250) then stderr the stdin
Parse file line to check for 'To:' + msg => output: 'RCPT TO:' + msg
Input 250 ok or error...if error then print 'QUIT' and terminate program
    if not error (250) then stderr the stdin
Output 'DATA'
Input 354 or error...if error then print 'QUIT' and terminate program
    if not error (354) then stderr the stdin
Then next lines until EOF or another 'From:' => store each line...if EOF reached, stdout each line
    then stdout '.' on newline, then input 250 ok or error (and error processing)
    then stdout 'QUIT' and terminate
    if 'From:' found, stdout each line then stdout '.' on new line, input 250 ok or error (and error processing)
    then repeat starting from 'From:' parse
'''

import sys
import re
import string
import argparse
import fileinput
import re
from socket import *

special_characters = '"<>()[]\\.,;:@"'
space = ' '
printset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~     "


MAIL_FROM = 'MAIL FROM:'
RCPT_TO = 'RCPT TO: '
DATA = 'DATA'
data = []



def check_250response(response):
    if len(response) < 4:
        return False
    if response[0:4] == '250 ':
        return True
    else:
        return False

def check_354response(response):
    if len(response) < 4:
        return False
    if response[0:4] == '354 ':
        return True
    else:
        return False

def setState(state):
    return state

# assume no error in file syntax but maybe some system error like if file deleted
def start():
    # python program_name.py filename
    file = sys.argv[-1]
    #file = open('./forward/jeffay@cs.unc.edu')
    file = open('{file}'.format(file=file), "r")

    # maybe better to readline() one at a time to check for blank message part?
    state = setState('mail')


    while True:
        if state == 'mail':
            line = file.readline()
            line = line[6:]
            #line = line.rstrip()
            sys.stdout.write("MAIL FROM: " + line)
            resp = sys.stdin.readline()
            sys.stderr.write(resp)
            if not check_250response(resp):
                sys.stdout.write('QUIT\n')
                sys.exit(0)
            state = 'rcpt'

        if state == 'rcpt':
            line = file.readline()
            if line[0:3] != 'To:':
                state = 'data'
            else:
                line = line[4:]
                #line = line.rstrip()
                sys.stdout.write(RCPT_TO + line)
                resp = sys.stdin.readline()
                sys.stderr.write(resp)
                if not check_250response(resp):
                    sys.stdout.write('QUIT\n')
                    sys.exit(0)
                #state = 'data'

        if state == 'data':
            sys.stdout.write('DATA\n')
            resp = sys.stdin.readline()
            sys.stderr.write(resp)
            if not check_354response(resp):
                sys.stdout.write('QUIT\n')
                sys.exit(0)
            state = 'dataread'

        if state == 'dataread':
            #line = file.readline()
            if line == '':
                sys.stdout.write(".\n")
                resp = sys.stdin.readline()
                sys.stderr.write(resp)
                sys.stdout.write('QUIT\n')
                sys.exit(0)

            if line.__len__() > 4:
                if line[0:5] == 'From:':
                    sys.stdout.write('.\n')
                    resp = sys.stdin.readline()
                    sys.stderr.write(resp)
                    if not check_250response(resp):
                        sys.stdout.write('QUIT\n')
                        sys.exit(0)
                    line = line[5:]
                    #line = line.rstrip()
                    sys.stdout.write(MAIL_FROM + line)
                    resp = sys.stdin.readline()
                    sys.stderr.write(resp)
                    if not check_250response(resp):
                        sys.stdout.write('QUIT\n')
                        sys.exit(0)
                    state = 'rcpt'
                    continue
            sys.stdout.write(line)
            line = file.readline()

#########  HW 4 stuff
def path(token,index):
    current = index

    if token[index] != '<':
        #print_error('path')
        return False

    #if mailbox is valid returns current index, else returns false
    current = mailbox(token,current+1)
    if not current:
        return False

    # checks for last part of path

    if token[current] != '>':
        #print_error('path')
        return False

    return current + 1




def mailbox(token,index):
    current = index
    #check for local part has at least 1 char
    if not localpart(token[current]):
        #print_error('char')
        return False
    # looks for more valid chars in local part
    while localpart(token[current]):
        current = current + 1

    #once the current index is not a valid char, checks to see if next index is @

    if token[current] != '@':
        #print_error('mailbox')
        return False
    current += 1

    # now looking at domain

    current = domain(token,current)

    # if some part of domain was false, return false, else return current index
    if not current:
        return False

    return True

def localpart(char):
    specials = special_characters + space
    if char in specials:
        return False
    if len(char) != len(char.encode()):
        return False
    printables = string.printable
    if not (char in printables):
        return False
    if char == '\n':
        return False
    if char == '\t':
        return False
    # apparently doesn't work in python 2
    '''if not char.isprintable():
        return False'''

    return True

def domain(token,index):
    current = index

    #check current index = letter
    if not letter(token[current]):
        #print_error('letter')
        return False
    # check next = letter/digit
    current += 1
    while letter(token[current]) or digit(token[current]):
        current += 1

    # check for ., if so, call domain again

    if token[current] == '.':
        current = domain(token,current+1)

    # if no ., return index

    return current

def letter(token):
    pattern = re.compile('^[A-Za-z]')
    if str(re.match(pattern,token)) == 'None':
        return False
    else:
        return True

def digit(token):
    pattern = re.compile('^[0-9]')
    if str(re.match(pattern,token)) == 'None':
        return False
    else:
        return True

def to_emails_parser():
    to_emails = raw_input('To:\n')
    split = to_emails.split(',')

    if len(split) > 1:
        pass
    stripped_to_emails = []
    for email in split:
        stripped_to_emails.append(email.strip(' '))
    for email in stripped_to_emails:
        email+='\n'
        if not mailbox(email,0):
            return False, 0
    return True, stripped_to_emails

def message_tosend():
    sys.stdout.write('From:\n')
    from_mail = sys.stdin.readline()
    while not mailbox(from_mail,0):
        sys.stdout.write('Invalid FROM address\n')
        from_mail = sys.stdin.readline()

    to_emails = []
    to_check, to_emails = to_emails_parser()
    while not to_check:
        sys.stdout.write("1 or more invalid email addresses\n")
        to_check, to_emails = to_emails_parser()


    sys.stdout.write('Subject:\n')
    subject = sys.stdin.readline()

    sys.stdout.write('Message:\n')
    message = ''
    line = sys.stdin.readline()
    while line != '.\n':
        message += line
        line = sys.stdin.readline()

    return from_mail, to_emails, subject, message

def read():
    line = sys.stdin.readline()
    if line == '':
        sys.exit(0)
    return line

def connect_to_server(name, port):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((name, port))
    return greeting(client_socket,name)

def greeting(client_socket,domain):
    #receive greeting
    #print(domain)

    client_socket.recv(1024)
    helo_message = 'HELO ' + domain + 'pleased to meet you' + '\n'
    #send HELO and receive 250 ack
    client_socket.send(helo_message.encode())
    nothing = client_socket.recv(1024).decode()

    return client_socket

def form_message(from_email,to_emails, subject,data):
    #MAIL FROM: mail_box
    msg = ''
    msg += 'MAIL FROM: ' + '<' + from_email.strip('\n') + '>' +'\n'
    #RCPT TO: mail_box
    for to_mail in to_emails:
        msg += 'RCPT TO: ' + '<' + to_mail + '>' + '\n'
    #FROM: mail_box
    msg += 'DATA\n'
    msg += 'From: ' + '<' + from_email.rstrip('\n') + '>' + '\n'
    #TO: mail_box
    if len(to_emails) > 1:
        to_commas = ''
        for mail in to_emails:
            to_commas += '<' + mail + '>' + ', '
        msg += 'To: ' + to_commas.strip(', ') + '\n'
    else:
        for to_mail in to_emails:
            msg += 'To: ' + '<' + to_mail + '>' + '\n'
    #SUBJECT: subject
    msg += 'Subject: ' + subject + '\n'

    #body of the message
    msg += data
    msg += '.\n'
    msg += 'QUIT'
    return msg



def quit(clientSocket):
    clientSocket.send('QUIT'.encode())
    clientSocket.close()
    sys.exit(0)

def send_mail(message,clientSocket):
    state = setState('mail')

    message_split = message.split('\n')
    message = []
    for line in message_split:
        #line += '\n'
        message.append(line)
    #count = 0
    #message.remove[-1]
    datagram = ''
    for line in message:
        if state == 'mail':
            # send MAIL FROM cmd
            if (line[0:11] != 'MAIL FROM: '):
                print('error')
                quit(clientSocket)
            mailfrom = line
            clientSocket.send(mailfrom.encode())

            reply = clientSocket.recv(1024)
            reply = reply.decode()
            #print('From Server:', reply.decode())

            if not check_250response(reply):
                quit(clientSocket)
            state = 'rcpt'
            continue


        if state == 'rcpt':
            if line[0:9] != 'RCPT TO: ':
                state = 'data'
            else:
                rcpt = line
                clientSocket.send(rcpt.encode())

                reply = clientSocket.recv(1024)
                reply = reply.decode()
               # print('From Server:', reply.decode())

                if not check_250response(reply):
                    quit(clientSocket)
                #state = 'rcpt'
                continue

        if state == 'data':
            data = line
            clientSocket.send(data.encode())

            reply = clientSocket.recv(1024)
            reply = reply.decode()
            #print('From Server:', reply.decode())

            if not check_354response(reply):
                quit(clientSocket)
            state = 'dataread'
            continue

        if state == 'dataread':
            line += '\n'
            datagram += line
            if line == '.\n':
                state = 'quit'


                clientSocket.send(datagram.encode())
                reply = clientSocket.recv(1024)
                reply = reply.decode()
               # print('From Server:', reply.decode())
                if not check_250response(reply):
                    quit(clientSocket)


        if state == 'quit':
            reply = clientSocket.recv(1024)
            reply = reply.decode()
            #print('From Server:', reply.decode())


def main():
    serverName,serverPort = sys.argv[1], int(sys.argv[2])
    from_email, to_emails, subject, data = message_tosend()
    clientSocket = connect_to_server(serverName,serverPort)
    message = form_message(from_email,to_emails, subject,data)

    send_mail(message,clientSocket)

main()

