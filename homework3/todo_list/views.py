from http import HTTPStatus

from flask import abort
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask.blueprints import Blueprint

from .app import db
from .models import Task
from .utils import FilterStatus, FlashMessageCategory

view_bp = Blueprint('view', __name__)


@view_bp.route('/')
def index():
    return redirect(url_for('.tasks'))


@view_bp.route('/tasks')
def tasks():
    search_text = request.args.get('filter', '')
    cur_status = request.args.get(
        'status', app.config['DEFAULT_FILTER_STATUS'], FilterStatus
    )
    page_number = request.args.get('page', 1, int)

    if cur_status == FilterStatus.ALL:
        query = Task.description.contains(search_text)  # pylint: disable=no-member
    else:
        is_done_status = cur_status != FilterStatus.ACTIVE
        query = Task.description.contains(search_text) & (  # pylint: disable=no-member
            Task.done == is_done_status
        )

    tasks_to_render = Task.query.filter(query).paginate(
        page=page_number, per_page=app.config['DEFAULT_ITEMS_PER_PAGE'], error_out=False
    )

    return render_template(
        'list_tasks.html',
        cur_status=cur_status,
        tasks=tasks_to_render,
        filter=search_text,
    )


@view_bp.route('/new_task', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        task_description = request.form.get(
            'task_description', app.config['DEFAULT_TASK_DESCRIPTION']
        ).strip()
        if task_description:

            task = Task(description=task_description)
            db.session.add(task)
            db.session.commit()

            flash(
                app.config['TASK_SUCCESSFULLY_ADDED_MESSAGE'],
                FlashMessageCategory.SUCCESS.name.lower(),
            )
        else:
            flash(
                app.config['EMPTY_TASK_MESSAGE'],
                FlashMessageCategory.ERROR.name.lower(),
            )
        return redirect(url_for('.tasks'))
    return render_template('new_task.html')


@view_bp.route('/done_task')
def done_task():
    task_id = request.args.get('task_id', None, int)
    kwargs = dict(request.args)
    if task_id:
        del kwargs['task_id']

    task = Task.query.filter(Task.id == task_id).first_or_404()

    if not task.done:
        task.done = True
        db.session.commit()
        return redirect(url_for('.tasks', **kwargs))

    return abort(HTTPStatus.NOT_FOUND)
