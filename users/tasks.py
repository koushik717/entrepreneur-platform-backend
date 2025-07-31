# my_entrepreneur_platform/users/tasks.py

from celery import shared_task
import time # For simulating a long operation
import logging # For logging messages

logger = logging.getLogger(__name__)

@shared_task(bind=True) # @shared_task makes it a Celery task, bind=True passes the task instance
def debug_add(self, x, y):
    """
    A simple Celery task that adds two numbers and prints to the worker log.
    Simulates a long-running operation.
    """
    logger.info(f"Task {self.request.id} received: Adding {x} + {y}")
    # Simulate a long operation (e.g., sending an email, processing data)
    time.sleep(5) # Wait for 5 seconds

    result = x + y
    logger.info(f"Task {self.request.id} completed: Result = {result}")
    return result

@shared_task(bind=True)
def send_welcome_email(self, user_email):
    """
    Simulates sending a welcome email to a new user in the background.
    """
    logger.info(f"Task {self.request.id} received: Sending welcome email to {user_email}")
    time.sleep(10) # Simulate email sending time
    logger.info(f"Task {self.request.id} completed: Welcome email sent to {user_email}")
    return True