#!/usr/bin/env python3
import argparse
import conf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Launch scripts')
    parser.add_argument('script',
                        help='Name of the script')
    args = parser.parse_args()
    if args.script == "index_blog":
        from scripts.indexer import BlogIndexer
        bi = BlogIndexer(conf.INDEX_NAME, conf.INDEX_DIR, conf.STATIC_TPL)
        bi.init_index()
        bi.index_blog()
        bi.index_templates()
    elif args.script == "mails_to_mailchimp":
        from scripts.mailchimp import transfer
        transfer(conf.MAILCHIMP_API_KEY)
    elif args.script == "tweet_new_article":
        from scripts.twitter import tweet_new_article
        tweet_new_article(conf.TWITTER_CONSUMER_KEY,
                          conf.TWITTER_CONSUMER_SECRET,
                          conf.TWITTER_ACCESS_TOKEN_KEY,
                          conf.TWITTER_ACCESS_TOKEN_SECRET)
