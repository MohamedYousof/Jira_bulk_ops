import csv
import os
import sys
from jira import JIRA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EMAIL = os.getenv("EMAIL")
API_KEY = os.getenv("JIRA_API_KEY")
DOMAIN = os.getenv("DOMAIN")
PROJECT_KEY = "NA"
CUSTOM_FIELD_ACCEPTANCE = "customfield_10130"
CUSTOM_FIELD_DESIGN_LINK = "customfield_10131"
CSV_FILE = "user_stories.csv"

def connect_to_jira():
    """Connect to Jira instance with error handling."""
    if not API_KEY:
        print("Error: JIRA_API_KEY not found in environment variables.")
        sys.exit(1)
    try:
        return JIRA(server=DOMAIN, basic_auth=(EMAIL, API_KEY))
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        sys.exit(1)

def validate_row(row):
    """Validate CSV row for required fields."""
    required_fields = ["Summary", "Description", "Acceptance Criteria"]
    optional_fields = ["Issue ID", "Design Link", "Epic"]
    missing_fields = [field for field in required_fields if field not in row or not row[field]]
    if missing_fields:
        print(f"Invalid row, missing fields {missing_fields}: {row}")
        return False
    if not row["Summary"].strip():
        print(f"Invalid row, empty Summary: {row}")
        return False
    return True

def format_acceptance_criteria(criteria):
    """Format Acceptance Criteria for plain text with actual newlines."""
    # Replace wiki markup bullets (*) with plain text bullets (- )
    # Replace \n with actual newline character
    lines = criteria.split("\\n")
    formatted_lines = [line.replace("*", "- ").strip() for line in lines]
    return "\n".join(formatted_lines)

def update_csv_with_issue_id(original_issue_id, new_issue_id, row_data):
    """Update the CSV file with the new issue ID for a created story."""
    temp_file = CSV_FILE + '.tmp'
    with open(CSV_FILE, 'r', encoding='utf-8') as file, open(temp_file, 'w', encoding='utf-8', newline='') as temp:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(temp, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        for row in reader:
            if row.get("Issue ID", "").strip() == original_issue_id:
                row["Issue ID"] = new_issue_id
            writer.writerow(row)
    os.replace(temp_file, CSV_FILE)

def update_user_story(jira, issue_id, row):
    """Update an existing user story."""
    try:
        issue = jira.issue(issue_id)
        fields = {
            "summary": row["Summary"],
            "description": row["Description"],
            CUSTOM_FIELD_ACCEPTANCE: format_acceptance_criteria(row["Acceptance Criteria"]),
        }
        if "Design Link" in row and row["Design Link"]:
            fields[CUSTOM_FIELD_DESIGN_LINK] = row["Design Link"]
        else:
            fields[CUSTOM_FIELD_DESIGN_LINK] = None  # Clear if empty
        if "Epic" in row and row["Epic"]:
            fields["parent"] = {"key": row["Epic"]}
        else:
            fields["parent"] = None  # Remove parent if empty

        issue.update(fields=fields)
        print(f"Updated issue {issue_id}")
        return issue_id
    except Exception as e:
        print(f"Error updating issue '{issue_id}': {e}")
        return None

def create_user_story(jira, row):
    """Create a new user story and update CSV with the new issue ID."""
    issue_dict = {
        "project": {"key": PROJECT_KEY},
        "summary": row["Summary"],
        "description": row["Description"],
        "issuetype": {"name": "Story"},
        CUSTOM_FIELD_ACCEPTANCE: format_acceptance_criteria(row["Acceptance Criteria"]),
    }
    if "Design Link" in row and row["Design Link"]:
        issue_dict[CUSTOM_FIELD_DESIGN_LINK] = row["Design Link"]
    if "Epic" in row and row["Epic"]:
        issue_dict["parent"] = {"key": row["Epic"]}

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"Created issue {new_issue.key}")
        # Update CSV with the new issue ID for the row with empty Issue ID
        original_issue_id = row.get("Issue ID", "").strip()
        if not original_issue_id:  # Only update if it was a new story (empty Issue ID)
            update_csv_with_issue_id(original_issue_id, new_issue.key, row)
        return new_issue.key
    except Exception as e:
        print(f"Error creating issue for '{row['Summary']}': {e}")
        return None

def process_csv():
    """Read CSV and create or update user stories."""
    jira = connect_to_jira()
    processed_issues = []
    
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not validate_row(row):
                    print(f"Skipping row: {row}")
                    continue
                issue_id = row.get("Issue ID", "").strip()
                if issue_id:
                    result = update_user_story(jira, issue_id, row)
                else:
                    result = create_user_story(jira, row)
                if result:
                    processed_issues.append(result)
    except FileNotFoundError:
        print(f"CSV file '{CSV_FILE}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
    
    return processed_issues

def main():
    """Main function to execute bulk creation/update."""
    print("Starting bulk user story processing...")
    processed_issues = process_csv()
    if processed_issues:
        print(f"Successfully processed {len(processed_issues)} issues: {', '.join(processed_issues)}")
    else:
        print("No issues were processed.")
    print("Bulk processing complete.")

if __name__ == "__main__":
    main()
