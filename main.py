import os
import ssl
import time
import urllib

import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from flask import Flask, render_template, request
from wordcloud import WordCloud, STOPWORDS
from flask_cors import CORS, cross_origin
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

IMAGE_FOLDER = os.path.join('static', 'images')
CSV_FOLDER = os.path.join('static', 'CSVs')

app.config['IMG_FOLDER'] = IMAGE_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER

# SSL certificate verification
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


class DataCollection:
    def __init__(self):
        self.data = {
            "Product": [],
            "Name": [],
            "Price (INR)": [],
            "Rating": [],
            "Comment Heading": [],
            "Comment": [],
            "Sentiment": []
        }

        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def get_final_data(self, comment_box=None, prod_name=None, prod_price=None):
        self.data["Product"].append(prod_name)
        self.data["Price (INR)"].append(prod_price)

        try:
            self.data["Name"].append(comment_box.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text)
        except:
            self.data["Name"].append('No Name')

        try:
            self.data["Rating"].append(comment_box.div.div.div.div.text)
        except:
            self.data["Rating"].append('No Rating')

        try:
            self.data["Comment Heading"].append(comment_box.div.div.div.p.text)
        except:
            self.data["Comment Heading"].append('No Comment Heading')

        try:
            com_tag = comment_box.div.div.find_all('div', {'class': ''})
            self.data["Comment"].append(com_tag[0].div.text)
        except:
            self.data["Comment"].append('')


    def HTML_main(self, base_url=None, search_string=None):
        search_url = f"{base_url}/search?q={search_string}"
        with urllib.request.urlopen(search_url) as url:
            page = url.read()
        return soup(page, "html.parser")

    def PRODUCT_links_name(self, flipkart_base=None, big_boxes=None):
        temp = []
        for box in big_boxes:
            try:
                temp.append((box.div.div.div.a.img['alt'], flipkart_base + box.div.div.div.a["href"]))
            except:
                pass
        return temp

    def analyze_sentiment(self):
        for comment in self.data["Comment"]:
            sentiment_score = self.sentiment_analyzer.polarity_scores(comment)
            sentiment = "Positive" if sentiment_score["compound"] >= 0 else "Negative"
            self.data["Sentiment"].append(sentiment)

    def final_DATA(self, comment_box=None, prod_name=None, prod_price=None):
        self.data["Product"].append(prod_name)
        self.data["Price (INR)"].append(prod_price)

    def PRODUCT_HTML(self, product_link=None):
        prod_page = requests.get(product_link)
        return soup(prod_page.text, "html.parser")

    def DATA_dictionary(self):
        return self.data

    def DATAFRAME(self, dataframe, file_name=None):
        csv_path = os.path.join(app.config['CSV_FOLDER'], file_name)
        file_extension = '.csv'
        final_path = f"{csv_path}{file_extension}"
        dataframe.to_csv(final_path, index=None)
        print("File saved successfully!!")
        return final_path

    def WORDCLOUD(self, dataframe=None, img_filename=None):
        txt = dataframe["Comment"].values
        wc = WordCloud(width=800, height=400, background_color='black', stopwords=STOPWORDS).generate(str(txt))

        plt.figure(figsize=(20, 10), facecolor='k', edgecolor='k')
        plt.imshow(wc, interpolation='bicubic')
        plt.axis('off')
        plt.tight_layout()

        image_path = os.path.join(app.config['IMG_FOLDER'], img_filename + '.png')
        plt.savefig(image_path)
        plt.close()
        print("Saved word cloud image")


@app.route('/', methods=['GET'])
@cross_origin()
def home_page():
    return render_template("index.html")


@app.route('/review', methods=["POST", "GET"])
@cross_origin()
def indexing():
    if request.method == 'POST':
        try:
            base_url = 'https://www.flipkart.com'
            search_string = request.form['content']
            search_string = search_string.replace(" ", "+")
            print('Processing...')

            start = time.perf_counter()

            get_data = DataCollection()
            flipkart_html = get_data.HTML_main(base_url=base_url, search_string=search_string)
            big_boxes = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
            product_name_links = get_data.PRODUCT_links_name(base_url, big_boxes)

            for prod_name, product_link in product_name_links[:4]:
                prod_html = get_data.PRODUCT_HTML(product_link)
                try:
                    comment_boxes = prod_html.find_all('div', {'class': '_16PBlm'})
                    prod_price = prod_html.find_all('div', {"class": "_30jeq3 _16Jk6d"})[0].text
                    prod_price = float((prod_price.replace("₹", "")).replace(",", ""))
                    for comment_box in comment_boxes:
                        get_data.get_final_data(comment_box, prod_name, prod_price)
                except:
                    pass

            get_data.analyze_sentiment()
            df = pd.DataFrame(get_data.DATA_dictionary())
            sentiment_counts = df['Sentiment'].value_counts().to_dict()  # Count the sentiment occurrences
            download_path = get_data.DATAFRAME(df, file_name=search_string.replace("+", "_"))
            get_data.WORDCLOUD(df, img_filename=search_string.replace("+", "_"))

            finish = time.perf_counter()
            print(f"Program finished and elapsed time: {finish - start} second(s)")
            return render_template('review.html',
                                   tables=[df.to_html(classes='data')],
                                   titles=df.columns.values,
                                   search_string=search_string,
                                   download_csv=download_path,
                                   sentiment_counts=sentiment_counts  # Pass sentiment counts to template
                                   )
        except Exception as e:
            print(e)
            return render_template("404.html")
    else:
        return render_template("index.html")


@app.route('/show')
@cross_origin()
def WORDCLOUD_DISPLAY():
    img_file = os.listdir(app.config['IMG_FOLDER'])[0]
    full_filename = os.path.join(app.config['IMG_FOLDER'], img_file)
    return render_template("show_wc.html", user_image=full_filename)


if __name__ == '__main__':
    app.run(debug=True)
