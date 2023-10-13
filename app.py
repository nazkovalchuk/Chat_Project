from flask import Flask, render_template, redirect, request, session

import siteUtil
from datetime import *
mapOfMes = {}
userMap = {}
codeMap = {}
attemptsMap = {}
hourMap = {}
regcodeMap = {}


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["SESSION_PERMANENT"] = False
        self.app.config["SESSION_TYPE"] = "filesystem"
        self.app.secret_key = "123457890qwerty"

        # тут кожному класу вставляєш епп
        self.login_page = LoginPage(self.app)
        self.main_page = MainPage(self.app)
        self.signup_page = SignUpPage(self.app)
        self.forgotpass_page = ForgotPassPage(self.app)

    def run(self):
        self.app.run(debug=True)


class LoginPage:
    def __init__(self, app):
        self.app = app

        @app.route("/login", methods=["POST", "GET"])
        def login():
            if session.get("username") is not None:
                return redirect("/")
            if request.method == "POST":
                username = request.form.get("username").strip()
                password = request.form.get("password")

                if username not in userMap:
                    return render_template("login.html", error="There is no such account: " + username)
                elif password != userMap.get(username):
                    return render_template("login.html", error="Wrong password!")

                session["username"] = username
                if username not in mapOfMes:
                    mapOfMes[username] = []

                return redirect("/")

            return render_template("login.html")

        @app.route("/logout")
        def logout():
            session["username"] = None
            return redirect("/")

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def catch_all(path):
            return redirect("/")


class MainPage:
    def __init__(self, app):
        self.app = app

        @app.route("/")
        def main():
            if session.get("username") is None:
                return redirect("/login")

            l = mapOfMes.get(session.get('username'))
            if l is None:
                l = ''

            return render_template('main.html', response=l, error='')

        @app.route("/message/0", methods=["POST"])
        def message():
            if session.get("username") is None:
                return redirect("/login")

            # насправді це треба буде в базу даних ставити а не в сешин
            message = request.form.get("message")
            if message is None or len(message) == 0:
                l = mapOfMes.get(session.get('username'))
                if l is None:
                    l = ''
                return render_template('main.html', response=l, error="Message can't be empty!")

            temp = []
            if mapOfMes.get(session.get('username')):
                temp += mapOfMes.get(session.get('username'))
            temp.insert(0, {'sender': 'user', 'text': message})
            global realStringAIMessages
            realStringAIMessages += "User: " + message + "; Nolan: "
            response = siteUtil.get_gpt3_response(realStringAIMessages).replace("\n", "<br>")
            realStringAIMessages += response + ";"
            response = response.strip()
            while response.startswith("<br>"):
                response = response.replace("<br>", "")
            temp.insert(0, {'sender': 'AI', 'text': response})

            mapOfMes.update({session.get('username'): temp})

            return redirect("/")


class SignUpPage:
    def __init__(self, app):
        self.app = app

        @app.route("/signup", methods=["GET"])
        def signup():
            if session.get("username") is not None:
                return redirect("/")

            return render_template("signup.html", device="Mobile", error='')

        @app.route("/signup2", methods=["POST"])
        def signup2():
            if session.get("username") is not None:
                return redirect("/")

            username = request.form.get("username").strip()
            password = request.form.get("password")
            password2 = request.form.get("password2")

            if username in userMap:
                return render_template("signup.html", error="There is already account with this email!",
                                       username=username, password=password, password2=password2)
            elif len(username) == 0:
                return render_template("signup.html", error="Email can't be empty!", username=username,
                                       password=password, password2=password2)
            elif not siteUtil.validEmail(username):
                return render_template("signup.html", error="Invalid email!", username=username, password=password,
                                       password2=password2)
            elif len(password) < 8:
                return render_template("signup.html", error="Passwords length must be at least 8!", username=username,
                                       password=password, password2=password2)
            elif not siteUtil.strongPass(password):
                return render_template("signup.html",
                                       error="Password is not strong, it should contain uppercase, lowercase, digits and special characters like !_*",
                                       username=username, password=password, password2=password2)
            elif password != password2:
                return render_template("signup.html", error="Passwords must match!", username=username,
                                       password=password, password2=password2)

            session['reguser'] = username
            session['regpass'] = password2
            regcode = siteUtil.generateCodeEmail()
            regcodeMap[username] = regcode
            siteUtil.sendCodeToEmail(username, regcode)
            # database add all this info
            return render_template("enterregcode.html", username=username)

        @app.route("/regcode", methods=["POST"])
        def regcode():
            if session.get("username") is not None:
                return redirect("/")
            codefromUser = request.form.get('code')
            if regcodeMap[session['reguser']] == codefromUser:
                userMap[session['reguser']] = session['regpass']
                session['username'] = session['reguser']
                session['reguser'] = None
                session['regpass'] = None
                return redirect('/login')
            return render_template("enterregcode.html", username=session['reguser'], error="Codes don't match!")


