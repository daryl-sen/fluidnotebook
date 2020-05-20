from flask import Blueprint, render_template
from project.core.daynight import eval_time

error_pages = Blueprint('error_pages', __name__, template_folder = "templates/error_pages")

@error_pages.app_errorhandler(404)
def error_404(error):
    return render_template('404.html', daynight = eval_time())

@error_pages.app_errorhandler(403)
def error_403(error):
    return render_template('403.html', daynight = eval_time())

@error_pages.app_errorhandler(500)
def error_500(error):
    return render_template('500.html', daynight = eval_time())
