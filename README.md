# Jira Bulk Operations Script

## Overview
This script automates the creation and updating of Jira user stories from a CSV file. It connects to Jira using the API and performs bulk operations based on the data provided in the CSV file.

## Prerequisites
- Python 3.6 or higher
- Jira account with API access
- Required Python packages (install using `pip install -r requirements.txt`):
  - jira
  - python-dotenv

## Setup

1. Clone or download this repository

2. Create a `.env` file in the same directory as the script with the following variables:
   ```
   JIRA_API_KEY=your_jira_api_key
   DOMAIN=https://your-domain.atlassian.net
   EMAIL=your_admin_email_in_jira
   ```

3. Update the following variables in the script if needed:
   - `PROJECT_KEY`: Your Jira project key
   - `CSV_FILE`: Path to your CSV file (default is "user_stories.csv")

## CSV File Format

The CSV file must contain the following columns:

### Required Columns
- `Summary`: The title of the user story (required)
- `Description`: Detailed description of the user story (required)
- `Acceptance Criteria`: Acceptance criteria for the user story (required)

### Optional Columns
- `Issue ID`: Existing Jira issue ID (leave empty for new stories)
- `Design Link`: Link to design documents or mockups
- `Epic`: Epic key to associate the story with

### Example CSV Format

```csv
Issue ID,Summary,Description,Acceptance Criteria,Design Link,Epic
,Create login page,Implement secure login page with username and password fields,*User can enter username and password\n*Form validates input\n*User is redirected to dashboard after successful login,https://figma.com/design-link,PROJ-123
PROJ-456,Update profile page,Add ability to update user profile details,*User can edit name\n*User can change email\n*Changes are saved when clicking Submit,https://figma.com/profile-design,PROJ-123
```

### Formatting Acceptance Criteria

The Acceptance Criteria field supports a special format:
- Use `\n` to create line breaks in the text
- Use `*` at the beginning of lines to create bullet points (will be converted to `-` in Jira)

Example:
```
*User can log in\n*Password is validated\n*Error messages are displayed
```

This will appear in Jira as:
```
- User can log in
- Password is validated
- Error messages are displayed
```

## Running the Script

Execute the script by running:
```
python bulk_ops.py
```

## What the Script Does

1. Reads the CSV file line by line
2. For each row:
   - If no `Issue ID` is provided, creates a new user story in Jira
   - If an `Issue ID` is provided, updates the existing story
3. Updates the CSV file with new issue IDs for created stories
4. Outputs progress and results to the console

## Troubleshooting

- If you see "Error: JIRA_API_KEY not found in environment variables" - Check your `.env` file
- If you see "CSV file not found" - Verify the path to your CSV file
- If a row is skipped - Check that all required fields are present

## Note

This script will modify your Jira issues directly. It's recommended to test it on a non-production environment first.
