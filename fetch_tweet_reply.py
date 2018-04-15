import tweepy
from tweepy import TweepError
import re
import MeCab
import time

CONSUMER_KEY        = 'XXXXXXXXXXXXXXXX'
CONSUMER_SERCRET    = 'XXXXXXXXXXXXXXXX'
ACCESS_TOKEN        = 'XXXXXXXXXXXXXXXX'
ACCESS_TOKEN_SECRET = 'XXXXXXXXXXXXXXXX'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SERCRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

def limit_handled(curspr):
    while True:
        try:
            yield  curspr.next()
        except TweepError:
            write_data()
            time.sleep(15 * 60)

def fetch_reply_tweet(tweet):

    try:
        reply_obj = api.get_status(tweet.in_reply_to_status_id_str)

        re_text = processing_data(reply_obj.text)

        return re_text
    except TweepError as e:
        return "notext"


taggger = MeCab.Tagger("-Owakati")

pattern_retweet = re.compile(r"RT.*?:")
pattern_link = re.compile(r"https:")
pattern_hashtag = re.compile(r"#")

check_banned_chars = ('#', '【','】', '@', '✋', '(', ')')

def processing_data(str):

    match_retweet = pattern_retweet.match(str)
    if match_retweet:
        str = str.split(r":", maxsplit=1)[1]

    match_link = pattern_link.search(str)
    if match_link:
        str = str.rsplit(r"https", maxsplit=1)[0]

    match_hashtag = pattern_hashtag.search(str)
    if match_hashtag:
        str = str[0:match_hashtag.start()]

    str = taggger.parse(str).split(" ")
    str = "_" + " _".join(str)
    str = str[0:-2]


    for char in check_banned_chars:
        if char in str:
            return "notext"


    if len(str) == 0: return "notext"

    return str



def write_data():
    print('go to tweet')
    with open("tweet.from", "a", encoding="utf8") as f:
        for tw in tweet_list:
            f.write(tw + "\n")

    tweet_list.clear()

    print('move to retweet')

    with open("tweet.to", "a", encoding="utf8") as f:
        for rtw in retweet_list:
            f.write(rtw + "\n")

    retweet_list.clear()





if __name__ == '__main__':

    tweet_list = []
    retweet_list = []

    print('ツイートとリツイートの抽出')
    

    for tweet in limit_handled(tweepy.Cursor(api.search, q="").items()):



        reply_id = tweet.in_reply_to_status_id_str

        if reply_id is None: continue

        re_text = fetch_reply_tweet(tweet)
        if re_text is "notext": continue

        text = processing_data(tweet.text)
        if text is "notext": continue

        tweet_list.append(text)
        retweet_list.append(re_text)


