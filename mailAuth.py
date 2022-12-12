import os
from flask import *
from flask_mail import Mail, Message
import jwt
import datetime
from functools import wraps
import psycopg2
import psycopg2.extras

#pip install Flask-Mail

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_USERNAME']='hellokhafifa@outlook.co.id'
app.config['MAIL_PASSWORD']='hello875'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_SSL']=False
app.config['MAIL_USE_TLS']=True
mail = Mail(app)

app.config['SECRET_KEY'] = 'zkvlvk'

@app.route('/', methods=['GET', 'POST'])
def index():
    auth = request.authorization

    if auth and auth.username == 'by' and auth.password == 'together':
        # generate token
        token = jwt.encode({'user' : auth.username, 
                            'exp' : datetime.datetime.utcnow() + 
                            datetime.timedelta(seconds=300)}, 
                            app.config['SECRET_KEY'])
        if request.method == 'GET':
            return '<form action="/" method="POST"><input name = "email"><input type="submit"></form>'

        email = request.form['email']

        msg = Message('Confirm Email', sender='hellokhafifa@outlook.co.id', recipients=[email])
        link = url_for('protected', token=token.decode('UTF-8'), _external=True)
        msg.body = 'Your link is {} .\n Are you trying to confirm with this email? If it\'s not you please don\' use this link.'.format(link)

        mail.send(msg)

        return '<h3>Please check your email!</h3>'
    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

DB_HOST = "localhost"
DB_NAME = "tstdb"
DB_USER = "postgres"
DB_PASS = "1234567890"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403
        
        return f(*args, **kwargs)
    return decorated


@app.route('/protected')
@token_required
def protected():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    read = "SELECT * FROM heart_failure"
    cur.execute(read) # Execute the SQL
    list_data = cur.fetchall()
    return render_template('index.html', list_data = list_data)

@app.route('/create', methods=['POST'])
def create():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        age             = request.form['age']
        sex             = request.form['sex']
        chest_pain_type = request.form['chest_pain_type']
        cholesterol     = request.form['cholesterol']
        max_hr          = request.form['max_hr']
        heart_disease   = request.form['heart_disease']
        cur.execute("ROLLBACK")
        cur.execute("INSERT INTO heart_failure (age, sex, chest_pain_type, cholesterol, max_hr, heart_disease) VALUES (%s,%s,%s,%s,%s,%s)", (age, sex, chest_pain_type, cholesterol, max_hr, heart_disease))
        conn.commit()
        flash('Data Added successfully')
        return redirect(url_for('protected'))

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def edit(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM heart_failure WHERE id = {0}'. format(id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', dt = data[0])

@app.route('/update/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        age             = request.form['age']
        sex             = request.form['sex']
        chest_pain_type = request.form['chest_pain_type']
        cholesterol     = request.form['cholesterol']
        max_hr          = request.form['max_hr']
        heart_disease   = request.form['heart_disease']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""
            UPDATE heart_failure
            SET age = %s,
                sex = %s,
                chest_pain_type = %s,
                cholesterol = %s,
                max_hr = %s,
                heart_disease = %s
            WHERE id = %s
        """, (age, sex, chest_pain_type, cholesterol, max_hr, heart_disease, id))
        flash('Data Updated Successfully')
        conn.commit()
        return redirect(url_for('protected'))

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM heart_failure WHERE id = {0}'.format(id))
    conn.commit()
    flash('Data Removed Successfully')
    return redirect(url_for('protected'))

if __name__ == '__main__':
    app.run(debug=True)