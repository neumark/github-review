#!/usr/bin/python
import json
import sys
import os
import urllib2
import subprocess
OWNER="prezi" # edit this line
COMMITS_URL = "https://api.github.com/repos/%s/%s/commits"
DIFF_URL = "https://github.com/%s/%s/compare/%s...%s#files_bucket"
TOKEN_FILE = '.github_review_token'
SHA_FILE = '.github_last_reviewed_commit'
def token_file():
    return os.path.join(os.environ['HOME'],TOKEN_FILE)
def sha_file():
    return os.path.join(os.environ['HOME'],SHA_FILE)

USAGE = """
Usage: %s REPONAME
"""

MISSING_TOKEN_MESSAGE = """
It seems you do not have a token file yet.
Get one like this:
curl https://api.github.com/authorizations --user "%s" --data '{"scopes":["repo"],"note":"review script"}' > %s
""" % (os.environ['USER'], token_file())

def read_github_token():
    try:
        data = json.loads(open(token_file(),'r').read())
        return (data['scopes'], data['token'])
    except IOError:
        print MISSING_TOKEN_MESSAGE
        sys.exit(1)

def get_current_commit(repo, token):
    headers = {
        'Authorization': ' bearer %s' % token,
        }
    url = COMMITS_URL % (OWNER, repo)
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request, timeout=10)
    raw_response = response.read()
    response = json.loads(raw_response)
    return response[0]['sha']

def get_repo_to_review(repos):
    if len(sys.argv) != 2:
        print USAGE % sys.argv[0]
        sys.exit(1)
    return sys.argv[1]

def load_last_reviewed_commits():
    try:
        return json.loads(open(sha_file(),'r').read())
    except Exception, exc:
        print "Got exception reading last reviewed commit: %s " % str(exc)
        return {}

def save_last_reviewed_commits(current_commits):
    open(sha_file(), 'w').write(json.dumps(current_commits))

def showdiff(repo, last_reviewed_commit, current_commit):
    subprocess.call(["open", DIFF_URL % (OWNER, repo, last_reviewed_commit, current_commit)])

def main():
    repos, token = read_github_token()
    current_repo = get_repo_to_review(repos)
    last_reviewed_commits = load_last_reviewed_commits()
    current_commit = get_current_commit(current_repo, token)
    last_commit = last_reviewed_commits[current_repo] if last_reviewed_commits.has_key(current_repo) else current_commit
    last_reviewed_commits[current_repo] = current_commit
    save_last_reviewed_commits(last_reviewed_commits)
    showdiff(current_repo, last_commit, current_commit)

if __name__ == '__main__':
    main()
