from flask import request
from flask_restx import Namespace, Resource, fields, abort
from blog.models import Announcement, db
from datetime import datetime
from blog.decorators import api_key_required

api = Namespace('announcements', description='Announcement related operations')

announcement_model = api.model('Announcement', {
    'id': fields.Integer(readOnly=True, description="The announcement's unique identifier"),
    'title': fields.String(required=True, description="The announcement's title"),
    'content': fields.String(required=True, description="The announcement's content"),
    'content_html': fields.String(required=True, description="The announcement's content in HTML"),
    'date_posted': fields.DateTime(description="The date the announcement was posted"),
    'start_date': fields.DateTime(description="The date the announcement starts"),
    'end_date': fields.DateTime(description="The date the announcement ends"),
})

@api.route('/')
class AnnouncementList(Resource):
    @api_key_required
    @api.marshal_list_with(announcement_model)
    def get(self):
        """List all announcements"""
        return Announcement.query.all()

    @api_key_required
    @api.expect(announcement_model, validate=True)
    @api.marshal_with(announcement_model, code=201)
    def post(self):
        """Create a new announcement"""
        data = request.json
        announcement = Announcement(title=data['title'], content=data['content'])
        db.session.add(announcement)
        db.session.commit()
        return announcement, 201

@api.route('/<int:id>')
@api.param('id', 'The announcement identifier')
@api.response(404, 'Announcement not found')
class AnnouncementResource(Resource):
    @api_key_required
    @api.doc('get_announcement')
    @api.marshal_with(announcement_model)
    def get(self, id):
        """Fetch an announcement given its identifier"""
        announcement = Announcement.query.filter_by(id=id).first()
        if announcement is None:
            api.abort(404)
        else:
            return announcement

    @api_key_required
    @api.doc('delete_announcement')
    def delete(self, id):
        """Delete an announcement"""
        announcement = Announcement.query.get_or_404(id)
        db.session.delete(announcement)
        db.session.commit()
        return {'message': 'Announcement deleted'}, 200