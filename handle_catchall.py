import logging, email
import wsgiref.handlers
import exceptions

from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from google.appengine.ext import ndb

from google.appengine.ext import blobstore
from google.appengine.api import files



class mmails(ndb.Model):
  """Models an individual guestbook entry with author, content, and date."""
  from_ = ndb.StringProperty()
  subject = ndb.StringProperty()
  content = ndb.TextProperty()
  to_ = ndb.TextProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

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
          
  def save(self, name, content):
    file_name = files.blobstore.create(
      mime_type='application/octet-stream',
      _blobinfo_uploaded_filename=name
    )
    
    logging.info("saving file "+file_name);

    with files.open(file_name, 'a') as f:
      f.write(content)

    files.finalize(file_name)
    return name


  def receive(self, mail_message):
    self.logme("================================")
    self.logme("Received a mail_message from: " + mail_message.sender)
    if hasattr(mail_message,"subject"):
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
      
    allBodies = "";
    for body in plaintext_bodies:
      allBodies = allBodies + " " + body[1].decode()
    self.logme("plaintext_bodies: " + allBodies);
    
    attachments = []
    my_file = []
    my_list = []
    if hasattr(mail_message, 'attachments'):
      file_name = ""
      file_blob = ""
      for filename, filecontents in mail_message.attachments:
        file_name = filename
        file_blob = filecontents.decode()
        my_file.append(file_name)
        self.save(file_name,file_blob)

    self.logme("number of attachments: " + str(len(attachments)))
    self.logme("number of my_file: " + str(len(my_file)))
    self.logme("number of my_list: " + str(len(my_list)))

    for filename, content in attachments:
      self.logme("filename: " + filename)
      

    self.logme("--------------------------------")
    self.send_mail_()
    allBodies=u''.join(allBodies).encode('utf-8').strip()
    mm = mmails(from_=mail_message.sender,subject=self.subject,content = allBodies,to_=str.join(str(mail_message.to), ', '))
    mm.put()



def main():
  application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
