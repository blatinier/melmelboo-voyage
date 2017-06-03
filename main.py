#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os.path
import requests
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect
from flask_mail import Message
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import MultifieldParser

import conf
from bootstrap import application, mail
from forms import ContactForm
from utils.cleaner import clean_string
from utils.country_names import countries


def excerpt(text):
    text = clean_string(text)
    return " ".join(text.split(" ")[:45])


@application.route("/", methods=['GET'])
def home():
    return render_template('index.html')


@application.route("/blog")
def redir_blog():
    return redirect("/blog/")

@application.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == "GET":
        return render_template('contact.html', form=form,
                               current='contact')
    elif request.method == "POST":
        if not form.validate():
            return render_template('contact.html', form=form,
                                   current='contact')
        else:
            pass
            msg = Message("[melmelboo-voyage] %s" % form.name.data,
                          sender=form.email.data,
                          reply_to=form.email.data,
                          recipients=['benoit@latinier.fr',
                                      'camille.demoment@gmail.com'])
            msg.body = """
From: %s <%s>
Website: %s
%s
""" % (form.name.data, form.email.data, form.website.data, form.message.data)
            mail.send(msg)
            return render_template('contact.html', form=form,
                                   success=True, current='contact')


@application.route("/baloo-notre-camping-car/related")
def camping_car_linked_posts():
    ghost = sqlite3.connect(conf.BLOG_VOYAGE_DB)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT title, image, html, slug FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=1) "
                      "AND published_at < DATE('now') "
                      "ORDER BY published_at DESC")
    posts = [{'title': i[0],
              'image': i[1],
              'excerpt': excerpt(i[2]),
              'slug': i[3]} for i in ghost_cur.fetchall()]
    ghost.close()
    return render_template('camping_car/linked_posts.html', posts=posts,
                           current="camping_car", panel="linked_posts")


@application.route("/qui-sommes-nous/related")
def who_are_we_linked_posts():
    ghost = sqlite3.connect(conf.BLOG_MELMELBOO_DB)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT title, image FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=36) "
                      "AND strftime('%Y', published_at)='2016' "
                      "AND published_at < DATE('now') "
                      "ORDER BY published_at DESC")
    images = [{'title': i[0],
               'image': i[1]} for i in ghost_cur.fetchall()]
    ghost.close()
    return render_template('/who_are_we/linked_posts.html', images=images,
                           current="who_are_we",
                           panel="linked_posts")


@application.route("/gps/maps")
def gen_maps():
    maps = get_maps_data()
    return render_template("/itinerary/maps.html",
                           **maps)


def get_maps_data():
    with open(conf.CURRENT_POS_FILE) as pos_file:
        content = json.load(pos_file)
    rev_countries = {v: k for k, v in countries.items()}
    points_by_country = defaultdict(list)
    latitudes_by_country = defaultdict(list)
    longitudes_by_country = defaultdict(list)
    ordered_countries = []
    for point in content['hist']:
        country = rev_countries[point['country']]
        map_name = country.replace(" ", "")
        map_name = map_name[0].lower() + map_name[1:]
        if map_name not in ordered_countries:
            ordered_countries.append(map_name)
        points_by_country[map_name].append(point)
        latitudes_by_country[map_name].append(point['latitude'])
        longitudes_by_country[map_name].append(point['longitude'])
    ordered_countries = ordered_countries[::-1]
    return {"countries": ordered_countries,
            "last_country": ordered_countries[0],
            "maps": points_by_country,
            "latitudes": latitudes_by_country,
            "longitudes": longitudes_by_country}


@application.route("/accounting/add", methods=["GET", "POST"])
def accounting():
    last_action = ""
    with open(conf.ACCOUNTING_FILE) as acc_file:
        achats = json.load(acc_file)
    if request.method == "POST":
        cat, scat = request.form['spending_type'].split(" -- ")
        amount = int(request.form['amount'])
        if amount and cat in achats and scat in achats[cat]:
            achats[cat][scat] += amount
            with open(conf.ACCOUNTING_FILE, "w+") as acc_file:
                json.dump(achats, acc_file)
                last_action = "Added %s to %s -- %s" % (amount, cat, scat)
    return render_template("/planning/accounting.html",
                           achats=achats,
                           last_action=last_action)


@application.route("/gps/pipopipo")
def update_coords_by_btn():
    return render_template("/itinerary/update_gps.html")


