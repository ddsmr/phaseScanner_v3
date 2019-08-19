# from time import gmtime, strftime
import time
import numpy
import httplib2
import os
import socket

import oauth2client
from oauth2client import file

from oauth2client import client, tools
from time import strftime, gmtime
import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from apiclient import errors, discovery
# from apiclient.errors import build #errors, discovery


import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.header import Header
from email.utils import formataddr

SCOPES = 'https://mail.google.com/'  # https://www.googleapis.com/auth/gmail.send
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'


def get_credentials():
    '''
            Gets the credentials from the gmail-python-email-send.json file via the oauth2client protocols
        and returns the credentials as output
    '''
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      query: String used to filter messages returned.
      Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
      List of Messages that match the criteria of the query. Note that the
      returned list contains Message IDs, you must use get with the
      appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    '''
            Calls the createMessage functions depending if there is an attachmentFile or not, sends the email and
        returns as a result the status message of the entire thing
    '''
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(
            sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else:
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result


def SendMessageInternal(service, user_id, message):
    '''
        Some internal stuff to try and sort out if anything is or isn't in the wrong format?
    '''
    try:
        message = (service.users().messages().send(
            userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"


def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    '''
            Creates a MIME message addresed to "to" from "sender" and contains a HTML and a plain part of the message.
        Returns a 64 bit encoded message as a result
    '''
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('UTF-8')).decode('ascii')}


def createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients
      attachmentFile: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['To'] = to
    message['From'] = sender
    message['Subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)

    message.attach(messageA)

    print("create_message_with_attachment: file:", attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, _subtype=sub_type)
        msg.set_payload(fp.read())
        fp.close()

    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    email.encoders.encode_base64(msg)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode('UTF-8')).decode('ascii')}


def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        # print 'Message snippet: %s' % message['snippet']

        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def GetMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                 format='raw').execute()

        # print 'Message snippet: %s' % message['snippet']

        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(msg_str)

        return mime_msg
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def sendCompletionEmail(scanSting, pathToAttach=None, toList=['dansmaranda@gmail.com']):
    '''
            Pseudo-main sorta file ment to send out a completion email whenever a scan finishes.
        Takes a "scanSting" to be inserted somewhere in the message and a "pathToAttach" file path
        to the required attachment.
    '''

    # str(numpy.random.randint(1, 1000000))
    jobID = strftime("%d/%m/%Y %H:%M:%S", gmtime())

    computerName = socket.gethostname()
    computerName = computerName[0:1].upper() + computerName[1:]

    for to in toList:
        sender = formataddr((str(Header(computerName, 'utf-8')),
                             'ppt.glasgow.computer@gmail.com'))
        subject = "Finished " + scanSting + " scan @ " + computerName + "::" + jobID
        msgHtml = """<p>Hi, <br><br>
        Current time of scan finishing is : <br>""" + \
            "&nbsp;&nbsp;&nbsp;&nbsp;" + strftime("%d/%m/%Y %H:%M:%S", gmtime()) + "<br>"\
            """
        Have scanned the following: <br>
        &nbsp;&nbsp;&nbsp;&nbsp; """ + scanSting
        if pathToAttach:
            msgHtml = msgHtml + """ <br><br>
            See attached pdf's for the plots!<br><br>

            Cheers,<br>
            """ + computerName + """
            </p>
            """
        else:
            msgHtml = msgHtml + """ <br><br>

            Cheers,<br>
            """ + computerName + """
            </p>
            """

        msgPlain = "asd /n asd"
        # Send message with attachment:
        if pathToAttach:
            SendMessage(sender, to, subject, msgHtml, msgPlain, pathToAttach)
        else:
            SendMessage(sender, to, subject, msgHtml, msgPlain)

    return None


