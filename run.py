import os
import sys

# add project path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import flask_app, ilog


def main():
    ilog.info("{0} server is running... {0}".format("-" * 20))
    flask_app.run(
        host=flask_app.config["HOST"],
        port=flask_app.config["PORT"],
        debug=flask_app.config["DEBUG"]
    )


if __name__ == "__main__":
    main()

