import os
import uuid  # for generating random user id values

import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest
from dotenv import load_dotenv
from flask import Flask, render_template, request
from rpi_join import RpiJoinThread
from threading import Event

# Load environment variables from a .env file
load_dotenv()

# Create a Twilio client
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY_SID"]
api_secret = os.environ["TWILIO_API_KEY_SECRET"]
twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)

# twilio_client = twilio.rest.Client(account_sid, auth_token)

RPI_THREAD = None

# Create a Flask app
app = Flask(__name__)


def find_or_create_room(room_name):
    try:
        # try to fetch an in-progress room with this name
        twilio_client.video.rooms(room_name).fetch()
    except twilio.base.exceptions.TwilioRestException:
        # the room did not exist, so create it
        twilio_client.video.rooms.create(unique_name=room_name, type="go")


def get_access_token(room_name):
    # create the access token
    access_token = twilio.jwt.access_token.AccessToken(
        account_sid, api_key, api_secret, identity=uuid.uuid4().int
    )
    # create the video grant
    video_grant = twilio.jwt.access_token.grants.VideoGrant(room=room_name)
    # Add the video grant to the access token
    access_token.add_grant(video_grant)
    return access_token


# Create a route that returns the index.html template
@app.route("/")
def serve_homepage():
    return render_template("index.html")


@app.route("/join-room", methods=["POST"])
def join_room():
    # extract the room_name from the JSON body of the POST request
    room_name = request.json.get("room_name")
    # find an existing room with this room_name, or create one
    find_or_create_room(room_name)
    # retrieve an access token for this room
    access_token = get_access_token(room_name)
    # return the decoded access token in the response
    print(access_token)
    # return {"token": access_token.to_jwt().decode()}
    return {"token": access_token.to_jwt()}

@app.route("/join-rpi", methods=["GET", "POST"])
def join_rpi():
    global RPI_THREAD
    if RPI_THREAD:
        RPI_THREAD.event.set()
        RPI_THREAD.join()
        RPI_THREAD = None
    RPI_THREAD = RpiJoinThread('myroom', Event())
    RPI_THREAD.start()
    return "Room joined"

# Start the server when this file runs
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
