''' Email interface module
For sending short text messages and emails on status events
'''
import time
import sys
import smtplib

class Mail:
    def __init__(self, toaddr=None, subject=None, msg=None):
        self.username = 'michael.jennings42'
        self.password = 'icanhazAnonEmail?'
        self.fromaddr = 'michael.jennings42@gmail.com'
        self.serveraddr = 'smtp.gmail.com:587'
##        self.server = smtplib.SMTP(self.serveraddr)
##        self.server.starttls()
##        self.server.login(self.username,self.password)

        if toaddr:
            self.toaddr = toaddr
        else:
            self.toaddr = '3362631393@vtext.com'
        if subject:
            self.subject = subject
        else:
            self.subject = 'Testing'
        if msg:
            self.msg = msg
        else:
            self.msg = 'The dishes are done!!!'

    def setSubject(self, subj):
        self.subject = subj

    def setMessage(self, msg):
        self.msg = msg

    def setToAddr(self, toaddr):
        self.toaddr = toaddr

    def send(self):
        self.server = smtplib.SMTP(self.serveraddr)
        self.server.starttls()
        self.server.login(self.username,self.password)
        if type(self.toaddr) == list:
            to_header = ", ".join(self.toaddr)
        else:
            to_header = self.toaddr

        message =   ( "From: %s\nTo: %s\nSubject: %s\n\n%s" %
                      (self.fromaddr, to_header, self.subject, self.msg) )
        #print message
        print 'Sending message...'
        self.server.sendmail(self.fromaddr, self.toaddr, message)
        self.server.quit()

    def close(self):
        pass
        #self.server.quit()


def main(argv):
    print '====================================='
    print '= Testing Mail Module.'
    print '====================================='
    mail=Mail()
    mail.send()
    mail.setMessage('This is 1 later.')
    time.sleep(60)
    mail.send()
    mail.setMessage('This is 10 later.')
    time.sleep(60*10)
    mail.send()
    mail.setMessage('This is 25 later...')
    time.sleep(60*25)
    mail.send()
    mail.close()
    print '====================================='
    print '= Testing Complete'
    print '====================================='

if __name__ == "__main__":
    main(sys.argv[1:])
