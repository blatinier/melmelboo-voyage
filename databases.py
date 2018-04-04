import pymysql

import conf


def get_voyage_connection():
    return pymysql.connect(**conf.BLOG_VOYAGE_DATABASE)


def get_melmelboo_connection():
    return pymysql.connect(**conf.BLOG_MELMELBOO_DATABASE)
