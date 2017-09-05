#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sqlite3
import twitter
import re
import urllib.parse


def iri_to_uri(url):
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    return url


def tweet_new_article(twitter_ckey, twitter_csecret,
                      twitter_token, twitter_token_secret,
                      db_voyage):
    api = twitter.Api(consumer_key=twitter_ckey,
                      consumer_secret=twitter_csecret,
                      access_token_key=twitter_token,
                      access_token_secret=twitter_token_secret)

    ghost = sqlite3.connect(db_voyage)
    ghost_cur = ghost.cursor()
    ghost_cur.execute("SELECT title, image, slug FROM posts "
                      "WHERE published_at < DATETIME('now') "
                      "AND published_at > DATETIME('now', '-1 day') "
                      "ORDER BY published_at DESC")
    for post in ghost_cur.fetchall():
        image_url = post[1]
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        msg = "%s https://www.melmelboo-voyage.fr/blog/%s" % (post[0], post[2])
        image_url = iri_to_uri(image_url)
        api.PostMedia(msg, image_url)
