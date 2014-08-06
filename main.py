#!/usr/bin/env python

import webapp2

class MainHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write("<div style='text-align:center;margin-top:20px;'>Broom brroom..</div>")


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
