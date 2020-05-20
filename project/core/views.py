from flask import render_template, url_for, flash, redirect, request, Blueprint
from project import db
from project.models import Notebooks, Desks
from project.core.daynight import eval_time


core = Blueprint('core', __name__, template_folder = "templates/core")

@core.route('/')
def index():
    recent_notebooks = Notebooks.query.filter_by(visibility = "PUBLIC").order_by(Notebooks.last_update.desc()).limit(10)
    featured_table = Desks.query.filter_by(owner = 2).filter_by(deskname = "Featured").first()
    if featured_table is not None:
        featured_notebooks = Notebooks.query.filter(Notebooks.associated_desks.contains(featured_table))
    else:
        featured_notebooks = [Notebooks(title = "Featured desk is missing.", desc = "", creation_date = "", last_update = "", visibility = "PUBLIC", access_code = "", url = "", cover_img = "", owner = 1)]
    return render_template('index.html', webtitle = "Homepage", daynight = eval_time(), recent_notebooks = recent_notebooks, featured_notebooks = featured_notebooks)


@core.route('/search', methods=['GET'])
def search():
    if request.args.get('query'):
        search_term = request.args.get('query')
        search_results = Notebooks.query.filter_by(visibility = "PUBLIC").filter(Notebooks.title.contains(search_term))
        if search_results.count() == 0:
            search_results = 0

        # if current_user.is_authenticated:
        #     personal_results = Notebooks.query.filter_by(owner = current_user.id).filter(Notebooks.title.contains(search_term))
        #     if personal_results is None:
        #         personal_results = 0
        # else:
        #     personal_results = 0
    else:
        search_results = 0


    return render_template('search.html', webtitle = "Search", daynight = eval_time(), search_results = search_results)



@core.route('/info')
def info():
    info_table = Desks.query.filter_by(owner = 2).filter_by(deskname = "Info").first()
    if info_table is not None:
        info_notebooks = Notebooks.query.filter(Notebooks.associated_desks.contains(info_table))
    else:
        info_notebooks = [Notebooks(title = "Info desk is missing.", desc = "", creation_date = "", last_update = "", visibility = "PUBLIC", access_code = "", url = "", cover_img = "", owner = 1)]
    return render_template('about.html', webtitle = "About", daynight = eval_time(), info_notebooks = info_notebooks)