@application.route("/gps/<latitude>/<longitude>")
def update_coords(latitude, longitude):
    dic = {"latitude": latitude,
           "longitude": longitude}
    url_ws = "%s?lat=%s&lng=%s&username=%s&password=%s" % \
                (conf.GEONAMES_WS,
                 latitude, longitude,
                 conf.GEONAMES_USER,
                 conf.GEONAMES_PWD)
    res = requests.get(url_ws).json()
    dic["country"] = countries[res["geonames"][0]['countryName']]
    with open(conf.CURRENT_POS_FILE) as pos_file:
        content = json.load(pos_file)
        to_hist = {"latitude": content["latitude"],
                   "longitude": content["longitude"],
                   "country": content["country"]}
    if "hist" in content:
        content["hist"].append(to_hist)
    else:
        content["hist"] = [to_hist]
    content.update(dic)
    with open(conf.CURRENT_POS_FILE, "w+") as fh:
        json.dump(content, fh)
    return jsonify({'message':'You got served!'})

@application.route("/itinerary/related/<country>")
def itinerary_linked_posts(country):
    ghost = sqlite3.connect(conf.BLOG_VOYAGE_DB)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT title, image, html, slug FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags "
                      " LEFT JOIN tags ON posts_tags.tag_id=tags.id "
                      " WHERE tags.name=?) "
                      "AND published_at < DATETIME('now') "
                      "ORDER BY published_at DESC", (country, ))
    posts = [{'title': i[0],
              'image': i[1],
              'excerpt': excerpt(i[2]),
              'slug': i[3]} for i in ghost_cur.fetchall()]
    ghost.close()
    has_top_img = os.path.isfile("img/articles/Bilan_%s.png" % country.capitalize())
    return render_template('itinerary/linked_posts.html', posts=posts,
                           current="itineraire",
                           panel="visited_countries",
                           country=country,
                           has_top_img=has_top_img)

@application.route("/preparation/related")
def planning_linked_posts():
    ghost = sqlite3.connect(conf.BLOG_VOYAGE_DB)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT title, image, html, slug FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=8) "
                      "AND published_at < DATE('now') "
                      "ORDER BY published_at DESC")
    posts = [{'title': i[0],
              'image': i[1],
              'excerpt': excerpt(i[2]),
              'slug': i[3]} for i in ghost_cur.fetchall()]
    ghost.close()
    return render_template('planning/linked_posts.html', posts=posts,
                           current="preparation", panel="linked_posts")


@application.route("/search/", defaults={'page': 1})
@application.route("/search/<int:page>")
def search(page):
    search = request.args['q']
    storage = FileStorage(conf.INDEX_DIR)
    index = storage.open_index(indexname=conf.INDEX_NAME)
    qp = MultifieldParser(['title', 'text', 'tags'], schema=index.schema)
    q = qp.parse(search)
    results = []
    with index.searcher() as searcher:
        results = searcher.search_page(q, page, pagelen=conf.PAGE_SIZE)
        # Get real posts
        post_ids = ",".join([p['post_id'] for p in results
                             if not p['post_id'].startswith('static-')])
        ghost = sqlite3.connect(conf.BLOG_VOYAGE_DB)
        ghost_cur = ghost.cursor()
        ghost_cur.execute("SELECT title, image, html, slug "
                          "FROM posts WHERE id IN (%s) "
                          "ORDER BY published_at DESC" % post_ids)
        posts = [{'type': "post",
                  'title': i[0],
                  'image': i[1],
                  'excerpt': excerpt(i[2]),
                  'url': "/blog/" + i[3]} for i in ghost_cur.fetchall()]
        ghost.close()
        # Get static pages
        for p in results:
            if p['post_id'].startswith('static-'):
                page_key = p['post_id'].replace("static-", "")
                page = conf.STATIC_TPL[page_key]
                with open('templates/' + page['tpl_file'], "r") as p:
                    page_text = p.read()
                posts.append({'type': 'static-page',
                              'title': page['title'],
                              'excerpt': excerpt(page_text),
                              'image': page.get('image'),
                              'url': page['url']})
    return render_template("search.html", posts=posts, search=search)


def create_static_view(page):
    def view():
        departure_day = datetime(2017, 3, 4)
        days_past_since_departure = (datetime.today() - departure_day).days
        with open(conf.ACCOUNTING_FILE) as acc_file:
            achats = json.load(acc_file)
            achats_glob = {k: sum(v.values()) for k, v in achats.items()}
        with open(conf.CURRENT_POS_FILE) as pos_file:
            content = json.load(pos_file)
            pos_lat = content["latitude"]
            pos_long = content["longitude"]
            country = content.get("country")
            points_hist = content["hist"]
        maps = get_maps_data()
        return render_template(page['tpl_file'],
                               current=page['active-menu'],
                               panel=page['active-panel'],
                               title=page['title'],
                               latitude=pos_lat,
                               longitude=pos_long,
                               points_hist= points_hist,
                               country=country,
                               achats=achats,
                               achats_glob=achats_glob,
                               days_past_since_departure=days_past_since_departure,
                               departure_day=departure_day,
                               **maps)
    return view


for key, page in conf.STATIC_TPL.items():
    application.add_url_rule(page['url'],
                             endpoint=key,
                             view_func=create_static_view(page))
