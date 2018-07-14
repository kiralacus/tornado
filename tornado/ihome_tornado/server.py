import tornado

from tornado import web, ioloop, options, httpserver

import torndb

import urls

import config

import redis

tornado.options.define('port', 8000, 'run on this port')

class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.db = torndb.Connection(**config.mysql_option)
        self.redis = redis.StrictRedis(**config.redis_options)

def main():
    tornado.options.options.log_file_prefix = config.log_path
    tornado.options.options.logging = config.log_level
    tornado.options.parse_command_line()
    app = Application(urls.handler, **config.setting)
    http_server = httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
