import os
import json

from google.appengine.ext import webapp
from generic import JsonRpcService

class ViewService(JsonRpcService):
  def json_create(self):
    return "Hello, World!"
