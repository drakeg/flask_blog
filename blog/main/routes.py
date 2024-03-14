from flask import render_template, request, Blueprint
from blog.models import Post, AboutPageContent

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)

@main_bp.route('/about')
def about():
    title = 'About'
    about_content = AboutPageContent.query.first_or_404()
    return render_template('about.html', content=about_content, title=title)