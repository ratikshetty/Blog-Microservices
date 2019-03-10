import flask
from flask import request, jsonify, json
import datetime
import sqlite3
from functools import wraps
from flask_basicauth import BasicAuth


app = flask.Flask(__name__)
app.config["DEBUG"] = True

author = ''

# app.config['BASIC_AUTH_USERNAME'] = 'john'
# app.config['BASIC_AUTH_PASSWORD'] = 'matrix'

# basic_auth = BasicAuth(app)

# class check(BasicAuth):
#     def check_credentials(username, password):
#         return true

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'john' and password == 'matrix'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return "invalid"

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        global author 
        author= auth.username
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
# @basic_auth.required
def home():
    return "<h1>testing Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/new', methods=['POST'])
@requires_auth
def new():


    result = request.json

    if 'content' in result:
        content = result['content']
    else:
        return "Error: No content field provided. Please specify an content."

    if 'title' in result:
        title = result['title']
    else:
        return "Error: No title field provided. Please specify an title."

    # if 'author' in result:
    #     author = result['author']
    # else:
    #     return "Error: No author field provided. Please specify an author."
    global author


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    curDate = datetime.datetime.now()

    c.execute("insert into article (content, title, author, createdDate, modifiedDate) values (:content, :title, :author, :createdDate, :modifiedDate)", {'content': content, 'title': title, 'author': author, 'createdDate': str(curDate), 'modifiedDate': str(curDate)})
    
    conn.commit()

    c.execute("select * from article where isDeleted= 0")

    print(c.fetchall())

    conn.close()

    return "Article Created"

@app.route('/search', methods=['GET'])
def search():

    if 'title' in request.args:
        title = request.args['title']
    else:
        return "Error: No title field provided. Please specify Title of the article."

    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    c.execute("select * from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

    result = jsonify(c.fetchone()) 

    c.close()

    return result

@app.route('/edit', methods=['PATCH'])
@requires_auth
def edit():

    result = request.json

    if 'title' in result:
        title = result['title']
    else:
        return "Error: No title field provided. Please specify an title."

    if 'content' in result:
        content = result['content']
    else:
        return "Error: No content field provided. Please specify an content."

    global author


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    curDate = datetime.datetime.now()

    c.execute("""UPDATE article
            set content = (:content),
            modifiedDate = (:date),
            author = (:author)
            where title = (:title)  COLLATE NOCASE""", {'content': content, 'title': title, 'date': str(curDate), "author": author})

    conn.commit()

    conn.close()

    return "Article updated"


@app.route('/delete', methods=['GET'])
@requires_auth
def delete():

    if 'title' in request.args:
        title = request.args['title']
    else:
        return "Error: No title field provided. Please specify Title of the article."

    global author

    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    c.execute("""update article
        set isDeleted = 1
        where isDeleted = 0 and author= (:author) and title = (:title) COLLATE NOCASE""", {'title': title, 'author': author})


    conn.commit()
    conn.close()

    return "Article Deleted"

@app.route('/retrieve', methods=['GET'])
def retrieve():

    if 'number' in request.args:
        num = request.args['number']
    else:
        num = -1

    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    if num is -1:

        c.execute("SELECT content FROM article where isDeleted = 0 ORDER BY articleId DESC")

    else:
        c.execute("""
            
            SELECT content FROM article where isDeleted = 0 ORDER BY articleId DESC LIMIT (:number)
            ;""", {'number': num})

    result = jsonify(c.fetchall())

    conn.close()

    return result

@app.route('/meta', methods=['GET'])
def meta():

    if 'number' in request.args:
        num = request.args['number']
    else:
        num = -1

    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    if num is -1:

        c.execute("SELECT * FROM article where isDeleted = 0 ORDER BY articleId DESC")

    else:
        c.execute("""
            
            SELECT * FROM article where isDeleted = 0 ORDER BY articleId DESC LIMIT (:number)
            ;""", {'number': num})

    result = jsonify(c.fetchall())

    conn.close()

    return result



app.run()
