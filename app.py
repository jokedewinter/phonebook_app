
from flask import Flask, render_template, request
from app_functions import *
from search import *

app = Flask(__name__)


@app.route("/")
def index():
    page = 'index'
    return render_template("pages/index.html", title="Search for businesses or people", **locals())


@app.route("/business", methods=["GET", "POST"])
def business():
    page = 'business'
    types = show_business_types()

    if request.method == "GET":
        title = "Need shoes? | Business search"

    elif request.method == "POST":
        form_data = request.form

        if ('all_businesses' in request.form) or ('biz_submit' in request.form):
            category = form_data["biz_type"]
            name = form_data["biz_name"]
            location = form_data["biz_location"]

            results = get_business_results(category, name, location)

        elif 'sort_submit' in request.form:
            category = form_data["cat"]
            name = form_data["name"]
            location = form_data["loc"]
            column = form_data["sorting"]

            search = get_business_results(category, name, location)
            results = sort_results(search, column)

        plural = plural_check(results)
        title = "You can have shoes | Business search"

    return render_template("pages/business.html", **locals())


@app.route("/people", methods=["GET", "POST"])
def people():
    page = 'people'
    if request.method == "GET":
        title = "Is it me you're looking for? | People search"

    elif request.method == "POST":
        form_data = request.form

        if ('all_people' in request.form) or ('people_submit' in request.form):
            name = form_data["person_name"]
            location = form_data["person_location"]

            results = search_people(name.title(), location)

        elif 'sort_submit' in request.form:
            name = form_data["name"]
            location = form_data["loc"]
            column = form_data["sorting"]

            search = search_people(name.title(), location)
            results = sort_results(search, column)

        plural = plural_check(results)
        title = "Here I am | People search"
    return render_template("pages/people.html", **locals())


if __name__ == "__main__":
    app.run(debug=True)
