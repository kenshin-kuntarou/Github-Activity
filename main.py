import requests
import argparse

def request(response):
    if response.status_code == 200:
        events = response.json()
        push_commits = {}
        other_messages = []

        for event in events:
            event_type = event['type']
            repo_name = event['repo']['name']
            payload = event['payload']

            if event_type == "PushEvent":
                commit_count = len(payload.get('commits', []))
                push_commits[repo_name] = push_commits.get(repo_name, 0) + commit_count
            else:
                msg = None

                if event_type == "IssuesEvent":
                    action = payload.get('action')
                    if action == "opened":
                        msg = f"Opened a new issue in {repo_name}"
                    elif action == "closed":
                        msg = f"Closed an issue in {repo_name}"
                    else:
                        msg = f"{action.capitalize()} an issue in {repo_name}"

                elif event_type == "PullRequestEvent":
                    action = payload.get('action')
                    if action == "opened":
                        msg = f"Opened a new pull request in {repo_name}"
                    elif action == "closed":
                        merged = payload.get('pull_request', {}).get('merged', False)
                        if merged:
                            msg = f"Merged a pull request in {repo_name}"
                        else:
                            msg = f"Closed a pull request in {repo_name}"
                    else:
                        msg = f"{action.capitalize()} a pull request in {repo_name}"

                elif event_type == "WatchEvent":
                    msg = f"Starred {repo_name}"

                elif event_type == "ForkEvent":
                    msg = f"Forked {repo_name}"

                # Evita mensagens vazias e repetidas consecutivas
                if msg and (not other_messages or other_messages[-1] != msg):
                    other_messages.append(msg)

        # Monta as mensagens finais, agrupando os pushes
        messages = []
        for repo, total_commits in push_commits.items():
            messages.append(f"Pushed {total_commits} commit{'s' if total_commits != 1 else ''} to {repo}")

        messages.extend(other_messages)
        return messages

    else:
        print(f"Error: {response.status_code}")
        return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-user", type=str, required=True, help="Github username")
    args = parser.parse_args()

    headers = {
        "Accept": "application/vnd.github+json"
    }

    url = f'https://api.github.com/users/{args.user}/events/public'
    response = requests.get(url, headers=headers)

    messages = request(response)
    for msg in messages:
        print(msg)

if __name__ == "__main__":
    main()
