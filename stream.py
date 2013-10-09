import re
from random import random
from string import ascii_letters
import json

import tweepy

import keys


auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.token, keys.secret)
api = tweepy.API(auth)


def stut(word, chance=.4):
    if random() < chance and word[0] in ascii_letters:
        return u'%s-%s' % (word[0], stut(word, chance/2))
    else:
        return word


def tsun(string, verboten):
    def stut_if_not_verboten(match):
        word = match.group(0)

        if word not in verboten:
            return stut(word)
        else:
            return word

    return re.sub(r'\b\S+\b', stut_if_not_verboten, string)


def unescape(string):
    for bad, sub in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>')]:
        string = string.replace(bad, sub)

    return string


class TsundereRepeater(tweepy.StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)

        if not 'text' in tweet:
            print 'not a tweet'
            return True

        if not tweet['user']['id_str'] == keys.the_id:
            print 'not from our user'
            return True

        rt_status = tweet.get('retweeted_status')

        if rt_status is not None:
            try:
                api.retweet(rt_status['id'])
            except tweepy.error.TweepError as error:
                print 'rt failed with %r' % error

            return True

        if tweet['entities']['user_mentions']:
            return True  # we don't want to be unnecessarily spammy

        goel = lambda d, k: d.get(k, [])

        verboten = [
            url['url'] for url in goel(tweet['entities'], 'urls')
        ] + [
            media['url'] for media in goel(tweet['entities'], 'media')
        ] + [
            tag['text'] for tag in goel(tweet['entities'], 'hashtags')
        ]

        tsun_tweet = tsun(tweet['text'], verboten)

        try:
            api.update_status(unescape(tsun_tweet))
        except tweepy.error.TweepError as error:
            print 'tweeting failed with %r' % error

        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':
    stream = tweepy.Stream(auth, TsundereRepeater())
    stream.filter(follow=[keys.the_id])
