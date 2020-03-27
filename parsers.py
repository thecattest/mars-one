from flask_restful import reqparse


UserParser = reqparse.RequestParser()
UserParser.add_argument('surname', required=True)
UserParser.add_argument('name', required=True)
UserParser.add_argument('age', required=True, type=int)
UserParser.add_argument('position', required=True)
UserParser.add_argument('speciality', required=True)
UserParser.add_argument('address', required=True)
UserParser.add_argument('email', required=True)


JobsParser = reqparse.RequestParser()
JobsParser.add_argument('team_leader', required=True)
JobsParser.add_argument('job', required=True)
JobsParser.add_argument('work_size', required=True, type=int)
JobsParser.add_argument('collaborators', required=False)
JobsParser.add_argument('creator', required=False)
JobsParser.add_argument('kind', required=True, type=int)
JobsParser.add_argument('is_finished', required=False, type=bool)