# def sendEmail_(scanSting, pathToAttach=None, toList=['dansmaranda@gmail.com']):
#     '''
#             Pseudo-main sorta file ment to send out a completion email whenever a scan finishes.
#         Takes a "scanSting" to be inserted somewhere in the message and a
#         "pathToAttach" file path to the required attachment.
#     '''
#
#     # str(numpy.random.randint(1, 1000000))
#     # jobID = strftime("%d/%m/%Y %H:%M:%S", gmtime())
#
#     # computerName = socket.gethostname()
#     # computerName = computerName[0:1].upper() + computerName[1:]
#     computerName = 'SLURM at HPCS/CSD3'
#     import random
#     for to in toList:
#         sender = formataddr((str(Header(computerName, 'utf-8')),
#                              'ppt.glasgow.computer@gmail.com'))
#         jobID = random.randint(14000000, 15000000)
#         jobNb = random.randint(1, 10)
#
#         subject = "Slurm Job_id=" + str(jobID) + " Name=openmm-uf" + str(jobNb) + " Failed, Run time 00:00:00, FAILED"
#         msgHtml = ''
#
#         # if pathToAttach:
#         #     msgHtml = msgHtml + """ <br><br>
#         #     See attached pdf's for the plots!<br><br>
#         #
#         #     Cheers,<br>
#         #     """ + computerName + """
#         #     </p>
#         #     """
#         # else:
#         #     msgHtml = msgHtml + """ <br><br>
#         #
#         #     Cheers,<br>
#         #     """ + computerName + """
#         #     </p>
#         #     """
#         #
#         msgPlain = ""
#         # Send message with attachment:
#         if pathToAttach:
#             SendMessage(sender, to, subject, msgHtml, msgPlain, pathToAttach)
#         else:
#             SendMessage(sender, to, subject, msgHtml, msgPlain)
#
#     return None


def labelMessageAsRead(service, user_id, msg_id):
    """Modify the Labels on the given Message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The id of the message required.
      msg_labels: The change in labels.

    Returns:
      Modified message, containing updated labelIds, id and threadId.
    """
    try:
        message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                    body={'removeLabelIds': ['UNREAD']}).execute()

        label_ids = message['labelIds']

        print ('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
        return message
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)


if __name__ == '__main__':
        # sendCompletionEmail("CHANGE THIS WHEN RUNNING SCAN", '/home/smaranda/Documents/latex/Postgraduate/Orbifolds_Paper/SMSSM_Case2.pdf')
        # messageIDtest = "rROga#FiYbK9piz7FHDjlZQ"

    credentials = get_credentials()
    serviceHTTP = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=serviceHTTP)

    # allMessages = ListMessagesMatchingQuery(service , "me" )

    #   This section will proceed and read the UNREAD emails from the inbox, and if they contain the following identifiers:
    #
    #       1) TRUSTED SENDER: Sender has to be on the trusted sender list
    #       2) TRUSTED SUBJECT: Subject email must contain the specified header
    #       3) ----> Need to implement RSA key exchange via attachment <----
    #
    #   If all the above conditions are met the script then proceeds to execute the commands specified in the body of the email. Finnaly
    # the script marks the email that it has finished executing as read on the gMail server

    cmndQue = []
    while True:

        time.sleep(5)

        unreadMessages = ListMessagesMatchingQuery(service, 'me', "l:unread")
        if len(unreadMessages) == 0:
            print ("No Unread Messages, will keep listening!")

        for member in unreadMessages:

            if len(cmndQue) == 0:
                print ("Command Que is Empty, proceeding to put commands in it")

                messageInEmail = GetMessage(service, "me", member['id'])
                MIMEmessage = GetMimeMessage(service, "me", member['id'])

                emailBody = MIMEmessage._payload[0]._payload

                for line in emailBody.split('\n'):
                    if line != '\r' and line != '':
                        cmndQue.append(line.replace('\r', ''))
                print (cmndQue)

                isTrustedSubject = False
                isTrustedSender = False

                for header in messageInEmail['payload']['headers']:

                    if header['name'] == "Subject":
                        if header['value'] == "Test email":
                            print ("CONFIRMED: Email subject!")
                            isTrustedSubject = True

                    if header['name'] == 'From':
                        if header['value'] == 'Dan Smaranda <dansmaranda@gmail.com>':
                            print ("CONFIRMED: Sender!")
                            isTrustedSender = True

                    if isTrustedSender and isTrustedSubject:
                        print ("Trusted Sender and cmd Subject! Proceeding with commands ::")
                        for commandLine in cmndQue:
                            print (commandLine)
                            os.system(commandLine)
                            print (cmndQue)
                        cmndQue = []

                labelMessageAsRead(service, 'me', member['id'])

            else:

                print ("Comand Que alreaddy populated, will break and add commands when they've finished")
                break
