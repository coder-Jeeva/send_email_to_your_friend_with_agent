import os
import json
import azure.functions as func
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load credentials from environment variables
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("GMAIL_PASSWORD")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="BirthdayEmailTriggerGmail")
@app.route(route="send-birthday", methods=["POST"])
def send_birthday(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get JSON from POST request
        data = req.get_json()
        friend_name = data.get("name", "Friend")
        friend_email = data.get("email")
        custom_message = data.get("message", f"Happy Birthday, {friend_name}! 🎉")

        if not friend_email:
            return func.HttpResponse(
                json.dumps({"status": "error", "message": "'email' is required"}),
                status_code=400,
                mimetype="application/json"
            )

        # Create email
        message = MIMEMultipart()
        message["From"] = sender_email 
        message["To"] = friend_email
        message["Subject"] = f"Birthday Wishes for {friend_name}"
        message.attach(MIMEText(custom_message, "plain"))

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, friend_email, message.as_string())

        # Return success as JSON
        return func.HttpResponse(
            json.dumps({"status": "success", "message": f"Birthday email sent to {friend_name}!"}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )