from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from project import db, mail
from flask_mail import Message
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from project.core.daynight import eval_time
import time

#forms
from project.users.forms import login_form, registration_form, changePassword_form, report_form, preferences_form, profile_form, pw_reset_form, pw_reset_request_form, email_login_form

# #models
from project.models import Users, Desks, Reports, Preferences


accounts = Blueprint('users', __name__, template_folder = "templates/users")

@accounts.route('/login', methods=['POST', 'GET'])
def login():
    form = login_form()
    if form.validate_on_submit():
        this_user = Users.query.filter_by(username = form.username.data.lower()).first()
        if this_user is not None and this_user.check_password(form.password.data):
            login_user(this_user)
            flash('Logged In')
            next = request.args.get('next')
            if next == None or not next[0]=='/':
                next = url_for('desks.index')
            return redirect(next)
        else:
            flash('You have provided a wrong username or password.')
            return redirect(url_for('users.login'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('login.html', webtitle = "Log In", daynight = eval_time(), form = form)


@accounts.route('/email_login', methods=['POST', 'GET'])
def email_login():
    form = email_login_form()
    if form.validate_on_submit():
        this_user = Users.query.filter_by(email = form.email.data.lower()).first()
        if this_user is not None and this_user.check_password(form.password.data):
            login_user(this_user)
            flash('Logged In')
            next = request.args.get('next')
            if next == None or not next[0]=='/':
                next = url_for('desks.index')
            return redirect(next)
        else:
            flash('You have provided a wrong email or password.')
            return redirect(url_for('users.email_login'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('email_login.html', webtitle = "Log In", daynight = eval_time(), form = form)



@accounts.route('/signup', methods=['POST', 'GET'])
def register():
    form = registration_form()
    if form.validate_on_submit():
        new_user = Users(username = form.username.data.lower(), email = form.email.data, password = form.password.data, bio = "", pic = "https://www.fluidnotebook.com/static/images/defaultavatar.png", active_desk = 0)
        db.session.add(new_user)
        db.session.commit()
        new_desk = Desks(deskname = "Main Desk", desc = ("The primary desk that's setup for {}.".format(new_user.username)), owner = new_user.id)
        db.session.add(new_desk)
        db.session.commit()
        new_user.active_desk = new_desk.id
        user_prefs = Preferences(timezone = "Etc/GMT+8", night_on = 21, night_off = 7, night_type = "dark", font_size = "18", coding_addon = 0, hyperlinks_addon = 0, colors_addon = 0, user_id = new_user.id)
        db.session.add(user_prefs)
        db.session.commit()
        flash("Your account has been registered, please log in!")
        return redirect(url_for('users.login'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('register.html', webtitle = "Register an Account", daynight = eval_time(), form = form)


@accounts.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('core.index'))


@accounts.route('/change_password', methods = ['GET', 'POST'])
@login_required
def change_password():
    this_user = Users.query.get(current_user.id)
    form = changePassword_form()
    if form.validate_on_submit():
        if this_user.check_password(form.current_pw.data):
            this_user.password = generate_password_hash(form.new_pw.data)
            db.session.commit()
            flash('Password Changed.')
            return redirect(url_for('users.settings'))
        else:
            print(generate_password_hash(form.current_pw.data))
            print(this_user.password)
            flash('Your current password is wrong, please try again.')
            return redirect(url_for('users.change_password'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('changepassword.html', webtitle = "Change Password", daynight = eval_time(), form = form)



@accounts.route('/report', methods = ['POST', 'GET'])
def report():
    form = report_form()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            reporter = current_user.username
        else:
            reporter = "unauthenticated"
        new_report = Reports(type = form.type.data, url = form.url.data, content = form.content.data, user = reporter, date = int(time.time()))
        db.session.add(new_report)
        db.session.commit()
        flash('Your report has been submitted, thank you!')
        return redirect(url_for('users.report'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('report.html', webtitle = "Report", daynight = eval_time(), form = form)



@accounts.route('/myinfo', methods = ['POST', 'GET'])
@login_required
def change_info():
    target_user = Users.query.get(current_user.id)
    form = profile_form(obj = target_user)
    if form.validate_on_submit():
        target_user.bio = form.bio.data
        target_user.email = form.email.data
        target_user.pic = form.pic.data
        db.session.commit()
        flash('Your details have been updated.')
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('myinfo.html', webtitle = "My Information", daynight = eval_time(), form = form)



@accounts.route('/settings', methods = ['POST', 'GET'])
@login_required
def settings():
    return render_template('settings.html', webtitle = "Settings", daynight = eval_time())



@accounts.route('/preferences', methods = ['GET', 'POST'])
@login_required
def preferences():
    user_prefs = Preferences.query.filter_by(user_id = current_user.id).first()
    form = preferences_form(obj = user_prefs)
    if form.validate_on_submit():
        user_prefs.timezone = form.timezone.data
        user_prefs.night_time_on = form.night_time_on.data
        user_prefs.night_time_off = form.night_time_off.data
        user_prefs.night_mode_type = form.night_mode_type.data
        user_prefs.font_size = form.font_size.data
        user_prefs.coding_addon = form.coding_addon.data
        user_prefs.hyperlinks_addon = form.hyperlinks_addon.data
        user_prefs.colors_addon = form.colors_addon.data
        db.session.commit()
        flash('Settings Updated.')
        return redirect(url_for('users.settings'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('preferences.html', webtitle = "Account Preferences", daynight = eval_time(), form = form)



@accounts.route('/device', methods = ['GET', 'POST'])
def device_settings():
    if "modified_settings" in request.form:
        if request.form['daynight_pref'] != "AUTO":
            session['daynight_pref'] = request.form['daynight_pref']
        elif request.form['daynight_pref'] == "AUTO" and session.get('daynight_pref'):
            session.pop('daynight_pref')

        if request.form['font_size_pref'] != "AUTO":
            session['font_size_pref'] = request.form['font_size_pref']
        session['keywords_pref'] = request.form['keywords_pref']

        if "editor_pref" in request.form:
            session['editor_pref'] = request.form['editor_pref']


    if request.args.get('clear'):
        if request.args.get('clear') == "session":
            if session.get('daynight_pref'):
                session.pop('daynight_pref')
            if session.get('font_size_pref'):
                session.pop('font_size_pref')
            if session.get('keywords_pref'):
                session.pop('keywords_pref')
            if session.get('editor_pref'):
                session.pop('editor_pref')

            flash('Your device-specific settings have been cleared.')

    return render_template('device_settings.html', webtitle = "Device-Specific Settings", daynight = eval_time())



@accounts.route('/forgot_password', methods = ['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        flash("Actually, you're already logged in.")
        return redirect(url_for('core.index'))
    else:
        form = pw_reset_request_form()
        if form.validate_on_submit():
            target_user = Users.query.filter_by(email = form.email.data).first()
            token = target_user.get_reset_token()
            email_message = Message('Password Reset Request', sender = 'noreply@sensworks.ca', recipients = [target_user.email])
            email_message.body = f"""Hey {target_user.username}, \n
I heard that you forgot your password for your account at Fluid Notebook. Please click on the following link to reset it. \n
{url_for('users.reset_password', token = token, _external = True)}\n
This link will expire in 30 mins, please do not share it with anyone, as they'll be able to change your password.\n\n
Thanks for using Fluid Notebook!\n
Daryl"""
            mail.send(email_message)
            flash("An email has been sent to the email address we have on file. Please check that email for instructions. If you do not see an email from noreply@sensworks.ca, please check your junk mail. If you're experiencing problems recovering your account, please send contact us.")
            return redirect(url_for('users.login'))
        else:
            for field, error in form.errors.items():
                flash('{} ({} error)'.format(error[0], field))
        return render_template('forgot_password.html', webtitle = "Forgot Password", daynight = eval_time(), form = form)



@accounts.route('/reset_password/<string:token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash("Actually, you're already logged in.")
        return redirect(url_for('core.index'))
    else:
        target_user = Users.verify_reset_token(token)
        if target_user is None:
            flash('The token is invalid or has expired.')
            return redirect(url_for('users.login'))
        else:
            form = pw_reset_form()
            if form.validate_on_submit():
                target_user.password = generate_password_hash(form.password.data)
                db.session.commit()
                flash('Your password has been changed, please login now.')
                return redirect(url_for('users.login'))
            else:
                for field, error in form.errors.items():
                    flash('{} ({} error)'.format(error[0], field))

        return render_template('reset_password.html', webtitle = "Set New Password", daynight = eval_time(), form = form)
