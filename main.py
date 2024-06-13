import subprocess
import json
from datetime import datetime


def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"Error message: {result.stderr}")
        return None
    return result.stdout.strip()


def get_last_merged_pr_time():
    cmd = "gh pr list --repo LexisNexis-TFE/tfe-prod-us-globaltransit-firewall --base prod --state merged --limit 1 --json 'updatedAt' -q '.[].updatedAt'"
    result = run_command(cmd)
    if result:
        try:
            last_merged_time = datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")
            return last_merged_time
        except ValueError as e:
            print(f"Error parsing last merged PR time: {result}")
            return None
    return None


def get_open_pr_count():
    cmd = "gh pr list --repo LexisNexis-TFE/tfe-prod-us-globaltransit-firewall --base prod --state open --json 'id'"
    result = run_command(cmd)
    if result:
        try:
            open_prs = json.loads(result)
            return len(open_prs)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {result}")
            return 0
    return 0


def get_oldest_pr_with_label(label):
    cmd = f"gh pr list --repo LexisNexis-TFE/tfe-prod-us-globaltransit-firewall --base prod --label '{label}' --json 'createdAt' -q '.[].createdAt' | tail -1"
    result = run_command(cmd)
    if result:
        try:
            oldest_pr_time = datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")
            return oldest_pr_time
        except ValueError as e:
            print(f"Error parsing oldest PR time with label {label}: {result}")
            return None
    return None


def calculate_confidence_score(
    open_pr_count, time_since_last_merged, oldest_waiting_age, oldest_ready_age
):

    # This dimension has the highest impact on confidence because a high number of open PRs suggests a backlog, which directly affects the queue and processing time for new PRs.
    backlog_factor = 2

    # This dimension provides insight into the team's recent activity. If PRs are being merged regularly, it indicates an active review process, even if the queue is long.
    activity_factor = 1.5

    # This dimension reflects the delay in the review process. If PRs are awaiting approval for a long time, it suggests inefficiencies or unavailability of reviewers.
    delay_factor = 1.5

    # This dimension shows how quickly PRs are integrated once they are ready. Delays here might indicate issues in the final stages of merging, but it is less critical than the initial approval.
    queue_factor = 1

    # Calculate confidence score
    confidence_score = (
        backlog_factor * open_pr_count
        + activity_factor * time_since_last_merged
        + delay_factor * oldest_waiting_age
        + queue_factor * oldest_ready_age
    )

    print(f"{open_pr_count} open PRs")
    print(f"Last Merge {round(time_since_last_merged, 1)}h")
    print(f"Oldest Awaiting Approval {round(oldest_waiting_age, 1)}h")
    print(f"Oldest Ready For Merge {round(oldest_ready_age, 1)}h")
    print(f"Confidence Score: {round(confidence_score, 2)}\n")

    return confidence_score


def run_test_cases():
    test_cases = [
        {  # baseline
            "open_pr_count": 5,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 5,
        },
        {  # open_pr_count more
            "open_pr_count": 10,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 5,
        },
        {  # open_pr_count less
            "open_pr_count": 2,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 5,
        },
        {  # time_since_last_merged more
            "open_pr_count": 5,
            "time_since_last_merged": 10,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 5,
        },
        {  # time_since_last_merged less
            "open_pr_count": 5,
            "time_since_last_merged": 2,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 5,
        },
        {  # oldest_waiting_age more
            "open_pr_count": 5,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 10,
            "oldest_ready_age": 5,
        },
        {  # oldest_waiting_age less
            "open_pr_count": 5,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 2,
            "oldest_ready_age": 5,
        },
        {  # oldest_ready_age more
            "open_pr_count": 5,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 10,
        },
        {  # oldest_ready_age less
            "open_pr_count": 5,
            "time_since_last_merged": 5,
            "oldest_waiting_age": 5,
            "oldest_ready_age": 2,
        },
        {  # all dimensions more
            "open_pr_count": 10,
            "time_since_last_merged": 10,
            "oldest_waiting_age": 10,
            "oldest_ready_age": 10,
        },
        {  # all dimensions less
            "open_pr_count": 2,
            "time_since_last_merged": 2,
            "oldest_waiting_age": 2,
            "oldest_ready_age": 2,
        },
        {  # mixed case 1
            "open_pr_count": 10,
            "time_since_last_merged": 2,
            "oldest_waiting_age": 10,
            "oldest_ready_age": 2,
        },
        {  # mixed case 2
            "open_pr_count": 2,
            "time_since_last_merged": 10,
            "oldest_waiting_age": 2,
            "oldest_ready_age": 10,
        },
    ]

    for i, case in enumerate(test_cases):
        print(f"Test Case {i+1}:")
        calculate_confidence_score(
            case["open_pr_count"],
            case["time_since_last_merged"],
            case["oldest_waiting_age"],
            case["oldest_ready_age"],
        )


if __name__ == "__main__":
    # run_test_cases()
    last_merged_time = get_last_merged_pr_time()
    if not last_merged_time:
        print("Failed to get last merged PR time")
        exit

    open_pr_count = get_open_pr_count()
    oldest_waiting_for_approval = get_oldest_pr_with_label("Awaiting Approval")
    oldest_ready_for_merge = get_oldest_pr_with_label("Ready For Merge")

    time_since_last_merged = (
        datetime.utcnow() - last_merged_time
    ).total_seconds() / 3600

    oldest_waiting_age = (
        (datetime.utcnow() - oldest_waiting_for_approval).total_seconds() / 3600
        if oldest_waiting_for_approval
        else 0
    )

    oldest_ready_age = (
        (datetime.utcnow() - oldest_ready_for_merge).total_seconds() / 3600
        if oldest_ready_for_merge
        else 0
    )

    calculate_confidence_score(
        open_pr_count, time_since_last_merged, oldest_waiting_age, oldest_ready_age
    )
