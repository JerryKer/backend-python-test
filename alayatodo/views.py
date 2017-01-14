
from alayatodo import app
from flask import (
    redirect,
    render_template,
    request,
    session,
    jsonify,
    url_for)

from alayatodo.models import Todo, User, Pagination


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User().get_user(username, password)

    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    todo = Todo().get_by_id(id)
    todo = Todo(todo)

    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
def todo_as_json(id):
    todo = Todo().get_by_id(id)
    todo = Todo(todo)

    if not todo:
        return jsonify({})

    todo = {'id': todo.id,
            'user_id': todo.user_id,
            'description': todo.description,
            'status': todo.status}

    return jsonify(todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    limit = 5

    current_page = request.args.get('current_page', 1)
    current_page = int(current_page) if current_page > 0 else 1

    if not session.get('logged_in'):
        return redirect('/login')

    pagination = Pagination(Todo(), limit, current_page)
    todos = pagination.get_current_items()

    context = dict()
    context['todos'] = todos
    context['form_error'] = request.args.get('form_error', None)
    context['form_message'] = request.args.get('form_message', None)
    context['total_pages'] = pagination.total_pages
    context['current_page'] = current_page

    return render_template('todos.html', **context)


@app.route('/todo/json', methods=['GET'])
@app.route('/todo/json/', methods=['GET'])
def todos_as_json():
    todos = Todo().get_todos_list()

    todos = [{'id': todo.id,
              'user_id': todo.user_id,
              'description': todo.description,
              'status': todo.status}
             for todo in todos]

    return jsonify(todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')

    form_description = request.form.get('description', '').strip()
    form_status = 1 if request.form.get('status', None) is not None else 0

    if not form_description:
        return redirect(url_for('todos', form_error='Description is mandatory.'))

    status = Todo().add(session['user']['id'], form_description, form_status)

    form_message = 'Todo is successful added.'
    print status
    if not status:
        form_message = 'Todo failed to add.'

    return redirect(url_for('todos', form_message=form_message))


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')

    status = Todo().delete(id)

    form_message = 'Todo is successful deleted.'

    if not status:
        form_message = 'Todo failed to delete.'

    return redirect(url_for('todos', form_message=form_message))
