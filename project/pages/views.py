from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from project import db
import time
from flask_login import login_required, current_user
import datetime
import pytz
from flask_wtf import csrf

from project.core.urlcode import url_encode, url_decode
from project.core.daynight import eval_time
from project.models import Notebooks, Pages, Desks
from project.core.sequencing import page_add, page_delete, page_insert, page_swap
from project.pages.forms import add_page_form, edit_page_form

pages = Blueprint('pages', __name__, template_folder = "templates/pages")

@pages.route('/<int:notebook_id>', methods=['GET', 'POST'])
def show(notebook_id):
    target_notebook = Notebooks.query.get(notebook_id)
    if target_notebook is None:
        flash('Sorry, a notebook with that ID does not exist.')
        return redirect(url_for('core.index'))
    if target_notebook.access_code == "" or (current_user.is_authenticated and target_notebook.owner == current_user.id):
        access = True
    else:
        if session.get('access_key'):
            if session['access_key'] == "{}-{}".format(target_notebook.id, target_notebook.access_code):
                access = True
            else:
                flash('Please enter the access code again.')
                access = False
        else:
            access = False



    if access == True:
        if "daynight_pref" in request.form:
            session['daynight_pref'] = request.form['daynight_pref']

        if request.args.get('p'):
            try:
                page_id = url_decode(request.args.get('p'))
            except:
                flash('There was something wrong with the page ID. Please do not type page IDs manually.')
                return redirect(url_for('pages.show', notebook_id = notebook_id))
            target_page = Pages.query.get(page_id)
            if target_page in target_notebook.pages:
                if target_page.next == 0:
                    next_page_url = 0
                else:
                    next_page_url = url_encode(target_page.next)

                if target_page.prior == 0:
                    prior_page_url = 0
                    return redirect(url_for('pages.show', notebook_id = target_notebook.id))
                else:
                    prior_page_url = url_encode(target_page.prior)

                if current_user.is_authenticated:
                    page_last_update = datetime.datetime.fromtimestamp(int(target_page.last_update)).astimezone(pytz.timezone(current_user.preferences.timezone)).strftime('%d %B, %Y')
                else:
                    page_last_update = datetime.datetime.fromtimestamp(int(target_page.last_update)).astimezone(pytz.timezone('Etc/GMT+7')).strftime('%d %B, %Y')

                return render_template('page.html', webtitle = "{} - {}".format(target_notebook.title, target_page.heading), daynight = eval_time(), notebook = target_notebook, page = target_page, next_page_url = next_page_url, prior_page_url = prior_page_url, page_url = url_encode(target_page.id), page_last_update = page_last_update)
            else:
                flash('The page you requested does not exist within this notebook.')
                return redirect(url_for('pages.show', notebook_id = target_notebook.id))
        else:
            # check if notebook is on active desk
            if current_user.is_authenticated:
                active_desk = Desks.query.get(current_user.active_desk)
                if active_desk in target_notebook.associated_desks:
                    added_to_desk = True
                else:
                    added_to_desk = False
            else:
                added_to_desk = False

            # show contents page
            all_pages = Pages.query.filter_by(notebook = target_notebook.id)

            page_dict = {}
            for page in all_pages:
                page_dict[page.id] = {'heading': page.heading, 'next': page.next, 'url': url_encode(page.id)}
            num_pages = len(page_dict)

            content_objects = []
            content_objects.append(page_dict[all_pages[0].id])


            for i in range(0, num_pages-1):
                content_objects.append(page_dict[content_objects[i]['next']])

            content_objects.pop(0)
            if len(content_objects) == 0:
                content_objects = 0
                next_page_url = 0
            else:
                next_page_url = content_objects[0]['url']

            if current_user.is_authenticated:
                creation_date = datetime.datetime.fromtimestamp(int(target_notebook.creation_date)).astimezone(pytz.timezone(current_user.preferences.timezone)).strftime('%d %B, %Y')
            else:
                creation_date = datetime.datetime.fromtimestamp(int(target_notebook.creation_date)).astimezone(pytz.timezone('Etc/GMT+7')).strftime('%d %B, %Y')

            return render_template('contents.html', webtitle = "{} - Content Page".format(target_notebook.title), daynight = eval_time(), notebook = target_notebook, page = all_pages[0], all_pages = content_objects, next_page_url = next_page_url, creation_date = creation_date, added_to_desk = added_to_desk)
    else:
        return redirect(url_for('notebooks.get_access', notebook_url = target_notebook.url))

