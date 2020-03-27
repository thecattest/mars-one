from flask_restful import abort, Resource
from flask import jsonify
from data import db_session
from data.__all_models import Jobs
from parsers import JobsParser


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'job': job.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators',
                  'kind', 'start_date', 'is_finished'))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': "OK"})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('team_leader', 'job', 'work_size', 'collaborators',
                  'kind', 'start_date', 'is_finished'))
            for item in jobs]})

    def post(self):
        args = JobsParser.parse_args()
        session = db_session.create_session()
        job = Jobs()
        job.team_leader = args["team_leader"]
        job.job = args["job"]
        job.work_size = args["work_size"]
        job.kind = args["kind"]
        if "collaborators" in args:
            job.collaborators = args["collaborators"]
        if "creator" in args:
            job.creator = args["creator"]
        if "is_finished" in args:
            job.is_finished = args["is_finished"]
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})