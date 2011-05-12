import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util

import json

class HelloWorldPage(webapp.RequestHandler):
    
    def get(self):
        hello = os.path.join('templates', 'helloworld.html')
        self.response.out.write(template.render(hello, {}))

class JSONHandler(webapp.RequestHandler, json.JSONRPC):

    def post(self):
        response, code = self.handleRequest(self.request.body, self.HTTP_POST)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(code)
        self.response.out.write(response)

    def json_helloworld(self):
        return "Hello, World!"

def main():
    app = webapp.WSGIApplication([
        ('/json', JSONHandler),
        ('/', HelloWorldPage),
        ], debug=True)
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()
