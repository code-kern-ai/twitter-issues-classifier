# twitter-issues-classifier
Ok, you all most likely heard it. Twitter went open-source. That's amazing. Curious as I am, I wanted to dive into their [repository](https://github.com/twitter/the-algorithm).

When looking into their issues list, I was laughing out loud. Check this:

![Funny issues](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/fauqrbxiavcojqyyp27n.png)

GitHub users are making fun on the whole release, and turn the issues list into a jokes section.

As an engineer on the dev team of Twitter, however, I would be really annoyed. Differentiating between issues of trolls and non-trolls is now a new todo on their list. So let's try to help them. I'm going to show a first, very simple version of a classifier for identifying troll-issues in the Twitter repo. Of course, I'm sharing the work on GitHub as well. Here's the [repo](https://github.com/code-kern-ai/twitter-issues-classifier).

---

## Getting the data

I've scraped the issues with a simple Python script, which I also shared in the repo:
```python
import requests
import json

PAT = "add-your-PAT-here" # see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
owner = "twitter" 
repo = "the-algorithm" 

url = f"https://api.github.com/repos/{owner}/{repo}/issues"
headers = {"Authorization": f"Bearer {PAT}"}

all_issues = []

while url:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        issues = response.json()
        all_issues.extend(issues)
        if "next" in response.links:
            url = response.links["next"]["url"]
        else:
            url = None
    else:
        print(f"Failed to retrieve issues (status code {response.status_code}): {response.text}")
        break

issues_reduced = []
for issue in all_issues:
    issue_reduced = {
        "title": issue["title"],
        "body": issue["body"],
        "html_url": issue["html_url"],
        "reactions_laugh": issue["reactions"]["laugh"],
        "reactions_hooray": issue["reactions"]["hooray"],
        "reactions_confused": issue["reactions"]["confused"],
        "reactions_heart": issue["reactions"]["heart"],
        "reactions_rocket": issue["reactions"]["rocket"],
        "reactions_eyes": issue["reactions"]["eyes"],
    }
    issues_reduced.append(issue_reduced)

with open("twitter-issues.json", "w") as f:
    json.dump(issues_reduced, f)

print(f"Retrieved {len(all_issues)} issues and saved to twitter-issues.json")
```

Of course, these days, I didn't write the code for this myself. ChatGPT did that, but you all already know that.

I decided to reduce the downloaded data a bit, because much of the content didn't seem to be relevant to me. Instead, I wanted to just have the URL to the issue, the title and body, and some potentially interesting metadata in form of the reactions.

An example of this looks as follows:
```json
  {
    "title": "adding Documentation",
    "body": null,
    "html_url": "https://github.com/twitter/the-algorithm/pull/838",
    "reactions_laugh": 0,
    "reactions_hooray": 0,
    "reactions_confused": 0,
    "reactions_heart": 0,
    "reactions_rocket": 0,
    "reactions_eyes": 0
  },
```

## Building the classifier

With the data downloaded, I started [refinery](https://github.com/code-kern-ai/refinery) on my local machine. With refinery, I'm able to label a little bit of data and build some heuristics to quickly test if my idea works. It's open-sourced under Apache 2.0, you can just grab it and try along.

Simply upload the `twitter-issues.json` file we just created:
![Upload data](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/9qo16d8ceqz608tjrw77.png)

For the `title` and `body` attributes, I added two `distilbert-base-uncased` embeddings directly from Hugging Face.
![Project settings](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/5a1dgvv8qms3p9ur35xo.png)

After that, I set up three labeling tasks, of which for now only the `Seriousness` task is relevant.
![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/nox30jrtt0hjxwbswr48.png)

Diving into the data, I labeled a few examples to see how the data looks like and to get some reference labels for my automations I want to build.
![Labeling data](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3jd82pdkx36t0fma4kk3.png)

I realized that quite often, people are searching for jobs in issues. So i started building my first heuristic for this, in which I use a lookup list that I created to search for appearances of job-terms. I'm going to later combine this via [weak supervision](https://www.youtube.com/watch?v=8TusRTqp9uQ&ab_channel=KernAI) with other heuristics to power my classifier.

![Job search heuristic](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/0ckwz2bnmvufgpc3tffd.png)

For reference, this is how the lookup lists looks like. Terms are automatically added while labeling spans (which is also why i had three labeling tasks, one for classification and two for span labeling), but I could also have uploaded a CSV file of terms.
![Lookup list job terms](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ujx1p9nl1tmxla6t87it.png)

As I also already labeled a bit of data, I created a few active learners:
![Active Learner](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/33rx85uw1tbmha1tpv62.png)

With weak supervision, I can easily combine this active learner with my previous job search classifier without having to worry about conflicts, overlaps and the likes.

Also I noted a couple of issues with just a link to play chess online:
![Play chess](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/g3fqgvwamhgzs0n78k4v.png)

So i added a heuristic for detecting links via spaCy.
![Title is link](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ffrrs2zfjqli9j90o1wf.png)

Of course, I also wanted to create a GPT-based classifier, since this is publicly available data. However, GPT seems to be down while I'm initially building this :(
![GPT-down](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/lfu1tuoe68be0rbj4p5t.png)

After circa 20 minutes of labeling and working with the data, this is how my heuristics tab looked like
![All heuristics](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7uvk32nddy6nmyfaqap1.png)

So there are mainly active learners, some lookup lists and regular-expression like heuristics. I will add GPT in the comments section as soon as I can access it again :)

Now, I weakly supervised the results:
![Distribution](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ktxp9dfxreq3zl9yf7vb.png)

You can see that the automation already nicely fits the distribution of trolls vs. non-trolls.

I also noticed a strong difference in confidence:
![Confidence distribution](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/r214w76egjq997uumjun.png)

So I headed over to the data browser and configured the confidence so I only see the records with above 80% confidence.
![Data browser](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/24qgjr6ud74zlejqabd9.png)

Notice that in here, we could also filter by single heuristic hits, e.g. to find records where different heuristics vote different labels:
![Heuristics filtering](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/tpkcvwqi362oucgzhvz2.png)

In the dashboard, I now filter for the high confidence records and see that our classifier is performing quite good already (note, this isn't even using GPT yet!):
![Confusion matrix](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/6ohc6kwjjmuchm3qyoq0.png)

## Next steps
I exported the project snapshot and labeled examples into the [public repository](https://github.com/code-kern-ai/twitter-issues-classifier) (`twitter_default_all.json.zip`), so you can play with the bit of labeled data yourself. I'll continue on this topic the next days, and we'll add a YouTube video for this article for a version 2 of the classifier. There certainly are further attributes, we can look into, such as taking the length of the body into account (I already saw that shorter bodys typically are troll-like).

Also, keep in mind that this is an excellent way to benchmark how power GPT can add for your use case. Simply add it as a heuristic, try a few different prompts, and play with excluding or adding it from your heuristics in the weak supervision procedure. For instance, here, I excluded GPT:

![All heuristics](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7uvk32nddy6nmyfaqap1.png)

---

I'm really thrilled about Twitter going open-source with their algorithm, and I'm sure it will add a lot of benefits. What you can already tell is due to the nature of Twitter's community, issues are often written by trolls. So finding detecting such will be important for the dev team of Twitter. Maybe this post here can be of help for that :)
