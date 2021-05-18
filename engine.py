from flask import Flask, render_template, request, redirect
from flaskext.mysql import MySQL
import requests
import json

app = Flask(__name__)
app.config["DEBUG"] = False
mysql = MySQL()

# change database configuration for custom deployment
app.config['MYSQL_DATABASE_USER'] = 'databaseuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'databasepassword'
app.config['MYSQL_DATABASE_DB'] = 'db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

# redirect root to about page
@app.route('/', methods=['GET'])
def index():
    return redirect('/about')

# get random food inspiration from foodish api
@app.route('/getInspiration', methods=['GET'])
def getInspiration():
    response = requests.get('https://foodish-api.herokuapp.com/api')
    jsonResponse = json.loads(response.text)

    # substring dish name from url and remove numbers from dishName
    dishName = jsonResponse["image"][jsonResponse["image"].rfind("/")+1:jsonResponse["image"].rfind(".")]
    dishName = dishName.translate(str.maketrans('','','1234567890'))

    return render_template('inspiration.html', dishName=dishName, dishImage=jsonResponse["image"])

# get recepies based on keywords from edamam api
@app.route('/getRecipe', methods=['GET'])
def getRecipe():
    # insert api key and app id for edamam api  
    edamamAppId = "XXXXXXXX"
    edamamApiKey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    
    if 'query' in request.args:
        # parameter 'query' is specified
        ingredient = request.args.get("query")
        isQuery = 1
    else:
        # parameter 'query' is NOT specified set it to "Enter ingredient"
        ingredient = "Enter ingredient"
        isQuery = 0

    response = requests.get("https://api.edamam.com/search?q={}&app_id={}&app_key={}".format(ingredient, edamamAppId, edamamApiKey))
    jsonResponse = json.loads(response.text)

    if isQuery == 1:
        for item in jsonResponse['hits']:
            item['recipe']['label'] = item['recipe']['label'].replace(' ', "").replace("'", "")
            count = getTastyCounter(item['recipe']['label'])
            item['recipe']['tastyCount'] = count

    recipies = jsonResponse['hits']

    return render_template('recipe.html', recipes=recipies, ingredient=ingredient)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route("/increaseTastyCounter")
def increaseTastyCounter():
    if 'label' in request.args:
       # parameter 'query' is specified
       label = request.args.get("label")

    if 'query' in request.args:
       # parameter 'query' is specified
       query = request.args.get("query")
    
    #Adding to tasty counter
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO db.apitite (label, tastyCount) VALUES('" + label + "', 1) ON DUPLICATE KEY UPDATE label='" + label + "', tastyCount=tastyCount+1")
    data = conn.commit()

    return redirect("/getRecipe?query=" + query)#render_template('recipe.html')

#select likes from db
def getTastyCounter(label):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(tastyCount, 0) AS tastyCount from db.apitite where label = '" + label + "' limit 1")
    data = cursor.fetchall()

    count = 0
    for row in data:
        count = row[0]
    
    return count

app.run(host="0.0.0.0", port="443", ssl_context=('server.crt', 'server.key'))
