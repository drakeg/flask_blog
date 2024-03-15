from flask import request
from flask_restx import Namespace, Resource, fields
from blog.models import AboutPageContent
from blog import db
from flask import abort
from blog.decorators import api_key_required

api = Namespace('about', description='About page operations')

about_model = api.model('AboutPageContent', {
    'id': fields.Integer(readOnly=True, description="The unique identifier"),
    'content': fields.String(required=True, description="The about page content"),
    'content_html': fields.String(required=True, description="The about page content in HTML"),
})

@api.route('/')
class AboutList(Resource):
    @api_key_required
    @api.marshal_list_with(about_model)
    def get(self):
        """List all about content entries"""
        return AboutPageContent.query.all()

    @api_key_required
    @api.expect(about_model, validate=True)
    @api.marshal_with(about_model, code=201)
    def post(self):
        """Create a new about content entry"""
        data = request.json
        about_content = AboutPageContent(content=data['content'])
        db.session.add(about_content)
        db.session.commit()
        return about_content, 201

@api.route('/<int:id>')
@api.param('id', 'The about content identifier')
@api.response(404, 'About content not found')
class AboutResource(Resource):
    @api_key_required
    @api.marshal_with(about_model)
    def get(self, id):
        """Fetch a single about content entry"""
        about_content = AboutPageContent.query.get_or_404(id)
        return about_content

    @api_key_required
    @api.doc('delete_about')
    def delete(self, id):
        """Delete an about content entry"""
        about_content = AboutPageContent.query.get_or_404(id)
        db.session.delete(about_content)
        db.session.commit()
        return {'message': 'About content deleted'}, 200
