__author__ = 'Aidan McRitchie, mcaim@live.unc.edu, Onyen = mcaim'


import re
import sys
import string
#import _curses.ascii
from socket import *

special_characters = '"<>()[]\\.,;:@"'
space = ' '
printset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~     "


syntax_501 = '501 Syntax error in parameters or arguments'
syntax_500 = '500 Syntax error: command unrecognized'
syntax_503 = '503 Bad sequence of commands'
ok = '250 ok'
data_ok = '354 Start mail input; end with <CRLF>.<CRLF>'

def mailfromcmd(line_list, line):
    if line_list[0] != 'M':
        return False
    elif line_list[1] != 'A':
        return False
    elif line_list[2] != 'I':
        return False
    elif line_list[3] != 'L':
        return False


    if (whitespace(line_list[4]) == False):
        return

    i = 4
    while whitespace(line_list[i]):
        i = i+1

    if line_list[i] != 'F':
        return
    else:
        i = i+1
    if line_list[i] != 'R':
        return
    else:
        i = i+1
    if line_list[i] != 'O':
        return
    else:
        i = i+1
    if line_list[i] != 'M':
        return
    else:
        i = i+1
    if line_list[i] != ':':
        return
    else:
        i = i+1

    while nullspace(line_list[i]):
        i = i+1

    # returns false or the index if true
    current_index = rvspath(line_list, i)
    if not current_index:
        return

    if line_list[current_index] == '\n':
        return line[i+1:current_index - 1]

    nullindex = current_index
    #finds any nullspace after
    while nullspace(line_list[nullindex]):
        nullindex = nullindex + 1

    if line_list[nullindex] != '\n':
        #print_error('CLRF')
        return False
    #print('250 ok')
    return line[i+1:current_index-1]

def rcpttocmd(line_list, line):
    line_list = list(line)
    if line_list[0] != 'R':
        return False
    elif line_list[1] != 'C':
        return False
    elif line_list[2] != 'P':
        return False
    elif line_list[3] != 'T':
        return False

    if (whitespace(line_list[4]) == False):
        return False

    i = 4
    while whitespace(line_list[i]):
        i = i + 1

    if line_list[i] != 'T':
        return False
    else:
        i = i + 1
    if line_list[i] != 'O':
        return False
    else:
        i = i + 1
    if line_list[i] != ':':
        return False
    else:
        i = i+1

    while nullspace(line_list[i]):
        i = i+1

    # returns false or the index if true
    current_index = rvspath(line_list, i)
    if not current_index:
        return

    if line_list[current_index] == '\n':
        return line[i + 1:current_index - 1]

    nullindex = current_index
    # finds any nullspace after
    while nullspace(line_list[nullindex]):
        nullindex = nullindex + 1

    if line_list[nullindex] != '\n':
        # print_error('CLRF')
        return False
    # print('250 ok')
    return line[i + 1:current_index - 1]

def datacmd(line_list,line):
    line_list = list(line)
    if line_list[0] != 'D':
        return False
    elif line_list[1] != 'A':
        return False
    elif line_list[2] != 'T':
        return False
    elif line_list[3] != 'A':
        return False

    i = 4

    if nullspace(line_list[4]):
        while nullspace(line_list[i]):
            i = i + 1
    elif line_list[4] != '\n':
        print('500 Syntax error: command unrecognized')
        return False

    #while nullspace(line_list[i]):
    #    i = i+1

    if line_list[i] == '\n':
        return True
    else:
        print('501 Syntax error in parameters or arguments')
        return False




def whitespace(token):
    if sp(token):
        return True
    else:
        return False

def sp(token):
    if token == ' ' or token == '\t':
        return True
    else:
        return False

def nullspace(token):
    if null(token) or whitespace(token):
        return True
    else:
        return False

def null(token):
    if token == '':
        return True
    else:
        return False

def rvspath(token,index):
    # if path true, return index, else return false
    return path(token,index)
    #can't have error here

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

    return current

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

def print_error(error):
    print('ERROR -- '+error)


def parse():
    for line in sys.stdin:
        if line =='':
            break

        line_list = list(line)
        if '\n' in line:
            sys.stdout.write(line)
            mailfromcmd(line_list,line)
        else:
            break

def mailcommand(line):
    line_list = list(line)
    if line_list[0] != 'M':
        return False
    elif line_list[1] != 'A':
        return False
    elif line_list[2] != 'I':
        return False
    elif line_list[3] != 'L':
        return False


    if (whitespace(line_list[4]) == False):
        return False

    i = 4
    while whitespace(line_list[i]):
        i = i+1

    if line_list[i] != 'F':
        return False
    else:
        i = i+1
    if line_list[i] != 'R':
        return False
    else:
        i = i+1
    if line_list[i] != 'O':
        return False
    else:
        i = i+1
    if line_list[i] != 'M':
        return False
    else:
        i = i+1
    if line_list[i] != ':':
        return False
    else:
        return True

