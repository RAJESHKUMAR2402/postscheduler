import requests
from flask import Flask, request, jsonify, render_template
import tweepy
from datetime import datetime
from threading import Thread
import pytz

app = Flask(__name__)

# Replace these values with your actual Twitter API keys
api_key = "vYkTYR5cj2v5NLo4vX1IjsKmz"
api_secret = "tXT7yDVlB5Llc9Ti15ZvBfL9HkmOmTe079TninKPAuW19oPAKC"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAHnznwEAAAAA2S18cSGfvtx4Zgo8R8Un2WPysRg%3DCAi2bqDdWfb5r7Vfcgk2DRvcH7wckzUdh43Quwobnwv3RA6dKU"
access_token = "1528221150484242432-b50EQi29covddMYY9JBW45eTUkC1PM"
access_token_secret = "MIFygSSEpVqRrTso8fjC3l9NyHRTzrxrsarVD4FnYbKGS"
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

# Authenticate with OAuth 1.0a
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)

# Create the API object
api = tweepy.API(auth)

def post_to_facebook(message):
    # Replace this function with your actual API call to post on Facebook
    # Make sure to use your own valid access token
    access_token = "EAAM4vJMj6foBAGbqc2X0hrkahZAZC4P9Urpw20o1bg6zR0221IK9HAgRX4vFj5g47S4XYebGHALaPZAnaIcvsVuUgc03QB92OUgXZC3zWPvYsi4b19jYPOhqrgzqbVvuclbvX1nTZCAjmEU6kZAzlynaMBYM32EiQgAvo5VHGPZBaCrIDD3Jgtt"

    # API endpoint URL
    url = f"https://graph.facebook.com/v16.0/me/feed"

    # Set the data to be sent in the request body
    data = {
        "message": message,
        "access_token": access_token
    }

    try:
        # Send the POST request
        response = requests.post(url, data=data)

        # Check the response status
        if response.status_code == 200:
            # Request succeeded
            response_data = response.json()
            return response_data
        else:
            # Request failed
            return f"API request failed with status: {response.status_code}. {response.text}"
    except requests.exceptions.RequestException as e:
        # Request encountered an error
        return f"Request error: {e}"

def post_to_twitter(message):
    text = f" {message}"
    try:
        client.create_tweet(text=text)
        return "Posted on Twitter successfully!"
    except tweepy.TweepyException as e:
        return f"Error: Failed to create tweet on Twitter.\n{e}"

def schedule_post_facebook(message, post_time):
    # Get the current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    # Calculate the delay until the scheduled time
    delay = (post_time - now).total_seconds()

    # Start a new thread to handle the post at the scheduled time
    def post_thread():
        if delay > 0:
            # Wait until the scheduled time
            import time
            time.sleep(delay)

        # Post to Facebook
        post_to_facebook(message)

    thread = Thread(target=post_thread)
    thread.start()

def schedule_post_twitter(message, post_time):
    # Get the current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    # Calculate the delay until the scheduled time
    delay = (post_time - now).total_seconds()

    # Start a new thread to handle the post at the scheduled time
    def post_thread():
        if delay > 0:
            # Wait until the scheduled time
            import time
            time.sleep(delay)

        # Post to Twitter
        post_to_twitter(message)

    thread = Thread(target=post_thread)
    thread.start()

def schedule_post(message, post_time, post_facebook=True, post_twitter=True):
    if post_facebook:
        schedule_post_facebook(message, post_time)
    if post_twitter:
        schedule_post_twitter(message, post_time)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post', methods=['POST'])
def handle_post_request():
    try:
        # Get the message and schedule time from the form data
        message = request.form.get('message')
        post_time = request.form.get('post_time')

        # Convert the form input to the correct time format for scheduling
        dt_format = "%Y-%m-%dT%H:%M"  # DateTime format from the form
        post_time_dt = datetime.strptime(post_time, dt_format)

        # Convert to IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        post_time_dt = ist.localize(post_time_dt)

        # Get the values of the checkboxes (if checked, returns '1', otherwise None)
        post_facebook = request.form.get('post_facebook')
        post_twitter = request.form.get('post_twitter')

        # Schedule the post for Facebook and/or Twitter based on the checkboxes
        schedule_post(message, post_time_dt, post_facebook=='1', post_twitter=='1')

        return render_template('result.html', message=message, post_time=post_time)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
