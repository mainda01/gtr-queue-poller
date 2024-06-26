import subprocess
import json
from datetime import datetime
import csv
import os

# This dimension has the highest impact on confidence.
# A high number of open PRs suggests a backlog, which directly affects the queue and processing time for new PRs.
backlog_factor = 4

# This dimension reflects the delay in the review process.
# If PRs are awaiting approval for a long time, it suggests inefficiencies or unavailability of reviewers.
delay_factor = 3

# This dimension shows how quickly PRs are integrated once they are ready.
# Delays here might indicate issues in the final stages of merging, but it is less critical than the initial approval.
queue_factor = 2

# This dimension provides insight into the team's recent activity.
# If PRs are being merged regularly, it indicates an active review process, even if the queue is long.
activity_factor = 1


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


def calculate_risk_basis(
    open_pr_count, time_since_last_merged, oldest_waiting_age, oldest_ready_age
):

    # Calculate confidence score
    risk_basis = (
        backlog_factor * open_pr_count
        + activity_factor * time_since_last_merged
        + delay_factor * oldest_waiting_age
        + queue_factor * oldest_ready_age
    )

    return risk_basis


def calculate_confidence_percentage(
    open_pr_count, time_since_last_merged, oldest_waiting_age, oldest_ready_age
):

    # Normalize each dimension
    open_pr_normalized = max(0, 1 / open_pr_count) if open_pr_count else 1
    last_merged_normalized = (
        max(0, 1 / time_since_last_merged) if time_since_last_merged else 1
    )
    oldest_waiting_normalized = (
        max(0, 1 / oldest_waiting_age) if oldest_waiting_age else 1
    )
    oldest_ready_normalized = max(0, 1 / oldest_ready_age) if oldest_ready_age else 1

    weighted_score = (
        backlog_factor * open_pr_normalized
        + activity_factor * last_merged_normalized
        + delay_factor * oldest_waiting_normalized
        + queue_factor * oldest_ready_normalized
    )

    # Normalize to percentage (0 to 100)
    max_weighted_score = backlog_factor + activity_factor + delay_factor + queue_factor
    confidence_percentage = (weighted_score / max_weighted_score) * 100

    return confidence_percentage


def save_to_csv(data, filename="risk_basiss.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(
                [
                    "Timestamp",
                    "Open PR Count",
                    "Time Since Last Merge (h)",
                    "Oldest Waiting Age (h)",
                    "Oldest Ready Age (h)",
                    "Risk Basis",
                    "Confidence Percentage",
                ]
            )
        writer.writerow(data)


if __name__ == "__main__":
    last_merged_time = get_last_merged_pr_time()
    if not last_merged_time:
        print("Failed to get last merged PR time")
        exit()

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

    risk_basis = calculate_risk_basis(
        open_pr_count, time_since_last_merged, oldest_waiting_age, oldest_ready_age
    )

    confidence_percentage = calculate_confidence_percentage(
        open_pr_count, time_since_last_merged, oldest_waiting_age, oldest_ready_age
    )

    print(f"{open_pr_count} open PRs")
    print(f"Last Merge {round(time_since_last_merged, 1)}h")
    print(f"Oldest Awaiting Approval {round(oldest_waiting_age, 1)}h")
    print(f"Oldest Ready For Merge {round(oldest_ready_age, 1)}h")
    print(f"Risk: {round(risk_basis, 2)}")
    print(f"Confidence Percentage: {round(confidence_percentage, 2)}%")

    # Save data to CSV
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    save_to_csv(
        [
            timestamp,
            open_pr_count,
            round(time_since_last_merged, 1),
            round(oldest_waiting_age, 1),
            round(oldest_ready_age, 1),
            round(risk_basis, 2),
            round(confidence_percentage, 2),
        ]
    )
