from flask import request
from flask_restx import Namespace, Resource, fields, abort
from werkzeug.security import generate_password_hash
from blog.models import User
from blog import db
from blog.decorators import api_key_required

api = Namespace('users', description='User related operations')

user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description="The user's unique identifier"),
    'username': fields.String(required=True, description="The user's username"),
    'email': fields.String(required=True, description="The user's email"),
    'role_name': fields.String(attribute=lambda x: x.role_name())
})

@api.route('/')
class UserList(Resource):
    @api_key_required
    @api.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return User.query.all()

    @api_key_required
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        data = request.json
        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
            abort(400, 'Username or email already exists')
        user = User(username=data['username'], email=data['email'], 
                    password=generate_password_hash(data['password'], method='sha256'))
        db.session.add(user)
        db.session.commit()
        return user, 201

@api.route('/<int:id>')
@api.param('id', 'The user identifier')
@api.response(404, 'User not found')
class UserResource(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    def get(self, id):
        """Fetch a user given its identifier"""
        user = User.query.filter_by(id=id).first()
        if user is None:
            api.abort(404)
        else:
            return user

    @api.doc('delete_user')
    def delete(self, id):
        """Delete a user"""
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted'}, 200
