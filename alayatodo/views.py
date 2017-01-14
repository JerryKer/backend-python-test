from flask import url_for, jsonify

from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session
    )


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

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
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
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
def todo_as_json(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()

    if not todo:
        return jsonify({})

    todo = {'id': todo[0],
              'user_id': todo[1],
              'description': todo[2],
              'status': todo[3]}

    return jsonify(todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()

    context = dict()
    context['todos'] = todos
    context['form_error'] = request.args.get('form_error', None)

    return render_template('todos.html', **context)


@app.route('/todo/json', methods=['GET'])
@app.route('/todo/json/', methods=['GET'])
def todos_as_json():
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()

    todos = [{'id': todo[0],
              'user_id': todo[1],
              'description': todo[2],
              'status': todo[3]}
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

    g.db.execute(
        "INSERT INTO todos (user_id, description, status) VALUES ('%s', '%s', '%s')"
        % (session['user']['id'], request.form.get('description', ''), form_status)
    )
    g.db.commit()

    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    return redirect('/todo')
