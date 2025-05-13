from datetime import datetime

from flask_restful import reqparse, abort, Api, Resource

from .projects import Project
from .template_projects import Template_project
from . import db_session
from .users import User
from flask import jsonify
from werkzeug.security import generate_password_hash
from flask_login import current_user


temp_sites_parser = reqparse.RequestParser()
temp_sites_parser.add_argument("site_name", required=True, type=str)
temp_sites_parser.add_argument("name", required=True, type=str)
temp_sites_parser.add_argument("type", required=True, type=str)
temp_sites_parser.add_argument("about", required=True, type=str)
temp_sites_parser.add_argument("explanation", required=True, type=str)

sites_parser = reqparse.RequestParser()
sites_parser.add_argument("name", required=True, type=str)
sites_parser.add_argument("type", required=True, type=str)
sites_parser.add_argument("about", required=True, type=str)
sites_parser.add_argument("is_finished", required=False, type=bool)
sites_parser.add_argument("start_time", required=False, type=datetime)


def abort_if_template_site_not_found(site_id: str):
    session = db_session.create_session()
    project = None
    if site_id.isdigit():
        site_id = int(site_id)
        project = session.query(Template_project).get(site_id)
    session.close()
    if not project:
        abort(404, message=f"Site {site_id} not found")


class Sites_ListResourse(Resource):
    def get(self):
        con = sqlite3.connect(fr"user_dirs/{current_user.login}_dir/projects.db")
        cursor = con.cursor()
        params = ["id", "name", "type", "about", "is_finished", "start_time"]
        user_projects = cursor.execute(
            f"""
            SELECT {", ".join(params)}
            FROM projects
            """
        ).fetchall()
        con.close()

        user_projects = list(map(
            lambda project: {par: project[params.index(par)] for par in params}, user_projects
        ))
        return jsonify({
            "projects": [item.to_dict("*") for item in user_projects]
        })

    def post(self):
        args = sites_parser.parse_args()
        session = db_session.create_session()
        project = Project(
            type=args["type"],
            name=args["name"],
            about=args["about"],
            is_finished=False,
            start_time=datetime.now()
        )
        session.add(project)
        session.commit()
        session.close()
        return jsonify(
            project.to_dict("*")
        )


class TemplateSites_ListResource(Resource):
    def get(self):
        session = db_session.create_session()
        template_projects = session.query(Template_project).all()
        session.close()
        return jsonify({
            "template_projects": [item.to_dict("*") for item in template_projects]
        })

    def post(self):
        args = temp_sites_parser.parse_args()
        session = db_session.create_session()
        template_project = Template_project(
            type=args["type"],
            site_name=args["site_name"],
            name=args["name"],
            about=args["about"],
            explanation=args["explanation"]
        )
        session.add(template_project)
        session.commit()
        session.close()
        return jsonify(
            template_project.to_dict("*")
        )


class TemplateSites_Resource(Resource):
    def get(self, site_id):
        abort_if_template_site_not_found(site_id)
        session = db_session.create_session()
        template_site = session.query(Template_project).get(site_id)
        session.close()
        return jsonify(template_site.to_dict("*"))

    """def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})"""