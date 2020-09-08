from flask import render_template, session, request, redirect, url_for, flash
from . import home
import os
import subprocess
from wtforms import Form, StringField, SelectField
import sqlite3
from sqlite3 import Error
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sys
sys.path.append("..")
from merrors import merrors
import conf

configs=conf.config()
configs.read()
name = configs.get("name")
print(name)
Merrors=merrors()
Merrors.error("Test")

#Form stuff
class NewSurveyFormQuestions(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    #answer = StringField('Answers', validators=[DataRequired()])
    category = SelectField('Category', choices=[
                                                ('s_text', 'Short text'),
                                                ('radio', 'Radio choices'),
                                                ('m_text', 'Multiple choice'),
                                                ('none', 'No action, an announcement to the participant')])
    submit = SubmitField('Create')

class NewSurveyFormAnswersText(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Create')

class DoneForm(FlaskForm):
    submit = SubmitField('Finished')

class NewSurveyFormAnswersRadio(FlaskForm):
    answer1 = StringField('Answer 1', validators=[DataRequired()])
    answer2 = StringField('Answer 2', validators=[DataRequired()])
    answer3 = StringField('Answer 3')
    answer4 = StringField('Answer 4')
    answer5 = StringField('Answer 5')
    answer6 = StringField('Answer 6')
    submit = SubmitField('Create')

class NewSurveyFormAnswersChoices(FlaskForm):
    answer1 = StringField('Answer 1', validators=[DataRequired()])
    answer2 = StringField('Answer 2', validators=[DataRequired()])
    answer3 = StringField('Answer 3', validators=[DataRequired()])
    answer4 = StringField('Answer 4')
    answer5 = StringField('Answer 5')
    answer6 = StringField('Answer 6')
    submit = SubmitField('Create')

class NewSurveyFormAnswersNoAct(FlaskForm):
    answer1 = StringField('Extra text', validators=[DataRequired()])
    submit = SubmitField('Create')

# This far into the code I started to question my existance

#Database stuff
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_post(conn, post):
    """
    Create a new post into the posts table
    :param conn:
    :param post:
    :return: post id
    """
    sql = ''' INSERT INTO posts(title,contents,imageurl)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, post)
    conn.commit()
    return cur.lastrowid

def select_post(conn,postid):
    """
    Query a post in the posts table
    :param conn: the Connection object
    :param postid: the ID of the post
    :return:
    """
    cur = conn.cursor()
    cur.execute(str("SELECT * FROM posts WHERE id ="+postid))

    post = cur.fetchall()

    return post

def select_all_posts(conn):
    """
    Query a post in the posts table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts")

    posts = cur.fetchall()

    return posts

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    # Clean cookie moster
    session.clear()
    # Load latest feed
    # Connect to a database with posts
    feed_table=""" CREATE TABLE IF NOT EXISTS posts (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        contents text,
                                        imageurl text
                                    ); """
    conn = create_connection("feed.db")
    if conn is not None:
        # create posts table
        create_table(conn, feed_table)
    else:
        print("Error! cannot create the database connection.")
    # For demonstation we will set some placeholders
    livefeed=[]
    posts = select_all_posts(conn)
    #title = "Example post"
    #contents = "Some contents here"
    #image = "https://www.mvwautotechniek.nl/wp-content/uploads/2019/10/placeholder.png"
    for post in posts:
        livefeed.append([post[0],post[1],post[2]])
    #print(livefeed)
    # Get length
    col = len(posts)
    #Search for a post
    if request.method == "POST":
        searchitem = request.form["query"]
        return render_template('page/home/search.html',query=query, title="Search Results")
    return render_template('page/home/index.html', livefeed=livefeed ,col=col, title="Home Page")

@home.route('/newsurvey', methods=['GET', 'POST'])
def newsurvey():
    """ 
    Page to create a survey, based on a slide system
    """
    form = NewSurveyFormQuestions()
    doneform = DoneForm()
    conn = create_connection("feed.db")
    if form.validate_on_submit():
        if "qcount" not in session:
          session['qcount'] = 0
        else:
          session['qcount']+= 1
        if "qs" not in session:
          session['qs'] = []
        print("Validated")
        print('New survey question requested for user {}, question={}'.format(
            "unkown", form.question.data))
        style = form.category.data
        print("Got to validate new form")
        session['qs'] += [form.question.data]
        session['qs'] += [style]
        session['style'] = [style]
        print(session)
        #return "got here"
        return redirect(url_for("home.newanswer"))
    if doneform.validate_on_submit():
        conn = create_connection("feed.db")
        post = ("Survey",str(session['qs']),str(session['qcount']))
        postid = create_post(conn,post)
        return redirect(url_for("home.content",postid=postid))
    #Flask was being annoying and didnt want to except None as an answer, using a fake form here
    return render_template('page/home/newsurvey.html',form=form, doneform=doneform, style=None, state="qask", title="New Survey")

@home.route('/newanswer', methods=['GET', 'POST'])
def newanswer():
  style = session['style'][0]
  print("style:",style)
  # I liek to eat memory
  conn = create_connection("feed.db")
  if style == "s_text": 
    newform = NewSurveyFormAnswersText()
  elif style == "radio":
    newform = NewSurveyFormAnswersRadio()
  elif style == "m_text":
    newform = NewSurveyFormAnswersChoices()
  elif style == "none":
    newform = NewSurveyFormAnswersNoAct()
  if newform.validate_on_submit():
    print("Saving data")
    #Hold on, who aaareee you?
    if style == "s_text": 
      session['qs'] += [newform.answer.data]
    elif style == "radio":
      session['qs'] += [newform.answer1.data,newform.answer2.data,newform.answer3.data,newform.answer4.data,newform.answer5.data,newform.answer6.data]
    elif style == "m_text":
      newform = NewSurveyFormAnswersChoices()
    elif style == "none":
      newform = NewSurveyFormAnswersNoAct()
    print("session['qs']:",session['qs'])
    return redirect(url_for("home.newsurvey"))
  return render_template('page/home/newsurvey.html',form=newform, style=style, state="qgen ", title="New Survey")

@home.route('/clearsession')
def clearsession():
    """
    Clear session cookies
    """
    try:
      #cookie monster is sad
      session.clear()
      return "Success"
    except Exception as e:
      Merrors.error("Could not clean session. "+str(e))
      return "MErrors caught the event, please check /merrors for info"

@home.route('/session')
def sessions():
    """
    Check session cookies
    """
    try:
      #cookie monster is happy
      return str(session['sq'])
    except Exception as e:
      Merrors.error("Could not clean session. "+str(e))
      return "MErrors caught the event, please check /merrors for info"

@home.route('createcontent/<title>/<content>/<imageurl>')
def createcontent(title,content,imageurl):
    """ 
    Create a page with posted content
    """
    conn = create_connection("feed.db")
    post = (title,content,imageurl)
    postid = create_post(conn,post)
    return redirect(url_for("home.content",postid=postid))

@home.route('content/<postid>')
def content(postid):
    """ 
    Show a page with posted content
    """
    conn = create_connection("feed.db")
    post = select_post(conn,postid)
    return render_template('page/apps/app_page.html',post=post,title=str(postid))

@home.route('/dashboard')
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    #yes this is empty, no its not an accident. If it had something Earth would split.
    return render_template('page/home/dashboard.html', title="Dashboard")


@home.route('/merrors')
def merrors():
    """
    Render the merrors template on the /merrors route
    """
    errors = Merrors.getall()
    return render_template('page/home/merrors.html',errors = errors,  title="MErrors")