@pages.route('/<int:notebook_id>/add', methods=['GET', 'POST'])
# @csrf.exempt
@login_required
def add_page(notebook_id):
    target_notebook = Notebooks.query.get(notebook_id)
    if current_user.id == target_notebook.owner:
        form = add_page_form()
        if form.validate_on_submit():
            new_page_id = page_add(form.heading.data, form.content.data, notebook_id, current_user.id)
            flash('The new page has been created!')
            return redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(new_page_id)))
        else:
            for field, error in form.errors.items():
                flash('{} ({} error)'.format(error[0], field))
        return render_template('addpage.html', webtitle = "Adding New Page to {}".format(target_notebook.title), daynight = eval_time(), form = form, notebook = target_notebook)
    else:
        flash("Sorry, you can't add pages to a notebook that doesn't belong to you!")
        return redirect(url_for('pages.show', notebook_id = notebook.id))


@pages.route('/<int:notebook_id>/insert', methods=['GET', 'POST'])
@login_required
def insert_page(notebook_id):
    if request.args.get('p'):
        page_id = int(url_decode(request.args.get('p')))
        target_notebook = Notebooks.query.get(notebook_id)
        if current_user.id == target_notebook.owner:
            form = add_page_form()
            if form.validate_on_submit():
                if request.args.get('pos'):
                    position = request.args.get('pos')
                else:
                    position = "before"
                new_page_id = page_insert(position = position, insertion_point = page_id, rec_heading = form.heading.data, rec_content = form.content.data, rec_notebook_id = notebook_id, rec_author = current_user.id)
                flash('The new page has been created!')
                return redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(new_page_id)))
            else:
                for field, error in form.errors.items():
                    flash('{} ({} error)'.format(error[0], field))
            return render_template('addpage.html', webtitle = "Inserting New Page to {}".format(target_notebook.title), daynight = eval_time(), form = form, notebook = target_notebook)
        else:
            flash("Sorry, you can't add pages to a notebook that doesn't belong to you!")
            return redirect('/notebooks/{}'.format(target_notebook.url))
    else:
        flash("You must specify a page ID.")
        return redirect(url_for('notebooks.show_notebook', notebook_id = notebook_id))


@pages.route('/<int:notebook_id>/edit', methods=['GET', 'POST'])
# @csrf.exempt
@login_required
def edit_page(notebook_id):
    if request.args.get('p'):
        page_id = int(url_decode(request.args.get('p')))
        target_notebook = Notebooks.query.get(notebook_id)
        if current_user.id == target_notebook.owner:
            target_page = Pages.query.get(page_id)
            form = edit_page_form(obj = target_page)
            if form.validate_on_submit():
                target_page.heading = form.heading.data
                target_page.content = form.content.data
                target_page.last_update = int(time.time())
                db.session.commit()
                flash('This page has been editted!')
                return redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(target_page.id)))
            else:
                for field, error in form.errors.items():
                    flash('{} ({} error)'.format(error[0], field))

            page_url = url_encode(target_page.id)
            return render_template('editpage.html', webtitle = "Editting a Page in {}".format(target_notebook.title), daynight = eval_time(), form = form, notebook = target_notebook, page = target_page, page_url = page_url)
        else:
            flash("Sorry, you can't edit pages on a notebook that doesn't belong to you!")
            return redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(target_page.id)))
    else:
        flash('You must provide a page ID')
        return redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(target_page.id)))


@pages.route('/<int:notebook_id>/delete')
@login_required
def delete_page(notebook_id):
    if request.args.get('p'):
        page_id = int(url_decode(request.args.get('p')))
        target_notebook = Notebooks.query.get(notebook_id)
        if current_user.id == target_notebook.owner:
            target_page = Pages.query.get(page_id)
            page_delete(page_id)
            db.session.delete(target_page)
            db.session.commit()
            flash('The page has been deleted.')
            return redirect(url_for('pages.show', notebook_id = notebook_id))
        else:
            flash("Sorry, you can't delete pages on a notebook that doesn't belong to you!")
            return redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(target_page.id)))
    else:
        flash('Please provide a page ID')
        redirect(url_for('pages.show', notebook_id = notebook_id, p = url_encode(target_page.id)))
