from asyncio import to_thread
from datetime import datetime, timedelta
from multiprocessing.util import get_logger
from os import getenv
from typing import Literal
from dotenv import load_dotenv
from asyncio import sleep

import resend
from result import Result, Ok, Err

from database.repository.participants_repository import ParticipantsRepository
from server.exception import ParticipantNotFoundError, EmailRateLimitExceededError
from src.service.mail_service.mail_service import MailService
from src.service.mail_service.utils import (
    load_email_participant_html_template,
    load_email_verify_participant_html_template,
)

SENDER_EMAIL = "onboarding@resend.dev"
# SENDER_EMAIL = "thehubaubg.noreply@gmail.com" # We obviously need to supply our own email here.

LOG = get_logger()
load_dotenv()

MAX_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 1  # seconds
RATE_LIMIT_SECONDS = 60


class ResendMailService(MailService):
    """Service layer responsible for the resend MailService implementation"""

    def __init__(self, participant_repository: ParticipantsRepository) -> None:
        api_key = getenv("RESEND_API_KEY")
        if not api_key:
            LOG.exception("RESEND_API_KEY environment variable is not set")
            raise ValueError("RESEND_API_KEY environment variable is not set")
        resend.api_key = api_key
        self.client = resend
        self.participant_repository = participant_repository

    async def send_email(
        self, receiver: str, subject: str, body_content: str, content_type: Literal["text", "html"] = "text"
    ) -> Result[resend.Email, ParticipantNotFoundError | EmailRateLimitExceededError | str]:
        # Check if participant exists
        result = await self.participant_repository.fetch_by_email(receiver)
        if result.is_err():
            LOG.error(f"Participant with email {receiver} not found.")
            return Err(ParticipantNotFoundError())

        participant = result.ok_value
        # Check rate limit
        if participant.last_sent_email:
            if datetime.now() - participant.last_sent_email < timedelta(seconds=RATE_LIMIT_SECONDS):
                LOG.error(f"Rate limit exceeded for participant {participant.id} with email {participant.email}.")
                return Err(EmailRateLimitExceededError())

        # Prepare the email parameters
        params: resend.Emails.SendParams = {
            "from": f"THE HUB <{SENDER_EMAIL}>",
            "to": [participant.email],
            "subject": subject,
            content_type: body_content,
        }

        # Retry logic
        retry_delay = INITIAL_RETRY_DELAY_SECONDS
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Send the email asynchronously
                email: resend.Email = await to_thread(self.client.Emails.send, params)
                LOG.info(f"Email sent successfully: {email}")

                # Update participant's last sent email timestamp
                participant.last_sent_email = datetime.now()
                await self.participant_repository.update(obj_id=participant.id, updated_data=participant)

                return Ok(email)
            except Exception:
                LOG.warning(f"Attempt {attempt} failed. Retrying in {retry_delay} seconds...")
                await sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        LOG.error(f"Failed to send email after {MAX_RETRIES} attempts.")
        return Err(f"Failed to send email after {MAX_RETRIES} attempts.")

    async def send_participant_successful_registration_email(
        self,
        receiver: str,
        subject: str,
        participant: str,
        team_name: str,
        invite_link: str,
    ) -> Result[resend.Email, ParticipantNotFoundError | EmailRateLimitExceededError | str]:
        try:
            body_html = load_email_participant_html_template(participant, team_name, invite_link)
        except ValueError as e:
            LOG.exception(f"Error loading the HTML template: {str(e)}")
            return Err(f"Error loading the HTML template: {str(e)}")

        send_result = await self.send_email(
            receiver=receiver, subject=subject, body_content=body_html, content_type="html"
        )
        return send_result

    async def send_participant_verification_email(
        self,
        receiver: str,
        subject: str,
        participant: str,
        team_name: str,
        confirmation_link: str,
    ) -> Result[resend.Email, ParticipantNotFoundError | EmailRateLimitExceededError | str]:
        try:
            body_html = load_email_verify_participant_html_template(participant, team_name, confirmation_link)
        except ValueError as e:
            LOG.exception(f"Failed to load email template: {str(e)}")
            return Err(f"Failed to load email template: {str(e)}")

        send_result = await self.send_email(
            receiver=receiver, subject=subject, body_content=body_html, content_type="html"
        )
        return send_result
