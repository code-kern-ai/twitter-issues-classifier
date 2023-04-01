import requests
import json

PAT = "add-your-PAT-here" # see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
owner = "twitter" 
repo = "the-algorithm" 

url = f"https://api.github.com/repos/{owner}/{repo}/issues"
headers = {"Authorization": f"Bearer {PAT}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    issues = response.json()
    with open("twitter-issues.json", "w") as f:
        json.dump(issues, f)
    print("Issues saved to issues.json")
else:
    print(f"Failed to retrieve issues (status code {response.status_code}): {response.text}")
