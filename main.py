from flask import Flask , url_for , jsonify, render_template , redirect , flash , request , send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped , mapped_column , DeclarativeBase
from werkzeug.security import generate_password_hash , check_password_hash
from sqlalchemy import String , Integer
from flask_login import LoginManager, login_required , login_user , UserMixin,current_user,logout_user


app = Flask(__name__)

app.config["SECRET_KEY"] = "ARJUNTHEGREAT"

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)



class User(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register",methods=["GET","POST"])
def register():

    if request.method == "POST":

        hashed_password = generate_password_hash(
                        password=request.form.get("password"),
                        method="pbkdf2:sha256",
                        salt_length=8
        )

        new_user = User(
            name = request.form.get("name"),
            email = request.form.get("email"),
            password = hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return render_template("secrets.html",name=request.form.get("name"))

    return render_template("register.html")


@app.route("/secrets",methods=["GET","POST"])
@login_required
def secrets():
    
    print(current_user.name)
    return render_template("secrets.html",name=current_user.name)

@app.route("/download",methods=["GET","POST"])
@login_required
def download():
    return send_from_directory("static","files/cheat_sheet.pdf")







@app.route("/login",methods=["GET","POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")


        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()


        if not user:
            flash("User does not found , Please register")
            return redirect(url_for("login"))
        
        elif not check_password_hash(user.password,password):
            flash("Password Incorrect , Please try again.")
            return redirect(url_for("login"))
         
        else:
            login_user(user)
            return redirect(url_for("secrets"))

        
        
    return render_template("login.html")





@app.route("/logout",methods=["GET","POST"])
def logout():
    logout_user()

    return render_template("index.html")




if __name__ == "__main__":
    app.run(host="0.0.0",debug=True)