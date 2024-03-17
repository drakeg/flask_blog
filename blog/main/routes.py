from flask import render_template, request, Blueprint
from blog.models import Post, AboutPageContent
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)

@main_bp.route('/about')
def about():
    title = 'About'
    about_content = AboutPageContent.query.first()
    return render_template('about.html', content=about_content, title=title)

@main_bp.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        posts = Post.query.filter(
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%')
            )
        ).all()
    else:
        posts = []
    return render_template('search_results.html', posts=posts, query=query)