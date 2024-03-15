from flask import request
from flask_restx import Namespace, Resource, fields
from blog.models import Post
from blog import db

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
    @api.doc('list_posts')
    @api.marshal_list_with(post_model)
    def get(self):
        """List all posts"""
        posts = Post.query.all()
        return posts

    @api.doc('create_post')
    @api.expect(post_model)
    @api.marshal_with(post_model, code=201)
    def post(self):
        """Create a new post"""
        data = request.json
        new_post = Post(title=data['title'], content=data['content'])
        db.session.add(new_post)
        db.session.commit()
        return new_post, 201

@api.route('/<int:id>')
@api.param('id', 'The post identifier')
@api.response(404, 'Post not found.')
class PostResource(Resource):
    @api.doc('get_post')
    @api.marshal_with(post_model)
    def get(self, id):
        """Fetch a post given its identifier"""
        post = Post.query.filter_by(id=id).first()
        if post is None:
            api.abort(404)
        else:
            return post

    @api.doc('delete_post')
    def delete(self, id):
        """Delete a post"""
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return {'message': 'Post deleted'}, 200
