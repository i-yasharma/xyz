# Automated AI Engineering LinkedIn Poster

This project automates posting to LinkedIn and sending an email notification, daily at 10 PM IST. It generates humanized LinkedIn posts on AI engineering topics, pretending to be "Yash Sharma", a B.Tech CSE student specializing in AI.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   You need to set the following environment variables (or configure them as repository secrets for GitHub Actions):
   - `OPENAI_API_KEY`: Your OpenAI API Key for generating content.
   - `LINKEDIN_ACCESS_TOKEN`: The OAuth2 access token for the LinkedIn API.
   - `LINKEDIN_PERSON_URN`: Your LinkedIn profile URN (e.g., `urn:li:person:YOUR_ID`).
   - `EMAIL_SENDER`: The email address from which notifications will be sent (e.g., your Gmail).
   - `EMAIL_PASSWORD`: The app password or password for the sender email account.
   - `EMAIL_RECEIVER`: The email address to receive the daily notifications.

3. **Running locally**:
   ```bash
   python main.py
   ```

## Automated Deployment

This project includes a GitHub Actions workflow that runs automatically every day at 16:30 UTC (10:00 PM IST).
Make sure to configure the repository secrets in your GitHub repository matching the Environment Variables listed above.
