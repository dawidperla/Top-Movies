from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filmy.db'
Bootstrap(app)
db = SQLAlchemy()
db.init_app(app)


# CREATE TABLE MOVIE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250), unique = True, nullable = True)
    year = db.Column(db.Integer, nullable = True)
    description = db.Column(db.String(500), nullable = True)
    rating = db.Column(db.Float, nullable = True)
    ranking = db.Column(db.Integer, nullable = True)
    review = db.Column(db.String(250), nullable = True)
    img_url =db.Column(db.String(400), nullable = True)


# ADD FILM DIRECTLY TO DB - HARD CODE
# new_movie = Movie(title = 'Phone Booth',
#                   year = 2002,
#                   description = "Publicist Stuart Shepard finds himself trapped in a phone booth, "
#                                 "pinned down by an extortionist's sniper rifle. Unable to leave or "
#                                 "receive outside help, Stuart's negotiation with the caller leads to a "
#                                 "jaw-dropping climax." ,
#                   rating = 7.3,
#                   ranking = 10,
#                   review = "My favourite character was the caller.",
#                   img_url = "https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
with app.app_context():
    db.create_all()
    # db.session.add(new_movie)
    db.session.commit()


# FIELDS IN WTF FORM + BUTTON SUBMIT
class RateMovieForm(FlaskForm):
    new_rating = StringField(label="Your new raiting eg.7.8 :", validators=[DataRequired()])
    new_review = StringField(label ="Your new review: ", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    add_movie = SubmitField(label="Add Movie")


@app.route("/")
def home():
    movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()


    return render_template("index.html", card = movies)
#
#
# # EDIT RATING AND REVIEW FOR MOVIE
@app.route("/edit", methods = ['POST', 'GET'])
def edit_rating():
    form = RateMovieForm()
    if form.validate_on_submit() and request.method == 'POST':
        movie_id = request.args.get("id")
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = float(form.new_rating.data)
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form = form)


# # DELETE MOVIE FROM DATABASE
@app.route('/delete')
def delete_movie():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

#
# # ADD FILM TO DB
@app.route('/add', methods = ['GET', 'POST'])
def add():
    add_form = AddMovieForm()
    if add_form.validate_on_submit and request.method == 'POST':
        param = {
            'language': 'en-US',
            'query': add_form.title.data,
        }
        API_KEY = '309a5cf7dfbd39d4a9d559d92e6b4bca'
        data_request = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}", params=param)
        data = data_request.json()
        # print(data_request.json())
        movie_title = data['results']
        return render_template('select.html', form = movie_title)
    return render_template('add.html', addform = add_form )
#
#
@app.route('/find')
def find_movie():
    find_movie_id = request.args.get("id")
    if find_movie_id:
        param = {
            'language': 'en-US',

        }
        API_KEY = '309a5cf7dfbd39d4a9d559d92e6b4bca'
        request_api = requests.get(f'https://api.themoviedb.org/3/movie/{find_movie_id}?api_key={API_KEY}', params = param )
        data = request_api.json()
        new_movie = Movie(
            title = data["title"],
            description = data["overview"],
            year = data["release_date"].split('-')[0],
            img_url = f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            rating = 1.0
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit_rating', id=new_movie.id))


# @app.route('/search')
# def find_cafe(location):


if __name__ == '__main__':
    app.run(debug=True)

