from flask import render_template, url_for, flash, redirect, request, Blueprint
from project import db
from flask_login import login_required, current_user

from project.models import Users, Desks, Notebooks, desks_to_notebooks, Pages, Reports, Preferences

from project.core.daynight import eval_time

admin = Blueprint('admin', __name__, template_folder = "templates/admin")



@admin.route('/', methods=['GET','POST'])
@login_required
def index():
    if current_user.role == "admin":
        all_reports = Reports.query.order_by(Reports.id.desc())
        if all_reports.count() == 0:
            all_reports = 0

        users_count = db.session.query(Users).count()
        notebooks_count = db.session.query(Notebooks).count()
        pages_count = db.session.query(Pages).count()

        newest_users = Users.query.order_by(Users.id.desc()).limit(5)
        newest_notebooks = Notebooks.query.order_by(Notebooks.id.desc()).limit(3)

        return render_template('dashboard.html', webtitle = "Admin Dashboard", daynight = eval_time(),
            all_reports = all_reports,
            users_count = users_count,
            notebooks_count = notebooks_count,
            pages_count = pages_count,
            newest_notebooks = newest_notebooks,
            newest_users = newest_users)
    else:
        flash("Sorry but you're not authorized to use the admin dashboard. It's nothing personal, I promise!")
        return redirect(url_for('core.index'))


@admin.route('/check_tables/<string:table>')
@login_required
def check(table):
    if current_user.role == "admin":
        # table headings
        users_headings = ('id', 'username', 'email', 'password', 'bio', 'pic', 'role', 'active_desk', 'delete')
        desks_headings = ('id', 'deskname', 'desc', 'owner (FK)', 'delete')
        notebooks_headings = ('id', 'owner', 'title', 'desc', 'creation_date', 'last_update', 'V', 'access_code', 'url', 'cover_img', 'delete')
        pages_headings = ('id', 'prior', 'next', 'heading', 'content', 'last_update', 'notebook (FK)', 'author (FK)', 'delete')
        preferences_headings = ('id', 'timezone', 'night_time_on', 'night_time_off', 'night_mode_type', 'font_size', 'coding_addon', 'hyperlinks_addon', 'colors_addon', 'user_id', 'delete')
        relational_headings = ('desk_id', 'notebook_id')

        if table == "users":
            table_headings = users_headings
            table_contents = Users.query.all()

        elif table == "desks":
            table_headings = desks_headings
            table_contents = Desks.query.all()

        elif table == "notebooks":
            table_headings = notebooks_headings
            table_contents = Notebooks.query.all()

        elif table == "pages":
            table_headings = pages_headings
            table_contents = Pages.query.all()

        elif table == "preferences":
            table_headings = preferences_headings
            table_contents = Preferences.query.all()

        elif table == "relational":
            table_headings = relational_headings
            table_contents = db.session.query(desks_to_notebooks)

        return render_template('table.html', webtitle = "Checking Table", daynight = eval_time(), table_headings = table_headings, table_contents = table_contents, table = table)

    else:
        flash("Sorry but you're not authorized to use the admin dashboard. It's nothing personal, I promise!")
        return redirect(url_for('core.index'))



@admin.route('/old')
@login_required
def old():
    if current_user.role == "admin":
        all_users = Users.query.all()
        all_desks = Desks.query.all()
        all_notebooks = Notebooks.query.all()
        all_pages = Pages.query.all()
        rel_table = db.session.query(desks_to_notebooks)
        reports_table = Reports.query.all()
        preferences_table = Preferences.query.all()
        return render_template('tables.html', all_users = all_users, all_desks = all_desks, all_notebooks = all_notebooks, rel_table = rel_table, all_pages = all_pages, reports_table = reports_table, preferences_table = preferences_table)
    else:
        flash("Sorry but you're not authorized to use the admin dashboard. It's nothing personal, I promise!")
        return redirect(url_for('core.index'))




@admin.route('/delete/<string:model_name>/<int:id>')
@login_required
def delete_row(model_name, id):
    if current_user.role == "admin":
        if model_name == "desks":
            target_desk = Desks.query.get(id)
            db.session.delete(target_desk)

        elif model_name == "notebooks":
            target_notebook = Notebooks.query.get(id)
            db.session.delete(target_notebook)

        elif model_name == "users":
            target_user = Users.query.get(id)
            db.session.delete(target_user)

        elif model_name == "pages":
            target_page = Pages.query.get(id)
            db.session.delete(target_page)

        elif model_name == "preferences":
            target_pref = Preferences.query.get(id)
            db.session.delete(target_pref)

        elif model_name == "reports":
            target_report = Reports.query.get(id)
            db.session.delete(target_report)

        db.session.commit()
        if "fluidnotebook.com" in request.headers.get("Referer") or "127.0.0.1" in request.headers.get("Referer"):
            return redirect(request.headers.get("Referer"))
        else:
            return redirect(url_for('admin.index'))
    else:
        flash("Sorry but you're not authorized to use the admin dashboard. It's nothing personal, I promise!")
        return redirect(url_for('core.index'))

@admin.route('/exe')
@login_required
def execute():
    if current_user.role == "admin":
        fluid = Users.query.get(2)
        fluid.role = "admin"
        db.session.commit()
        flash('The command has been executed.')
        return redirect(url_for('admin.index'))
    else:
        flash("Sorry but you're not authorized to use the admin dashboard. It's nothing personal, I promise!")
        return redirect(url_for('core.index'))


@admin.route('/prune/<string:table>')
@login_required
def prune(table):
    if current_user.role == "admin":

        if table == "pages":
            db.session.query(Pages).filter(Pages.notebook == None).delete()
            db.session.query(Pages).filter(Pages.author == None).delete()
            db.session.commit()
        elif table == "preferences":
            db.session.query(Preferences).filter(Preferences.user_id == None).delete()
            db.session.commit()

        flash('The prune command has been executed.')
        return redirect(url_for('admin.index'))
    else:
        flash("Sorry but you're not authorized to use the admin dashboard. It's nothing personal, I promise!")
        return redirect(url_for('core.index'))
