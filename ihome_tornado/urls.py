from Handler import Verifycode, BaseHandler, Passport

from tornado.web import RequestHandler

import os


handler = [
    (r'/api/pitcode', Verifycode.PicCodeHandler),
    (r'/api/smscode', Verifycode.SMSCodeHandler),
    (r'/api/register', Passport.RegisterHandler),
    (r'/api/login', Passport.LoginHandler),
    (r'/(.*)', BaseHandler.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'html'), 'default_filename': 'index.html'}),
]