def rcptcommand(line):
    line_list = list(line)
    if line_list[0] != 'R':
        return False
    elif line_list[1] != 'C':
        return False
    elif line_list[2] != 'P':
        return False
    elif line_list[3] != 'T':
        return False
    if (whitespace(line_list[4]) == False):
        return False

    i = 4
    while whitespace(line_list[i]):
        i = i + 1
    if line_list[i] != 'T':
        return False
    else:
        i = i + 1
    if line_list[i] != 'O':
        return False
    else:
        i = i + 1
    if line_list[i] != ':':
        return False
    else:
        return True

def datacommand(line):
    line_list = list(line)
    if line_list[0] != 'D':
        return False
    elif line_list[1] != 'A':
        return False
    elif line_list[2] != 'T':
        return False
    elif line_list[3] != 'A':
        return False
    else:
        return True

def testrcpt():
    line = read()
    line_list = list(line)

    sys.stdout.write(line)
    print(rcptcommand(line))

# waiting for valid mail command
def waitformail(connectionSocket):
    # state starts in mail from
    state = 'mail from'
    while True:
        line = connectionSocket.recv(1024).decode() + '\n'
        if line == 'QUIT\n':
            quit_resp = '221 classroom.cs.unc.edu'
            connectionSocket.send(quit_resp.encode())
            connectionSocket.close()
            #start_restart(get_serverSocket())
        line_list = list(line)
        #print(line_list)

        #sys.stdout.write(line)

        if not mailcommand(line):
            if rcptcommand(line):
                connectionSocket.send(syntax_503.encode())
                continue
            elif datacommand(line):
                connectionSocket.send(syntax_503.encode())
                continue
            else:
                connectionSocket.send(syntax_500.encode())
                continue

        if not mailfromcmd(line_list,line):
            connectionSocket.send(syntax_501.encode())
        else:
            connectionSocket.send(ok.encode())
            break
    return True,mailfromcmd(line_list,line)

def waitforrcpt(connectionSocket):
    while True:
        line = connectionSocket.recv(1024).decode() + '\n'
        if line == 'QUIT\n':
            quit_resp = '221 classroom.cs.unc.edu'
            connectionSocket.send(quit_resp.encode())
            connectionSocket.close()
            #start_restart(get_serverSocket())
        line_list = list(line)

        if not rcptcommand(line):
            if mailcommand(line):
                connectionSocket.send(syntax_503.encode())
                continue
            elif datacommand(line):
                connectionSocket.send(syntax_503.encode())
                continue
            else:
                connectionSocket.send(syntax_500.encode())
                continue

        if not rcpttocmd(line_list,line):
            connectionSocket.send(syntax_501.encode())
        else:
            connectionSocket.send(ok.encode())
            break
    return True,rcpttocmd(line_list,line)

def socket_keeper():
    return socket

def waitforrcptordata(connectionSocket):
    data_or_rcpt = ''
    while True:
        line = connectionSocket.recv(1024).decode() + '\n'
        if line == 'QUIT\n':
            quit_resp = '221 classroom.cs.unc.edu'
            connectionSocket.send(quit_resp.encode())
            connectionSocket.close()
            #start_restart(get_serverSocket())

        line_list = list(line)

        if not rcptcommand(line):
            if mailcommand(line):
                connectionSocket.send(syntax_503.encode())
                continue
            elif datacommand(line):
                if not datacmd(line_list, line):
                    #print('500 Syntax error: command unrecognized')
                    continue
                else:
                    #print('250 OK')
                    data_or_rcpt =  "DATA"
                    break
            else:
                connectionSocket.send(syntax_500.encode())
                continue

        if not rcpttocmd(line_list,line):
            connectionSocket.send(syntax_501.encode())
        else:
            data_or_rcpt =  "RCPT"
            break

    return data_or_rcpt,rcpttocmd(line_list,line)

def waitforDATA(connectionSocket):
    while True:
        line = connectionSocket.recv(1024).decode()
        line_list = list(line)

        if not datacommand(line):
            if rcptcommand(line):
                print('503 Bad sequence of commands')
                continue
            elif mailcommand(line):
                print('503 Bad sequence of commands')
                continue
            else:
                print('500 Syntax error: command unrecognized')
                continue

        if not datacommand(line_list,line):
            print('501 Syntax error in parameters or arguments')
        else:
            break
    return True


