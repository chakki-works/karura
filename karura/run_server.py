import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import tornado.ioloop
from tornado.options import define, options, parse_command_line
from karura.server.app import application


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


def main():
    parse_command_line()
    app = application(options.debug)
    port = int(os.environ.get("PORT", options.port))
    print("karura server running on {}".format(port))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()