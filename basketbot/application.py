from basketbot import create_app

# from logging.config import dictConfig
#
# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })
#
app = create_app(config="basketbot.config.Production")

#
# from flask import request
# @app.before_request
# def log_request():
#     app.logger.debug("Request Headers %s", request.headers)
#     app.logger.debug("Request data %s", request.data)
#     return None