class ForgotPassPage:
    def __init__(self, app):
        self.app = app

        @app.route("/forgotpass")
        def forgotPass():
            x = datetime.strptime("11/03/22 14:23", "%d/%m/%y %H:%M")
            hour = str(x.time())[0:2]
            if session.get("username") is not None:
                return redirect("/")
            if hour == hourMap.get(session.get('usernameForRecovery')):
                return render_template("forgotpass.html", username=session.get('usernameForRecovery'),
                                       error="You exceed attempts limit | You would be able to reset password again in 1 hour")

            return render_template("forgotpass.html")

        @app.route("/forgotpass2", methods=["POST"])
        def forgotPass2():
            x = datetime.strptime("11/03/22 14:23", "%d/%m/%y %H:%M")
            hour = str(x.time())[0:2]

            if session.get("username") is not None:
                return redirect("/")
            if hour == hourMap.get(session.get('usernameForRecovery')):
                return render_template("forgotpass.html", username=session.get('usernameForRecovery'),
                                       error="You exceed attempts limit | You would be able to reset password again in 1 hour")

            username = request.form.get("username").strip()
            if username not in userMap:
                return render_template("forgotpass.html", error="There is no such account: " + username)
            session['usernameForRecovery'] = username

            # generate and send code to user email API and save code to Database
            code = siteUtil.generateCodeEmail()
            codeMap[username] = code
            siteUtil.sendCodeToEmail(username, code)
            attemptsMap[username] = 4

            return render_template("entercode.html", username=username)

        @app.route("/code", methods=["POST"])
        def code():
            x = datetime.strptime("11/03/22 14:23", "%d/%m/%y %H:%M")
            hour = str(x.time())[0:2]

            if session.get("username") is not None:
                return redirect("/")
            if hour == hourMap.get(session.get('usernameForRecovery')):
                return render_template("entercode.html", username=session.get('usernameForRecovery'),
                                       error="You exceed attempts limit | You would be able to reset password again in 1 hour")

            username = session.get('usernameForRecovery')
            codefromDatabase = codeMap.get(username)
            codefromUser = request.form.get("code").strip()

            if codefromDatabase == codefromUser:
                # here we will assign 3 attemts again to database
                codeMap[username] = "1"
                attemptsMap[username] = 4
                return redirect("/createpass")
            else:

                if attemptsMap[username] <= 1:
                    x = datetime.strptime("11/03/22 14:23", "%d/%m/%y %H:%M")
                    hour = str(x.time())[0:2]
                    hourMap[username] = hour
                    print(hour)
                    print(hourMap[username])
                    return render_template("entercode.html", username=username,
                                           error="You exceed attempts limit | You would be able to reset password again in 1 hour")

                # here we will be decreasing attemts from database
                attemptsMap[username] -= 1
                attemptsLeft = str(attemptsMap.get(username))

                return render_template("entercode.html", username=username,
                                       error="Codes don't match | You have got " + attemptsLeft + " attempts left")

        @app.route("/createpass")
        def createpass():
            x = datetime.strptime("11/03/22 14:23", "%d/%m/%y %H:%M")
            hour = str(x.time())[0:2]
            if session.get("username") is not None:
                return redirect("/")
            if hour == hourMap.get('usernameForRecovery'):
                return render_template("entercode.html", username=session.get('usernameForRecovery'),
                                       error="You exceed attempts limit | You would be able to reset password again in 1 hour")

            return render_template("createpass.html", username=session.get('usernameForRecovery'))

        @app.route("/createpass2", methods=["POST"])
        def createpass2():
            x = datetime.strptime("11/03/22 14:23", "%d/%m/%y %H:%M")
            hour = str(x.time())[0:2]
            if session.get("username") is not None:
                return redirect("/")
            if hour == hourMap.get('usernameForRecovery'):
                return render_template("createpass.html", username=session.get('usernameForRecovery'),
                                       error="You exceed attempts limit | You would be able to reset password again in 1 hour")

            username = session.get('usernameForRecovery')
            newPassword = request.form.get('newpass')
            newPassword2 = request.form.get('newpass2')

            if len(newPassword) < 8:
                return render_template("createpass.html", error="Password length must be at least 8!")
            elif not siteUtil.strongPass(newPassword):
                return render_template("createpass.html",
                                       error="Password is not strong, it should contain uppercase, lowercase, digits and special characters like !_*")
            elif newPassword != newPassword2:
                return render_template("createpass.html", error="Passwords must match", username=username)

            # add new data to database
            session['username'] = username
            session['usernameForRecovery'] = None

            userMap[username] = newPassword2

            return redirect("/")


if __name__ == "__main__":
    app = App()
    app.run()
