import smtplib
from flask import Flask, render_template, url_for, redirect, jsonify, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, URL, Optional, InputRequired

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)

# create DB
class Base(DeclarativeBase):
    pass

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

with app.app_context():
    db.create_all()


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('Maps URL', validators=[DataRequired(), URL()])
    img_url = StringField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    has_sockets = BooleanField('Sockets',  validators=[InputRequired()], default=False)
    has_toilet = BooleanField('Toilets', validators=[InputRequired()], default=False)
    has_wifi = BooleanField('Wifi', validators=[InputRequired()], default=False)
    can_take_calls = BooleanField('Can Take Calls', validators=[InputRequired()], default=False)
    seats = StringField('Seats', validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cafes')
def cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    list_of_cafes =  [cafe.to_dict() for cafe in result]
    # print(f'list of cafes: {list_of_cafes}')
    return render_template('cafe.html', cafes=list_of_cafes)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.form
        send_email(data['name'], data['email'],data['phone'], data['message'])
        return render_template('contact.html', msg_sent=True)
    return render_template('contact.html', msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f'Subject: New Message\n\n Name: {name}\nEMail:{email}\nPhone:{phone}\nMessage:{message}'
    with smtplib.SMTP('smtp.gmail.com', port=587) as connection:
        connection.starttls()
        connection.login(os.getenv('MY_EMAIL'), os.getenv('MY_PASSWORD'))
        connection.sendmail(os.getenv('MY_EMAIL'), os.getenv('MY_EMAIL'), email_message)

# add cafe
@app.route('/add',methods=['GET','POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe_details = Cafe(
            name = form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,  # ✅ Directly use WTForms data
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data
        )
        db.session.add(new_cafe_details)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)

# delete cafe
@app.route('/delete/<int:cafe_id>',methods=['GET','POST'])
def delete_cafe(cafe_id):
    cafe_to_delete = db.session.get(Cafe, cafe_id)
    if cafe_to_delete:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        flash('Cafe deleted successfully!', 'success')
    else:
        flash('cafe not found', 'danger')
    return redirect(url_for('cafes'))



if __name__ == '__main__':
    app.run(debug=True)