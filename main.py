#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import sqlite3
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
                      "AND strftime('%Y', published_at)='2016'"
                      "ORDER BY published_at DESC")
    images = [{'title': i[0],
               'image': i[1]} for i in ghost_cur.fetchall()]
    ghost.close()
    return render_template('/who_are_we/linked_posts.html', images=images,
                           current="who_are_we",
                           panel="linked_posts")


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
    with open(conf.CURRENT_POS_FILE, "w+") as fh:
        json.dump(dic, fh)
    return jsonify({'message':'You got served!'})

@application.route("/preparation/related")
def planning_linked_posts():
    ghost = sqlite3.connect(conf.BLOG_VOYAGE_DB)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT title, image, html, slug FROM posts WHERE id IN "
                      "(SELECT post_id FROM posts_tags WHERE tag_id=8) "
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
        with open(conf.CURRENT_POS_FILE) as pos_file:
            content = json.load(pos_file)
            pos_lat = content["latitude"]
            pos_long = content["longitude"]
            country = content.get("country")
        return render_template(page['tpl_file'],
                               current=page['active-menu'],
                               panel=page['active-panel'],
                               title=page['title'],
                               latitude=pos_lat,
                               longitude=pos_long,
                               country=country)
    return view


for key, page in conf.STATIC_TPL.items():
    application.add_url_rule(page['url'],
                             endpoint=key,
                             view_func=create_static_view(page))
