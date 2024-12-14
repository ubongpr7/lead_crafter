from google.oauth2 import service_account
from googleapiclient.discovery import build

# Replace with your service account file
SERVICE_ACCOUNT_FILE = 'your-service-account.json'

SCOPES = ['https://www.googleapis.com/auth/forms.body']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('forms', 'v1', credentials=credentials)

# Create the form
form_body = {
    "info": {
        "title": "Tech & Programming Survey",
        "description": "Help us guide you in choosing the right tech niche and programming career path!"
    }
}
form = service.forms().create(body=form_body).execute()
form_id = form.get('formId')

# Add questions to the form
update_body = {
    "requests": [
        {
            "createItem": {
                "item": {
                    "title": "Full Name",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {}
                        }
                    }
                },
                "location": {"index": 0}
            }
        },
        {
            "createItem": {
                "item": {
                    "title": "Email Address",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {}
                        }
                    }
                },
                "location": {"index": 1}
            }
        },
        {
            "createItem": {
                "item": {
                    "title": "Age Group",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [
                                    {"value": "Under 18"},
                                    {"value": "18–24"},
                                    {"value": "25–34"},
                                    {"value": "35 and above"}
                                ]
                            }
                        }
                    }
                },
                "location": {"index": 2}
            }
        },
        {
            "createItem": {
                "item": {
                    "title": "Why are you interested in learning programming?",
                    "questionItem": {
                        "question": {
                            "required": False,
                            "textQuestion": {}
                        }
                    }
                },
                "location": {"index": 3}
            }
        },
        {
            "createItem": {
                "item": {
                    "title": "Which of these Python career tracks excites you the most?",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "CHECKBOX",
                                "options": [
                                    {"value": "Web Development"},
                                    {"value": "Data Science"},
                                    {"value": "Artificial Intelligence/Machine Learning"},
                                    {"value": "Game Development"},
                                    {"value": "Automation/Scripting"},
                                    {"value": "Cybersecurity"}
                                ]
                            }
                        }
                    }
                },
                "location": {"index": 4}
            }
        }
    ]
}

# Batch update the form
service.forms().batchUpdate(formId=form_id, body=update_body).execute()

print(f"Form created successfully! Form ID: {form_id}")
