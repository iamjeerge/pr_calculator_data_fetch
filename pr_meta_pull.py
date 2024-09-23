import requests
import csv
from datetime import datetime


# Function to get all PRs in a repository
def get_all_prs(repo_owner, repo_name, github_token):
    prs = []
    page = 1
    per_page = 100  # GitHub API returns max 100 results per page

    while True:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=all&per_page={per_page}&page={page}"
        headers = {"Authorization": f"token {github_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch PRs: {response.status_code}")
            return prs

        data = response.json()
        if not data:  # Break loop if no more data
            break

        prs.extend(data)
        page += 1

    return prs


# Function to calculate time taken to merge PRs and save data to CSV
def calculate_merge_time_and_write_to_csv(prs, csv_file):
    # Prepare CSV file
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["PR Number", "Created At", "Merged At", "Time to Merge", "Author"])

        # Process each PR
        for pr in prs:
            pr_number = pr.get("number")
            created_at = pr.get("created_at")
            merged_at = pr.get("merged_at")
            author = pr.get("user").get("login")

            # If PR is not merged, skip it
            if not merged_at:
                continue

            # Convert times to datetime objects
            created_at_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            merged_at_dt = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ")

            # Calculate the time taken to merge in minutes
            time_to_merge_seconds = (merged_at_dt - created_at_dt).total_seconds()
            time_to_merge_minutes = (
                time_to_merge_seconds / 60
            )  # Convert seconds to minutes

            # Write PR data to CSV
            writer.writerow(
                [
                    pr_number,
                    created_at_dt,
                    merged_at_dt,
                    round(time_to_merge_minutes, 2),
                    author
                ]
            )

    print(f"Data written to {csv_file}")


# Example usage
def main():
    # Replace these variables with your own repo details and GitHub token
    repo_owner = ""
    repo_name = ""
    github_token = ""
    csv_file = "pr_merge_times.csv"

    # Get all PRs
    prs = get_all_prs(repo_owner, repo_name, github_token)

    # Calculate merge times and write to CSV
    calculate_merge_time_and_write_to_csv(prs, csv_file)


# Run the main function
if __name__ == "__main__":
    main()
