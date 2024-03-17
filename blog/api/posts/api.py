from flask import request
from flask_restx import Namespace, Resource, fields
from blog.models import Post
from blog import db
from flask_login import current_user
from blog.decorators import api_key_required
from blog.utilities import validate_json_input

api = Namespace('posts', description='Posts related operations')

post_model = api.model('Post', {
    'id': fields.Integer(readOnly=True, description='The post unique identifier'),
    'title': fields.String(required=True, description='The post title'),
    'content': fields.String(required=True, description='The post content'),
    'content_html': fields.String(required=True, description='The post content in HTML'),
    'date_posted': fields.DateTime(description='The date the post was posted'),
    'author': fields.String(required=True, description='The post author'),
    'tag_names': fields.List(fields.String, attribute=lambda x: x.tag_names())
})

@api.route('/')
class PostList(Resource):
    @api_key_required
    @api.doc('list_posts')
    @api.marshal_list_with(post_model)
    def get(self):
        """List all posts"""
        posts = Post.query.all()
        return posts

    @api_key_required
    @api.doc('create_post')
    @api.expect(post_model)
    @api.marshal_with(post_model, code=201)
    def post(self):
        """Create a new post"""
        data = request.json
        author_id = current_user.id
        required_fields = ['title', 'content']
        errors = validate_json_input(data, required_fields)
        if errors:
            return jsonify({'errors': errors}), 400

        new_post = Post(title=data['title'], content=data['content'], user_id=author_id)
        db.session.add(new_post)
        db.session.commit()
        return new_post, 201

@api.route('/<int:id>')
@api.param('id', 'The post identifier')
@api.response(404, 'Post not found.')
class PostResource(Resource):
    @api_key_required
    @api.doc('get_post')
    @api.marshal_with(post_model)
    def get(self, id):
        """Fetch a post given its identifier"""
        post = Post.query.filter_by(id=id).first()
        if post is None:
            api.abort(404)
        else:
            return post
        
    @api_key_required
    @api.doc('delete_post')
    def delete(self, id):
        """Delete a post"""
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return {'message': 'Post deleted'}, 200
