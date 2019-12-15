import os

from flask import Flask, session, render_template, redirect, url_for, request
from bs4 import BeautifulSoup
from joblib import load
from joblib import dump
import pandas as pd

import requests
from flask import jsonify

app = Flask(__name__)

@app.route("/")
def index():
	
	return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
	application_name = request.form.get("application_name")
	print("######")
	print(application_name)
	print("######")
	res = requests.get(f"https://play.google.com/store/search?q={application_name}&c=apps")

	soup = BeautifulSoup(res.text, 'html.parser')

	applications = soup.find_all("div", "ImZGtf mpg5gc")

	img_list = list()
	title_list = list()
	link_list = list()
	results = list()

	for application in applications:
		title = application.find("div", "WsMG1c nnK0zc").text
		image = application.img['data-srcset'].split("=")[0]
		link = "https://play.google.com" + application.a['href']
		img_list.append(image)
		title_list.append(title)
		link_list.append(link)

	results = list(zip(img_list,title_list,link_list))
	
	return render_template("search.html", results = results)

@app.route("/improve", methods=["GET", "POST"])
def improve():
	application_link = request.form.get("application_link")
	res = requests.get(application_link, headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"})
	soup = BeautifulSoup(res.text, 'html.parser')

	name = soup.find("h1", "AHFaub").text
	
	img_div = soup.find("div", "xSyT2c")
	if soup.find("div", "K9wGie"):
		rating_and_count = soup.find("div", "K9wGie")
		if rating_and_count.find("div", "BHMmbe"):
			rating = rating_and_count.find("div", "BHMmbe").text
		else:
			rating = "No Rating Information"
		if rating_and_count.find("span", ""):
			count = rating_and_count.find("span", "").text
		else:
			count = "No Rating Count Information"
	else:
		rating = "No Rating Information"
		count = "No Rating Count Information"

	img = img_div.img["srcset"].split("=")[0]

	
	additional_informations = soup.find_all("div", "hAyfc")
	additional_informations = list(map(additional_informations.__getitem__, [0,1,2,3,4,5,7]))

	information_list = list()
	# ['Updated', 'Size', 'Installs', 'Current Version', 'Requires Android', 'Content Rating', 'In-app Products']



	if additional_informations[0].find("span", "htlgb").text == 'Learn More':
		information_list.append(additional_informations[1].find("span", "htlgb").text)
		information_list.append(additional_informations[2].find("span", "htlgb").text)
		information_list.append(additional_informations[3].find("span", "htlgb").text)
		information_list.append(additional_informations[4].find("span", "htlgb").text)
		information_list.append(additional_informations[5].find("span", "htlgb").text)
		additional_informations = soup.find_all("div", "hAyfc")
		additional_informations = list(map(additional_informations.__getitem__, [6]))
		information_list.append(additional_informations[0].find("span", "htlgb").text)
		additional_informations = soup.find_all("div", "hAyfc")
		additional_informations = list(map(additional_informations.__getitem__, [8]))
		information_list.append((additional_informations[0].find("span", "htlgb").text).replace(u'\xa0', u' '))
	else:
		i = 1
		for additional_information in additional_informations:
			if i == 6:
				check_content = additional_information.find("div", "BgcNfc").text
				if check_content != "Content Rating":
					information_list.append("No content rating is available")
				else:
					content_rating = additional_information.find_all("div")[2].text
					information_list.append(content_rating)
			elif i == 7:
				check_content = additional_information.find("div", "BgcNfc").text
				if check_content != "In-app Products":
					information_list.append("No in-app purchase is shown")
				else:
					in_app_purchase = additional_information.find("span", "htlgb").text
					information_list.append(in_app_purchase)
			else:
				other_information = additional_information.find("span", "htlgb").text
				information_list.append(other_information)
			i = i + 1

	category = soup.find_all("a", "hrTbp R8zArc")[1]['href']
	category = category.split("/")[-1]
	information_list.append(category)

	count = "".join(count.split(','))
	dataset_content_rating = ['Everyone', 'Teen', 'Everyone 10+', 'Mature 17+', 'Adults only 18+', 'Unrated']
	if not information_list[5] in dataset_content_rating:
		ml_content_rating = 'Everyone'
		print(information_list[5])
	else:
		ml_content_rating = information_list[5]

	price = soup.find_all("button")
	metas = price[5].find_all("meta")
	meta = metas[-1].get("content")
	if len(meta.split()) == 2:
		price = float(meta.split()[1]) * 4.18
	else:
		price = 0
	if price == 0:
		ml_type = 'Free'
	else:
		ml_type = 'Paid'
	
	ml_price = str(price)
	if 'GAME' in category.split('_'):
		category = 'GAME'
	ml_category = category
	ml_android_ver = information_list[4]
	ml_size = information_list[1]
	ml_reviews = count
	ml_last_updated = information_list[0]
	ml_install = information_list[2]

	test_data = pd.DataFrame([[ml_category, ml_content_rating, ml_android_ver, ml_type, ml_size, ml_install, ml_price, ml_reviews, ml_last_updated]], columns=['Category', 'Content Rating', 'Android Ver', 'Type', 'Size', 'Installs', 'Price', 'Reviews', 'Last Updated'])
	print(test_data)
	result = (rating, count, img, name)
	information_list.append(ml_type)
	information_list.append(ml_price)
	loaded_model = load('finalized_google_playstore.sav')
	# predicted_rating = 0
	predicted_rating = loaded_model.predict(test_data)

	return render_template("improve.html", results = result, additional_informations = information_list, prediction = predicted_rating)