import json
from flask import request, Flask, Blueprint, render_template, redirect, url_for
import praw
import requests

reddit = praw.Reddit(
    client_id='lLzAuBHDjs8cCYEuTrKh3w',
    client_secret='uqMNWpDSXYxLXpgZ90y-wWspCgYC7A',
    username='servesociety',
    password='Hunters3!',
    user_agent="CrowdSearch",
)

def merge(list1, list2, list3, list4, list5):
      
    merged_list = tuple(zip(list1, list2, list3, list4, list5)) 
    return merged_list

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        search = request.form["searchtext"]
        return redirect(url_for("searches", srch=search))
    else:
        return render_template("index.html")

all = reddit.subreddit("all")

@app.route("/search/<srch>", methods=["POST", "GET"])
def searches(srch):
    if request.method == "POST":
        search = request.form["searchtext"]
        return redirect(url_for("searches", srch=search))

    titles = []
    comms = []
    upvotes = []
    date = []
    platform = []
    breakout = False

    html_text = requests.get('http://hn.algolia.com/api/v1/search?query=' + srch + '&tags=story').text
    data = json.loads(html_text)
    hits = data["hits"]

    for x in range(2): 
        if hits != []:
            titles.append(hits[x]['title'])
            postid = hits[x]['objectID']
            comms.append('https://news.ycombinator.com/item?id='+ postid)
            upvotes.append(hits[x]['points'])
            date.append(hits[x]['created_at'])
            platform.append("Hacker News")
        else:
            break

    for submission in reddit.subreddit('all').search(srch, limit=20):
        if breakout:
            break
        comments = submission.comments
        for comment in comments:
            if len(comms) == 6:
                breakout = True
                break
            elif len(comms) < 11 and comment.stickied == False:
                titles.append(submission.title)
                comms.append(comment.body)
                upvotes.append(comment.ups)
                date.append(comment.created)
                platform.append("Reddit")
                if len(comms) % 2 == 0:
                    break
            elif len(comms) < 11 and comment.stickied == True:
                pass

    data = merge(titles,comms,upvotes,date,platform) 
    print(data)
    return render_template("search.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)


