import logging, email
import wsgiref.handlers
import exceptions

from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class LogSenderHandler(InboundMailHandler):
  data=""
  subject=""
  def logme(self,log):
    logging.info(log)
    self.data += log
    self.data += "<br>"

  def send_mail_(self,):
    mail.send_mail(sender="forwarder <forward@<app-id>.appspotmail.com>",
          to="dushyant<dushyant@example.com>",
          subject=self.subject,
          body="",
          html=self.data)

  def receive(self, mail_message):
    self.logme("================================")
    self.logme("Received a mail_message from: " + mail_message.sender)
    self.subject=mail_message.subject
    self.logme("The email subject: " + mail_message.subject)
    self.logme("The email was addressed to: " + str.join(str(mail_message.to), ', '))

    try:
      self.logme("The email was CC-ed to: " + str.join(str(mail_message.cc), ', '))
    except exceptions.AttributeError :
      self.logme("The email has no CC-ed recipients")

    try:
      self.logme("The email was send on: " + str(mail_message.date))
    except exceptions.AttributeError :
      self.logme("The email has no send date specified!!!")

    plaintext_bodies = mail_message.bodies('text/plain')
    html_bodies = mail_message.bodies('text/html')

    for content_type, body in html_bodies:
      decoded_html = body.decode()
      self.logme("content_type: " + content_type)
      self.logme("decoded_html: " + decoded_html)
      plaintext_bodies

    attachments = []
    try:
      if mail_message.attachments :
        if isinstance(mail_message.attachments[0], basestring):
          attachments = [mail_message.attachments]
        else:
        	attachments = mail_message.attachments
    except exceptions.AttributeError :
      self.logme("This email has no attachments.")

    self.logme("number of attachments: " + str(len(attachments)))

    for filename, content in attachments:
      #logging.info("plaintext_bodies: " + plaintext_bodies)
      self.logme("filename: " + filename)
      content

    self.logme("--------------------------------")
    self.send_mail_()



def main():
  application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
