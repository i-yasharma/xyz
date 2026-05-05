import os
import json
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Environment variables
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def generate_content():
    """Generates a topic and a LinkedIn post using a free AI API."""
    prompt = (
        "You are Yash Sharma, a B.Tech CSE student specializing in AI engineering. "
        "Every day you write a LinkedIn post about a new topic in the AI engineering domain. "
        "Generate today's topic and a humanized LinkedIn post. The post should not be a single huge paragraph; "
        "use line breaks and spaces to make it readable and authentic. Write it in the first person. "
        "Make it engaging, relatable for students and professionals, and informative.\n\n"
        "Return the result exactly as a valid JSON object with two keys: 'topic' (a short string) and 'post' (the formatted post text). "
        "Do not wrap the JSON in markdown code blocks."
    )

    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?json=true"

    try:
        response = requests.get(url)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            # If the response isn't already a JSON object, maybe the text field contains the JSON string
            import re
            content_str = response.text
            # Try to extract JSON from within markdown blocks if present
            json_match = re.search(r'```json\n(.*?)\n```', content_str, re.DOTALL)
            if json_match:
                content_str = json_match.group(1)
            data = json.loads(content_str)

        return data.get("topic", "AI Engineering Topic"), data.get("post", "Post content unavailable.")
    except Exception as e:
        print(f"Error generating content: {e}")
        return "Error Topic", f"Failed to generate post: {e}"


def post_to_linkedin(post_content):
    """Posts the generated content to LinkedIn."""
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        print("Missing LinkedIn credentials. Skipping LinkedIn post.")
        return False

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Successfully posted to LinkedIn!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error posting to LinkedIn: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
        return False


def send_email_notification(topic, post_content, linkedin_success):
    """Sends an email notification summarizing what was posted."""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        print("Missing Email credentials. Skipping email notification.")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"Automated LinkedIn Post: {topic}"

    status = "Success" if linkedin_success else "Failed (or skipped)"

    body = f"""
Hello Yash,

Here is your automated LinkedIn post update.

Topic: {topic}
LinkedIn Post Status: {status}

--- Post Content ---
{post_content}
--------------------

Best,
Your AI Assistant
"""
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Assuming Gmail SMTP. Adjust if using another provider.
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Successfully sent email notification!")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    print("Starting daily automated job...")
    topic, post_content = generate_content()

    print(f"Generated Topic: {topic}")
    print("Generated Post preview:", post_content[:100], "...")

    if topic == "Error Topic":
        print("Skipping LinkedIn post and sending failure notification due to content generation error.")
        send_email_notification(topic, post_content, False)
        return

    success = post_to_linkedin(post_content)

    send_email_notification(topic, post_content, success)
    print("Job complete.")

if __name__ == "__main__":
    main()
