"""from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')"""

import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

app.config['SECRET_KEY'] = 'this should be a secret random string'
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            return redirect(url_for('index'))
        
        url_data = conn.execute('INSERT INTO urls (original_url) VALUES (?)', (url,))
        conn.commit()
        conn.close()

        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)
    
    return render_template('index.html')



@app.route('/<id>')
def url_redirect(id):
    conn = get_db_connection()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url'' WHERE id = (?)', (original_id,)).fetchone()
        original_url = url_data['original_url']

        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    conn = get_db_connection()
    if request.args.get('delete_id'):
        # Delete the row from the table with the given id
        conn.execute('DELETE FROM urls WHERE id = ?', (request.args.get('delete_id'),))
        conn.commit()

    db_urls = conn.execute('SELECT id, created, original_url, clicks From urls').fetchall()
    conn.close()
    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    return render_template('history.html', urls=urls)



if __name__ == '__main__':
    app.run(debug=True)
