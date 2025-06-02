# TaskMaster - AI-Powered Task Management System

TaskMaster is a Django-based task management application that uses AI to prioritize tasks based on deadlines, user-set priorities, and task age.

## Features

- AI-powered task prioritization
- User authentication and registration
- Task creation, editing, and completion
- Email and SMS notifications (configurable per user)
- MongoDB integration using Djongo
- Responsive Bootstrap UI

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd taskmaster
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure MongoDB is installed and running on localhost:27017

4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone
```

## AI Prioritization Algorithm

The AI prioritization algorithm considers:

1. **Deadline proximity** - Tasks with closer deadlines get higher priority
2. **User-set priority** - High, medium, or low priority set by the user
3. **Task age** - Older tasks get slightly higher priority to prevent them from being forgotten

The algorithm calculates a score from 0-10, with 10 being the highest priority.

## Technologies Used

- Django 5.1.1
- MongoDB with Djongo
- Bootstrap 5
- Font Awesome
- Twilio API for SMS notifications

## License

This project is licensed under the MIT License - see the LICENSE file for details.
