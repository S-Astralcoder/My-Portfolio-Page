import os
import smtplib
from email.message import EmailMessage

from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "portfolio-secret-key-change-me")

MY_EMAIL = os.environ.get("MY_EMAIL")
PASSWORD = os.environ.get("PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=3, max=120)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField("Send Message")


def send_contact_email(form: ContactForm) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"Portfolio Contact: {form.subject.data}"
    msg["From"] = MY_EMAIL
    msg["To"] = RECEIVER_EMAIL

    body = (
        "New portfolio contact form submission\n\n"
        f"Name: {form.name.data}\n"
        f"Email: {form.email.data}\n"
        f"Subject: {form.subject.data}\n\n"
        "Message:\n"
        f"{form.message.data}\n"
    )
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as connection:
        connection.login(MY_EMAIL, PASSWORD)
        connection.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def home():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            send_contact_email(form)
            flash("Your message was sent successfully.", "success")
            return redirect(url_for("home") + "#contact")
        except Exception:
            flash("Unable to send message right now. Please try again later.", "error")
            return redirect(url_for("home") + "#contact")

    return render_template("index.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
