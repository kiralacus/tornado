from Handler import Verifycode, BaseHandler, Passport, Profile

from tornado.web import RequestHandler

import os


handler = [
    (r'/api/pitcode', Verifycode.PicCodeHandler),
    (r'/api/smscode', Verifycode.SMSCodeHandler),
    (r'/api/register', Passport.RegisterHandler),
    (r'/api/login', Passport.LoginHandler),
    (r'/api/check_login', Passport.CheckLoginHandler),
    (r'/api/logout', Passport.LogoutHandler),
    (r'/api/profile/avatar', Profile.AvatarHandler),
    (r'/api/profile/name',Profile.NameHandler),
    (r'/api/profile/auth', Profile.AuthHandler),
    (r'/api/profile', Profile.ProfileHandler),
    (r'/(.*)', BaseHandler.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'html'), 'default_filename': 'index.html'}),
]