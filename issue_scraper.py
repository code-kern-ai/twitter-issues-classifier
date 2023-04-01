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
