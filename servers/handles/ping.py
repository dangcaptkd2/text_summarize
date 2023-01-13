from flask_restful import Resource


class Ping(Resource):
    #
    def get(self):
        return dict(error=0, message="server starting...")