##### SUPER IMPORTANT FUNCTION ####
# reads one line of stdin at a time
# checks for EOF and kills program when found
def read():
    line = sys.stdin.readline()
    if line == '':
        sys.exit(0)
    return line

# starts State Machine.... writes file then calls itself if valid email sequence reached
def start(connectionSocket,serverSocket):
    #goal: pull out data from socket communication with client
    mailfrom = ''
    recipients = []
    lines = ''

    # initialize mail from state
    bool, mailfrom = waitformail(connectionSocket)

    #keep checking until valid mail from
    while not bool:
        bool, mailfrom = waitformail(connectionSocket)


    bool, mailto = waitforrcpt(connectionSocket)

    # keep checking until valid rcpt to
    while not bool:
        bool, mailto = waitforrcpt(connectionSocket)

    # add rcpt to list of recipients
    recipients.append(mailto)



    # keep checking for either valid rcpt or valid data
    # if another rcpt keep checking until data
    while True:
        rcpt_or_data,mailto = waitforrcptordata(connectionSocket)

        # keep looking for valid rcpt or data command
        while rcpt_or_data != 'DATA' and rcpt_or_data != 'RCPT':
            rcpt_or_data = waitforrcptordata(connectionSocket)
        # if line == rcpt
        if rcpt_or_data == 'RCPT':
            recipients.append(mailto)

            connectionSocket.send(ok.encode())
            # don't break cause could be more rcpt's

        # if line == data
        if rcpt_or_data == 'DATA':
            connectionSocket.send(data_ok.encode())
            break

# look for data and append to list
    data = connectionSocket.recv(1024).decode()

    lines = data.split('\n')

    connectionSocket.send(ok.encode())

    # file stuff

    for recipient in recipients:

        split = recipient.split('@')[1]

        # make new file string for each recipient, writes string (file) to output at end
        file = ''
        # open new file...if already created, append new data to same file
        output = open("./forward/{split}".format(split=split), "a+")


        for line in lines:
            if line == '.':
                break
            file += line + '\n'
        output.write(file)
        output.close()

    #line = connectionSocket.recv(1024).decode() + '\n'

    quit_resp = '221 classroom.cs.unc.edu'
    connectionSocket.send(quit_resp.encode())
    connectionSocket.close()
    start_restart(serverSocket)

def data(connectionSocket):
    line = connectionSocket.recv(1024).decode() + '\n'
    print(line)
    if line == 'QUIT\n':
        quit_resp = '221 classroom.cs.unc.edu'
        connectionSocket.send(quit_resp.encode())
        connectionSocket.close()
        server_start(get_port())
    if line == '.\n':
        print('here')
        connectionSocket.send(ok.encode())
        return True,''
    return False,line

def parse_helo(msg,serverSocket):
    if msg[0:5] != 'HELO ':
        serverSocket.close()
        start_restart(serverSocket)
    if domain(msg, 5) == False:
        serverSocket.close()
        start_restart(serverSocket)
    if msg[-1] != '\n':
        serverSocket.close()
        start_restart(serverSocket)
    serverSocket.send((msg.strip('\n') + 'pleased to meet you\n').encode())

# loops server
def start_restart(serverSocket):
    connectionSocket, addr = serverSocket.accept()

    greeting = '220 classroom.cs.unc.edu'

    # sends greeting to client
    connectionSocket.send(greeting.encode())

    # client send helo
    helo = connectionSocket.recv(1024).decode()

    parse_helo(helo,connectionSocket)

    start(connectionSocket,serverSocket)

    connectionSocket.close()

    start_restart(serverSocket)

port = 8623

def set_port(port):
    port = port

def get_port():
    return port

def server_start(port):
    serverPort = port
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    #print('Server is ready')
    start_restart(serverSocket)

def main():

    port = int(sys.argv[1])
    set_port(port)
    server_start(port)
    # start state machine...everything handled by this function
    start(port)

main()

#print(False == False)

'''
MAIL	FROM:<K0~ @N2X5R2>	
MAIL FROM: <l@P5.i9.k2ov>
MAIL	FROM:	 <4j@e5.F7.Dq>
MAIL   FROM:	<g@c1x>
MAIL 	   	FROM:</ s@T6t> 
MAIL	 FROM: 	<#@b3>
MAIL	FROM:<X@K5dJ>
MAIL		FROM:		  <3@O5.br8.lMVUI>
MAIL 	FROM:<D@qx>		 	 
MAIL FROM:<@S08> 	
MAIL FROM:<s@US.N4Z6.hY03B.H0E.cx>	 
'''

