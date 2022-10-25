import json
from flask import request, Flask, Blueprint, render_template, redirect, url_for
import praw
import requests
from praw.models import MoreComments
import datetime

#reddit api details

def merge(list1, list2, list3, list4, list5, list6, list7):
      
    merged_list = tuple(zip(list1, list2, list3, list4, list5, list6, list7)) 
    return merged_list

list_of_searches = []

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        search = request.form["searchtext"]
        list_of_searches.append(search)
        return redirect(url_for("searches", srch=search))
    else:
        return render_template("index.html")

all = reddit.subreddit("all")

@app.route("/search/<srch>", methods=["POST", "GET"])
def searches(srch):
    if request.method == "POST":
        search = request.form["searchtext"]
        list_of_searches.append(search)
        return redirect(url_for("searches", srch=search))

    titles = []
    comms = []
    upvotes = []
    date = []
    platform = []
    url = []
    subreddit = []
    breakout = False

    html_text = requests.get('http://hn.algolia.com/api/v1/search?query=' + srch + '&tags=story').text
    data = json.loads(html_text)
    hits = data["hits"]

    for x in range(2): 
        if len(hits)>x:
            titles.append("")
            comms.append(hits[x]['title'])
            upvotes.append(hits[x]['points'])
            format_date = hits[x]['created_at']
            date.append(format_date[0:10])
            platform.append("Hacker News")
            subreddit.append("")
            url.append("https://news.ycombinator.com/item?id=" + hits[x]['objectID'])
        else:
            break

    for submission in reddit.subreddit('all').search(srch, limit=20):
        submission.comment_sort = 'top'
        submission.comment_limit = 2
        submission.comments.replace_more(limit=0)
        if breakout:
            break
        comments = submission.comments
        for comment in comments:
            if len(comms) == 8:
                breakout = True
                break
            elif len(comms) < 13 and comment.stickied == False:
                titles.append(submission.title)
                comms.append(comment.body)
                upvotes.append(comment.ups)
                formatted_date = datetime.datetime.utcfromtimestamp(comment.created)
                formatted_date2 = str(formatted_date)
                date.append(formatted_date2[0:10])
                platform.append("Reddit: r/")
                url.append("https://www.reddit.com" + submission.permalink)
                subreddit.append(submission.subreddit)
                if len(comms) % 2 == 0:
                    break
            elif len(comms) < 11 and comment.stickied == True:
                pass

    data = merge(titles,comms,upvotes,date,platform,url,subreddit) 
    sorted_by_popularity= sorted(data, key=lambda tup: tup[2], reverse=True)

    return render_template("search.html", data=sorted_by_popularity, srch=srch)

@app.route("/substack")
def substack():
    return render_template("substack.html")


@app.route("/list_of", methods=["POST", "GET"])
def searchlist():
    return render_template("list_of_searches.html", list = list_of_searches)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)


