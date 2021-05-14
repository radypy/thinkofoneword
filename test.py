from flask import Flask, redirect, url_for, render_template, request
from flask_mysqldb import MySQL
from decouple import config


app = Flask(__name__)

app.config['MYSQL_HOST'] = config('MYSQL_HOST')
app.config['MYSQL_USER'] = config('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = config('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = config('MYSQL_DB')

mysql = MySQL()
mysql.init_app(app)

req = ''
think_uniquely = False


@app.route("/")
def initial_page():
    return render_template('initial.html')


@app.route("/word/", methods=['GET', 'POST'])
def home():
    global req
    if request.method == 'POST':
        word = request.form['strword']
        word = word.lower()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO words (word) VALUES (%s)", [word])
        mysql.connection.commit()
        cur.close()
        req = str(word)
        return redirect(url_for('results'))
    return render_template("index.html")


@app.route("/results/", methods=['GET'])
def results():
    global req, think_uniquely
    i = 0
    other_list = []
    data = {'Word': 'Number of times'}
    cur = mysql.connection.cursor()
    users = cur.execute("SELECT word, COUNT(*) FROM words GROUP BY word HAVING COUNT(*) > 0;")
    if users > 0:
        user_details = cur.fetchall()
        sorted_details = sorted(user_details, key=lambda x: x[1], reverse=True)
        for user in sorted_details:
            if i < 9:
                i = i+1
                data[user[0]] = user[1]
            if i >= 9:
                other_list.append(user[1])
                data['Other'] = sum(other_list)
                i = i+1

        total_sum_of_word_count = sum([pair[1] for pair in sorted_details])
        pair_of_word_count = [item for item in sorted_details if item[0] == req]
        total_inputs = pair_of_word_count[0][1]
        if pair_of_word_count[0][1] == 1:
            think_uniquely = True
        else:
            think_uniquely = False
        return render_template("results.html", data=data, req=req, think_uniquely=think_uniquely,
                               total_inputs=total_inputs, total_sum_of_word_count=total_sum_of_word_count)


if __name__ == "__main__":
    app.run(debug=True)

