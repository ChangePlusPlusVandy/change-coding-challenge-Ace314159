import itertools
import html
import random
import requests

# Authentication token unique to developer
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAO0THwEAAAAAPEDYWqNSbHDsb85W8kYWMWuNQVs%3DQTP8Sxzb5bEGrLSxlnHGJUxwByOJyvyG79X7ZI15oQWbH15s6t'

TIMELINE_ENDPOINT = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
REQUEST_HEADERS = {
    'Authorization': f'Bearer {BEARER_TOKEN}',
}

# Twitter Handles of Elon and Kanye
ELON_HANDLE = 'elonmusk'
ELON_NAME = 'elon'
KANYE_HANDLE = 'kanyewest'
KANYE_NAME = 'kanye'


# Returns true if the tweet is genuinely by the user
# Criteria:
#   No retweets
#   No replies
#   Does not tag other users
#   No links, videos or images
def is_genuine_tweet(tweet):
    # Retweet Detection
    if tweet['retweeted']:
        return False

    # Reply Detection
    if tweet['in_reply_to_status_id'] is not None:
        return False

    # Tagged Users Detection
    if len(tweet['entities']['user_mentions']) > 0:
        return False

    # Link Detection
    if len(tweet['entities']['urls']) > 0:
        return False

    # Embedded Image or Video Detection
    if 'media' in tweet['entities'] and len(tweet['entities']['media']) > 0:
        return False

    return True


# Tweets returned newest first, so we page by setting max id
def get_tweets_with_id(user, max_id):
    timeline = requests.get(TIMELINE_ENDPOINT, headers=REQUEST_HEADERS, params={
        'screen_name': user,
        'count': 200,
        'max_id': max_id,
    }).json()

    if timeline:
        # Subtract 1 so we don't get this tweet again
        # The tweet shouldn't be 0 (hopefully)
        new_max_id = timeline[-1]['id'] - 1
    else:
        # No more tweets left
        new_max_id = None

    genuine_tweets = filter(is_genuine_tweet, timeline)
    texts = map(lambda tweet: tweet['text'], genuine_tweets)
    unescaped_texts = map(html.unescape, texts)  # Replaces HTML escaped characters like &amp; with &
    return (unescaped_texts, new_max_id)


def get_all_tweets(user):
    (tweets, max_id) = get_tweets_with_id(user, None)
    # max_id is None as long new tweets were returned
    while max_id:
        (older_tweets, max_id) = get_tweets_with_id(user, max_id)
        tweets = itertools.chain(tweets, older_tweets)

    return tweets


def game():
    print("Reading Elon's Tweets")
    elon_tweets = list(map(lambda tweet: (tweet, ELON_NAME), get_all_tweets(ELON_HANDLE)))
    print("Reading Kanye's Tweets")
    kanye_tweets = list(map(lambda tweet: (tweet, KANYE_NAME), get_all_tweets(KANYE_HANDLE)))

    num_elon = len(elon_tweets)
    num_kanye = len(kanye_tweets)
    num_elon_correct = 0
    num_kanye_correct = 0

    randomized_tweets = elon_tweets + kanye_tweets
    random.shuffle(randomized_tweets)

    print("Enter 'Kanye' if you think Kanye tweeted, and enter 'Elon' if you think Elon tweeted")
    for tweet, person in randomized_tweets:
        print()
        print('Who wrote this tweet:')
        print(tweet)
        guess = input('Your Guess: ')
        if guess.lower() == person:
            if person == ELON_NAME:
                num_elon_correct += 1
            elif person == KANYE_NAME:
                num_kanye_correct += 1
            print('Correct!')
        else:
            print('Incorrect')

    num_total_correct = num_elon_correct + num_kanye_correct
    num_total = num_elon + num_kanye

    overall_acc = num_total_correct / num_total * 100
    kanye_acc = num_kanye_correct / num_kanye * 100
    elon_acc = num_elon_correct / num_elon * 100

    print()
    print('Game Statistics')
    print(f'Overall Accuracy: {num_total_correct} / {num_total} = {overall_acc:.2f}%')
    print(f'Kanye Accuracy: {num_kanye_correct} / {num_kanye} = {kanye_acc:.2f}%')
    print(f'Elon Accuracy: {num_elon_correct} / {num_elon} = {elon_acc:.2f}%')


if __name__ == '__main__':
    game()
