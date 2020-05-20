from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from project import db
import time
from flask_login import login_required, current_user
from project.core.daynight import eval_time

from project.models import Desks, Notebooks, Pages, Users
from project.notebooks.forms import add_notebook_form, edit_notebook_form, notebook_form, get_access_form

notebooks = Blueprint('notebooks', __name__, template_folder = "templates/notebooks")


@notebooks.route('/')
def index():
    return render_template('featured.html', webtitle = "Featured Notebooks", daynight = eval_time())

@notebooks.route('/<string:username>')
def profile(username):
    target_user = Users.query.filter_by(username = username).first()
    user_notebooks = Notebooks.query.filter_by(owner = target_user.id).filter_by(visibility = "PUBLIC").order_by(Notebooks.id.desc())

    if current_user.is_authenticated:
        if current_user.id == target_user.id:
            private_notebooks = Notebooks.query.filter_by(owner = current_user.id).filter_by(visibility = "PRIVATE").order_by(Notebooks.id.desc())
            if private_notebooks.count() == 0:
                private_notebooks = 0
        else:
            private_notebooks = 0
    else:
        private_notebooks = 0

    return render_template('profile.html', webtitle = "{}'s Notebooks".format(username), daynight = eval_time(), username = username, notebooks = user_notebooks, private_notebooks = private_notebooks, target_user = target_user)


@notebooks.route('/<string:username>/<string:notebook_url>/')
def show_notebook(username, notebook_url):
    target_notebook = Notebooks.query.filter_by(url = notebook_url).first()
    if target_notebook is None:
        flash('Sorry, a notebook with that URL does not exist.')
        return redirect(url_for('core.index'))
    if target_notebook.associated_user.username == username:
        return redirect(url_for('pages.show', notebook_id = target_notebook.id))
    else:
        flash("Sorry but {} doesn't have the notebook you specified.")
        return redirect(url_for('users.profile'))


@notebooks.route('/<string:notebook_url>/getaccess', methods = ['GET', 'POST'])
def get_access(notebook_url):
    target_notebook = Notebooks.query.filter_by(url = notebook_url).first()
    form = get_access_form()
    if form.validate_on_submit():
        if form.access_code.data == target_notebook.access_code:
            session['access_key'] = "{}-{}".format(target_notebook.id, target_notebook.access_code)
            flash('Access code accepted!')
            return redirect(url_for('pages.show', notebook_id = target_notebook.id))
        else:
            flash('Sorry, the access code you entered was incorrect.')
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))
    return render_template('access.html', daynight = eval_time(), webtitle = "Access Code Required For {}".format(target_notebook.title), form = form)


@notebooks.route('/add', methods=['POST', 'GET'])
@login_required
def add_notebook():
    if request.args.get('notebook_id') is None:
        # create a new notebook
        recent_notebooks = Notebooks.query.filter_by(owner = current_user.id).order_by(Notebooks.id.desc())
        form = add_notebook_form()
        if form.validate_on_submit():
            if form.cover_img.data == "":
                form.cover_img.data = "https://www.fluidnotebook.com/static/images/default-cover.png"
            if form.access_code.data != "":
                visibility = "PRIVATE"
            else:
                visibility = "PUBLIC"
            active_desk = Desks.query.get(current_user.active_desk)
            new_notebook = Notebooks(title = form.title.data, desc = form.desc.data, creation_date = int(time.time()), last_update = int(time.time()), visibility = visibility, access_code = form.access_code.data, url = form.url.data, cover_img = form.cover_img.data, owner = current_user.id)
            db.session.add(new_notebook)
            active_desk.notebooks.append(new_notebook)
            db.session.commit()
            new_page = Pages(prior = 0, next = 0, heading = "Content Page", content = "", last_update = int(time.time()), notebook = new_notebook.id, author = current_user.id)
            db.session.add(new_page)
            db.session.commit()
            flash('Your new notebook has been created and is added to your active desk!')
            return redirect(url_for('desks.index'))
        else:
            for field, error in form.errors.items():
                flash('{} ({} error)'.format(error[0], field))
        return render_template('add.html', webtitle = "Adding New Notebook to Desk", daynight = eval_time(), form = form, recent_notebooks = recent_notebooks)
    else:
        # add to active desk
        selection = request.args.get('notebook_id')
        target_notebook = Notebooks.query.get(selection)
        active_desk = Desks.query.get(current_user.active_desk)
        if target_notebook in active_desk.notebooks:
            flash('The notebook you selected already exists on your active desk ({})'.format(active_desk.deskname))
            return redirect(url_for('desks.index'))
        else:
            active_desk.notebooks.append(target_notebook)
            db.session.commit()
            flash('The selected notebook has been added to your active desk!')
            return redirect(url_for('desks.index'))


