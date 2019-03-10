import flask
from flask import request, jsonify, json
from flask import Response
import datetime
import sqlite3
from functools import wraps


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

def check_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        global author
        if not auth or not check_auth(auth.username, auth.password):
            author = 'Anonymous Coward'
        else:
            author= auth.username
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
def home():
    return "<h1>Comments API</p>"

@app.route('/new', methods=['POST'])
@check_auth
def new():

    result = request.json

    if 'comment' in result:
        comment = result['comment']
    else:
        return "Error: No omment field provided. Please specify comment."

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

    c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

    result_set = c.fetchone()

    if result_set:
        id = result_set[0]
    else:
        conn.close()
        return "Article doesn't exist or may have been deleted"


    

    # for row in result_set:
    #     id = row["articleId"]
    

    c.execute("insert into comments (articleId, comment, author, createdDate) values (:id, :comment,  :author, :createdDate)", {'id': id, 'comment': comment, 'title': title, 'author': author, 'createdDate': str(curDate)})
    
    conn.commit()

    c.execute("select * from comments where isDeleted= 0")

    print(c.fetchall())

    conn.close()

    resp = Response(status=200, mimetype='application/json')

    # return "Comment Created"
    return resp

    
@app.route('/delete', methods=['GET'])
def delete():

    if 'id' in request.args:
        id = request.args['id']
    else:
        return "Error: No id field provided. Please specify id of the article."

    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    c.execute("""update comments
        set isDeleted = 1
        where isDeleted = 0 and commentId = (:id) """, {'id': id})


    conn.commit()

    c.execute("select * from comments where isDeleted= 0")

    print(c.fetchall())

    conn.close()

    return "Article Deleted"

@app.route('/count', methods=['GET'])
def count():

    if 'title' in request.args:
        title = request.args['title']
    else:
        return "Error: No title field provided. Please specify title of the article."


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    

    c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

    result_set = c.fetchone()

    if result_set:
        id = result_set[0]
    else:
        conn.close()
        return "Article doesn't exist or may have been deleted"

    c.execute("""
        select count(commentid) from comments
        where articleId= (:id) and isDeleted = 0""", {"id":id})

    commentsCount = c.fetchone()
    commentsCount = str(commentsCount[0])

    conn.close()

    return "Number of comments for given article:" + commentsCount

@app.route('/retrieve', methods=['GET'])
def retrieve():

    if 'number' in request.args:
        num = request.args['number']
    else:
        num = -1

    if 'title' in request.args:
        title = request.args['title']
    else:
        return "Error: No title field provided. Please specify title of the article."


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

    result_set = c.fetchone()

    if result_set:
        id = result_set[0]
    else:
        conn.close()
        return "Article doesn't exist or may have been deleted"


    if num is -1:

        c.execute("SELECT comment FROM comments where isDeleted = 0 and articleId = (:id) ORDER BY commentId DESC", {"id": id})

    else:
        c.execute("""
            
            SELECT comment FROM comments where isDeleted = 0 and articleId = (:id) ORDER BY commentId DESC LIMIT (:number)
            ;""", {'number': num, "id":id})

    result = jsonify(c.fetchall())

    conn.close()

    return result



app.run()

