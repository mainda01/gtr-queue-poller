from main import calculate_confidence_score

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
