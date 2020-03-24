from flask import Blueprint, jsonify, make_response, abort, request

from data import db_session
db_session.global_init("db/mars.sqlite")

from data.__all_models import *


blueprint = Blueprint("jobs_api", __name__,
                      template_folder="templates")


@blueprint.route("/api/jobs")
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return make_response(
        jsonify(
            {
                "jobs": [item.to_dict(only=('id', 'job', 'work_size', 'collaborators', 'is_finished',
                                            'kind', 'team_leader', 'start_date', 'end_date',
                                            'creator', 'user.name', 'user.surname'))
                         for item in jobs]
            }
        ),
        200
    )


@blueprint.route("/api/jobs/<int:job_id>",  methods=['GET'])
def get_one_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        abort(404)
    return make_response(
        jsonify(
            {
                "job": job.to_dict(only=('id', 'job', 'work_size', 'collaborators', 'is_finished',
                                        'kind', 'team_leader', 'start_date', 'end_date',
                                         'creator', 'user.name', 'user.surname'))
            }
        ),
        200
    )


@blueprint.route("/api/jobs", methods=["POST"])
def create_job():
    if not request.json:
        return make_response({"error": "Empty request"}, 400)
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'work_size', 'collaborators', 'kind', 'is_finished']):
        abort(400)
    session = db_session.create_session()
    job = Jobs()
    job.team_leader=request.json['team_leader']
    job.job=request.json['job']
    job.work_size=request.json['work_size']
    job.collaborators=request.json['collaborators']
    job.kind=request.json['kind']
    job.is_finished=request.json['is_finished']

    session.add(job)
    session.commit()
    return make_response(
        jsonify({'success': 'ok',
                 'id': job.id}),
        200
    )


@blueprint.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    session.delete(job)
    session.commit()
    return make_response(jsonify({'success': 'OK'}), 200)