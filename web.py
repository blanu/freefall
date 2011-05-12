from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from pages import *
from api import *

application = webapp.WSGIApplication([
  ('/', Index),
  ('/index.html', Index),
  ('/welcome', Welcome),
  ('/login', Login),

  ('/dashboard/(.*)/(.*)', DashboardDocument),
  ('/dashboard/(.*)', DashboardDatabase),
  ('/dashboard', DashboardIndex),

  ('/session/new', NewSession),
  ('/session/check', CheckSession),
  
  ('/db', DatabaseService),
  ('/view', ViewService),
  ('/document', DocumentService),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