@notebooks.route('/remove')
@login_required
def remove_notebook():
    if request.args.get('notebook_id') is None or request.args.get('desk_id') is None:
        flash('You did not select a notebook to remove from your desk.')
        return redirect(url_for('desks.manage_desk'))
    else:
        notebook_selection = int(request.args.get('notebook_id'))
        desk_selection = int(request.args.get('desk_id'))
        target_notebook = Notebooks.query.get(notebook_selection)
        target_desk = Desks.query.get(desk_selection)
        if current_user.id == target_desk.owner:
            target_desk.notebooks.remove(target_notebook)
            db.session.commit()
            flash("The notebook has been removed from your desk. Your notebook is not deleted though, you can reassign it to another desk, or you can choose the 'delete notebook' option when you open it.")
            if request.args.get('backref'):
                return redirect(url_for('pages.show', notebook_id=request.args.get('backref')))
            else:
                return redirect(url_for('desks.manage_desk', selection=target_desk.id))
        else:
            flash("You cannot remove notebooks from a desk that doesn't belong to you.")
            return redirect(url_for('desks.manage_desk'))

@notebooks.route('/edit/<string:notebook_url>', methods = ['POST', 'GET'])
@login_required
def edit_notebook(notebook_url):
    target_notebook = Notebooks.query.filter_by(url = notebook_url).first()
    if current_user.id == target_notebook.owner:
        form = edit_notebook_form(obj = target_notebook)
        if form.validate_on_submit():
            target_notebook.title = form.title.data
            target_notebook.desc = form.desc.data
            target_notebook.last_update = int(time.time())
            if form.access_code.data == "":
                target_notebook.visibility = "PUBLIC"
            else:
                target_notebook.visibility = "PRIVATE"
            target_notebook.access_code = form.access_code.data
            target_notebook.url = form.url.data
            target_notebook.cover_img = form.cover_img.data
            db.session.commit()
            flash('The notebook has been editted.')
            return redirect('/nb/{}'.format(target_notebook.id))
        else:
            for field, error in form.errors.items():
                flash('{} ({} error)'.format(error[0], field))
        return render_template('edit.html', webtitle = "Editting a Notebook", daynight = eval_time(), form = form, notebook = target_notebook)
    else:
        flash("Sorry pal, I can't let you edit someone else's notebook. Your login session may have timed out.")
        return redirect('/notebooks/{}'.format(notebook_url))


@notebooks.route('/delete/<int:notebook_id>')
@login_required
def delete_notebook(notebook_id):
    target_notebook = Notebooks.query.get(notebook_id)
    if current_user.id == target_notebook.owner:
        target_notebook.associated_desks = []
        db.session.delete(target_notebook)
        db.session.commit()
        flash("The notebook has been permanently deleted. It cannot be recovered.")
        return redirect(url_for('desks.index'))
    else:
        flash("You can't delete this notebook because it doesn't belong to you. Your login session may have timed out.")
        return redirect('/notebooks/{}'.format(target_notebook.url))

@notebooks.route('/show_all', methods = ['GET','POST'])
@login_required
def show_all():
    search_results = Notebooks.query.filter_by(owner = current_user.id)
    all_notebooks = search_results

    if request.args.get('query'):
        search_term = request.args.get('query')
    else:
        search_term = ""


    if request.args.get('type') and request.args.get('sort'):
        if search_term == "":
            flash('No search term entered, showing all notebooks.')

        if request.args.get('type') == 'desc':
            search_results = search_results.filter(Notebooks.desc.contains(search_term))
        else:
            search_results = search_results.filter(Notebooks.title.contains(search_term))

        if request.args.get('sort') == 'recency_old':
            search_results = search_results.order_by(Notebooks.id.asc())
        elif request.args.get('sort') == 'alphabetical':
            search_results = search_results.order_by(Notebooks.title)
        else:
            search_results = search_results.order_by(Notebooks.id.desc())

    else:
        search_results = search_results.order_by(Notebooks.id.desc())

    if search_results.count() == 0:
        search_results = 0

    return render_template('show_all.html', webtitle="All My Notebooks", daynight = eval_time(), all_notebooks = all_notebooks, search_results = search_results)
