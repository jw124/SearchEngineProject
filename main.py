from flask import Flask, render_template, request, redirect
import db

app = Flask(__name__)
mydb = db.Database()


@app.route('/')
def index():
  lectures = mydb.getLecture("week1")
  print(lectures)
  return render_template('index.html', lectures = lectures)

@app.route('/<week>')
def weeks(week):
  lectures = mydb.getLecture(week)
  print(week)
  return render_template('index.html', lectures = lectures)

@app.route('/<week>/<title>')
def lecture(week, title):
  lectures = mydb.lecture_detail(title)
  print(week)
  with open("static/" + lectures[0]["Subtitle"], "r") as f: 
    subtitle = f.read()
  return render_template('single-post.html', video = lectures[0]["Video"], subtitle = subtitle)

@app.route('/search', methods = ["POST"])
def search_lecture():
  lectures = mydb.get_All_Lecture()
  return render_template("index.html", lectures = lectures)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=81, debug=True)
