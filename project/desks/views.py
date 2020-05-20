from flask import render_template, url_for, flash, redirect, request, Blueprint
from project import db
from flask_login import login_required, current_user

from project.core.daynight import eval_time
from project.models import Users, Desks, Notebooks
from project.desks.forms import add_desk_form, edit_desk_form

desks = Blueprint('desks', __name__, template_folder = "templates/desks")

@desks.route('/')
@login_required
def index():
    active_desk = Desks.query.get(current_user.active_desk)

    #FIND NOTEBOOKS ON THIS DESK (many-to-many filter)
    desk_notebooks = Notebooks.query.filter(Notebooks.associated_desks.contains(active_desk))

    return render_template('desk.html', webtitle = "{} (My Active Desk)".format(active_desk.deskname), daynight = eval_time(), active_desk = active_desk, desk_notebooks = desk_notebooks)

@desks.route('/choose', methods=['GET', 'POST'])
@login_required
def choose_desk():
    all_desks = Desks.query.filter_by(owner = current_user.id)
    form = add_desk_form()
    if form.validate_on_submit():
        new_desk = Desks(deskname = form.deskname.data, desc = form.desc.data, owner = current_user.id)
        db.session.add(new_desk)
        db.session.commit()
        this_user = Users.query.get(current_user.id)
        this_user.active_desk = new_desk.id
        db.session.commit()
        flash("The new desk has been created! I've gone ahead and switched you over by making it your active desk! If you don't want that, activate a different desk below.")
        return redirect(url_for('desks.choose_desk'))
    else:
        for field, error in form.errors.items():
            flash('{} ({} error)'.format(error[0], field))

    return render_template('choosedesk.html', webtitle = "Switch Desk", daynight = eval_time(), all_desks = all_desks, form = form)

@desks.route('/activate')
@login_required
def activate_desk():
    if request.args.get('selection') is None:
        flash('You did not select a desk to activate, please try again.')
        return redirect(url_for('desks.choose_desk'))
    else:
        selection = int(request.args.get('selection'))
        this_user = Users.query.get(current_user.id)
        this_user.active_desk = selection
        db.session.commit()
        flash("You've been switched to your selected desk!")
        return redirect(url_for('desks.index'))

@desks.route('/manage', methods=['GET', 'POST'])
@login_required
def manage_desk():
    if request.args.get('selection') is None:
        flash('You did not select a desk to manage, please try again.')
        return redirect(url_for('desks.choose_desk'))
    else:
        selection = int(request.args.get('selection'))
        target_desk = Desks.query.get(selection)
        active_desk = Desks.query.get(current_user.active_desk)
        desk_notebooks = Notebooks.query.filter(Notebooks.associated_desks.contains(target_desk))
        form = edit_desk_form(obj = target_desk)
        if form.validate_on_submit():
            target_desk.deskname = form.deskname.data
            target_desk.desc = form.desc.data
            db.session.commit()
            flash("'{}' has been editted.".format(target_desk.deskname))
            return redirect(url_for('desks.choose_desk'))
        else:
            for field, error in form.errors.items():
                flash('{} ({} error)'.format(error[0], field))
        return render_template('managedesk.html', webtitle = "Manage My Desk", daynight = eval_time(), form = form, desk_notebooks = desk_notebooks, desk_id = target_desk.id)

@desks.route('/delete')
@login_required
def delete_desk():
    if request.args.get('selection') is None:
        flash('You did not select a desk to delete, please try again.')
        return redirect(url_for('desks.choose_desk'))
    else:
        if Desks.query.filter_by(owner = current_user.id).count() != 1:

            selection = int(request.args.get('selection'))
            target_desk = Desks.query.get(selection)

            if current_user.id == target_desk.owner:
                if current_user.active_desk == target_desk.id:
                    flash("You deleted your current active desk. I went ahead and switched you to your next available desk. We all need somewhere to sit at!")
                target_desk.notebooks = []
                db.session.delete(target_desk)
                this_user = Users.query.get(current_user.id)
                this_user.active_desk = Desks.query.filter_by(owner = current_user.id).first().id
                db.session.commit()
                flash("The selected desk has been deleted.")
            else:
                flash("Sorry but you can't delete someone else's desk.")

            return redirect(url_for('desks.choose_desk'))
        else:
            flash('You cannot delete your last desk, where will you sit at?')
            return redirect(url_for('desks.choose_desk'))
