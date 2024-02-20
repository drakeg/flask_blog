from flask_login import FlaskLoginClient

app.test_client_class = FlaskLoginClient

def test_request_with_logged_in_user():
	user = User.query.get(1)
	with app.test_client(user=user) as client:
		client.get("/")
