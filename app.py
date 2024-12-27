from flask import Flask, render_template, request, jsonify, flash
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)  # initializing a flask app
app.secret_key = "SankritaPatel"

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    flash("Please enter the product name")
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method=='POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            with open("flipkart_page.html", "w", encoding="utf-8") as file:
                file.write(str(flipkart_html))
            bigboxes = flipkart_html.findAll("div", {"class": "tUxRFH"})
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            # print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "col EPCmJX"})
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            reviews = []
            for commentbox in commentboxes:
                try:
                    name =  commentbox.find("p", class_="_2NsDsF AwS1CA").text
                except:
                    name = 'No Name'
                try:
                    rating = commentbox.find("div", class_="XQDdHH Ga3i8K").text
                except:
                    rating = 'No Rating'
                try:
                    commentHead = commentbox.find("p", class_="z9E0IG").text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.find("div", class_="ZmyHeo").div.div.text
                    custComment = comtag
                except:
                    custComment = 'No Customer Comment'
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}
                reviews.append(mydict)
                with open("reviews.csv", "a", encoding="utf-8") as fw:
                    fw.write(searchString + "," + name + "," + rating + "," + commentHead + "," + custComment + "\n")
                
            return render_template('results.html', reviews=reviews[1:], search=searchString)
        
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template('index.html')
    
if __name__ == "__main__":
    app.run(debug=True)