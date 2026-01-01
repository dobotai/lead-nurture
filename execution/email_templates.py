#!/usr/bin/env python3
"""
Email Templates for Lead Nurture Workflow
Manages and personalizes email templates for different stages.
"""

from datetime import datetime
from typing import Dict


class EmailTemplates:
    """Manages email templates for lead nurture campaigns."""

    @staticmethod
    def personalize(template: str, lead_data: Dict) -> str:
        """
        Personalize email template with lead data.

        Args:
            template: Email template string with {placeholders}
            lead_data: Dictionary with lead information

        Returns:
            Personalized email string
        """
        return template.format(**lead_data)

    @staticmethod
    def get_welcome_email(name: str, call_time: str, call_duration: int = 30) -> Dict[str, str]:
        """
        Welcome email sent immediately after booking.

        Args:
            name: Lead's first name
            call_time: Scheduled call time (formatted)
            call_duration: Duration in minutes

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = f"Your call is confirmed - {call_time}"

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Thanks for booking a call, {name}! 🎉</h2>

                    <p>We're excited to connect with you. Here are your call details:</p>

                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Date & Time:</strong> {call_time}</p>
                        <p style="margin: 5px 0;"><strong>Duration:</strong> {call_duration} minutes</p>
                    </div>

                    <h3 style="color: #2c3e50;">What to prepare:</h3>
                    <ul>
                        <li>Have any questions ready that you'd like to discuss</li>
                        <li>Be in a quiet space with a stable internet connection</li>
                        <li>Feel free to share your screen if needed</li>
                    </ul>

                    <p>We'll send you reminders as the call approaches, so you don't miss it.</p>

                    <p>Looking forward to speaking with you!</p>

                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        <strong>The Team</strong>
                    </p>

                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777;">
                        <p>Need to reschedule? Just reply to this email and we'll help you out.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        text = f"""
Thanks for booking a call, {name}!

We're excited to connect with you. Here are your call details:

Date & Time: {call_time}
Duration: {call_duration} minutes

What to prepare:
- Have any questions ready that you'd like to discuss
- Be in a quiet space with a stable internet connection
- Feel free to share your screen if needed

We'll send you reminders as the call approaches, so you don't miss it.

Looking forward to speaking with you!

Best regards,
The Team

---
Need to reschedule? Just reply to this email and we'll help you out.
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_midpoint_email(name: str, call_time: str) -> Dict[str, str]:
        """
        Mid-point follow-up email.

        Args:
            name: Lead's first name
            call_time: Scheduled call time (formatted)

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = f"Looking forward to our call on {call_time}"

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Hi {name},</h2>

                    <p>Just wanted to touch base before our upcoming call on <strong>{call_time}</strong>.</p>

                    <p>In the meantime, here are some resources you might find helpful:</p>

                    <ul>
                        <li><a href="#" style="color: #3498db;">Case Study: How we helped Company X</a></li>
                        <li><a href="#" style="color: #3498db;">Our approach to solving [problem]</a></li>
                        <li><a href="#" style="color: #3498db;">Frequently Asked Questions</a></li>
                    </ul>

                    <p>Feel free to review these at your leisure. We'll cover everything during our call, but these might give you some additional context.</p>

                    <p>See you soon!</p>

                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        <strong>The Team</strong>
                    </p>

                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777;">
                        <p>Have questions before the call? Just reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        text = f"""
Hi {name},

Just wanted to touch base before our upcoming call on {call_time}.

In the meantime, here are some resources you might find helpful:

- Case Study: How we helped Company X
- Our approach to solving [problem]
- Frequently Asked Questions

Feel free to review these at your leisure. We'll cover everything during our call, but these might give you some additional context.

See you soon!

Best regards,
The Team

---
Have questions before the call? Just reply to this email.
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_day_before_email(name: str, call_time: str, meeting_link: str = None) -> Dict[str, str]:
        """
        Day-before reminder email.

        Args:
            name: Lead's first name
            call_time: Scheduled call time (formatted)
            meeting_link: Optional Zoom/Meet link

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = f"Reminder: Our call tomorrow at {call_time}"

        meeting_section = ""
        if meeting_link:
            meeting_section = f"""
                <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Meeting Link:</strong><br>
                    <a href="{meeting_link}" style="color: #2e7d32; font-size: 16px;">{meeting_link}</a></p>
                </div>
            """

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Hi {name},</h2>

                    <p>This is a friendly reminder about our call scheduled for tomorrow:</p>

                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0; font-size: 18px;"><strong>{call_time}</strong></p>
                    </div>

                    {meeting_section}

                    <h3 style="color: #2c3e50;">Quick preparation checklist:</h3>
                    <ul>
                        <li>✓ Confirm you're still available (reply if you need to reschedule)</li>
                        <li>✓ Have your questions ready</li>
                        <li>✓ Test your audio/video setup</li>
                        <li>✓ Be in a quiet location</li>
                    </ul>

                    <p>We're looking forward to connecting with you!</p>

                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        <strong>The Team</strong>
                    </p>

                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777;">
                        <p>Need to reschedule? Reply to this email or contact us directly.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        text = f"""
Hi {name},

This is a friendly reminder about our call scheduled for tomorrow:

{call_time}

{"Meeting Link: " + meeting_link if meeting_link else ""}

Quick preparation checklist:
✓ Confirm you're still available (reply if you need to reschedule)
✓ Have your questions ready
✓ Test your audio/video setup
✓ Be in a quiet location

We're looking forward to connecting with you!

Best regards,
The Team

---
Need to reschedule? Reply to this email or contact us directly.
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_hour_before_email(name: str, call_time: str, meeting_link: str = None) -> Dict[str, str]:
        """
        One-hour-before reminder email.

        Args:
            name: Lead's first name
            call_time: Scheduled call time (formatted)
            meeting_link: Optional Zoom/Meet link

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = f"Starting in 1 hour: Our call at {call_time}"

        meeting_section = ""
        if meeting_link:
            meeting_section = f"""
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; font-size: 16px;"><strong>Join the call:</strong><br>
                    <a href="{meeting_link}" style="color: #f57c00; font-size: 18px; font-weight: bold;">{meeting_link}</a></p>
                </div>
            """

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Hi {name},</h2>

                    <p style="font-size: 18px;">Our call starts in <strong>1 hour</strong>!</p>

                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0; font-size: 20px;"><strong>{call_time}</strong></p>
                    </div>

                    {meeting_section}

                    <p>See you soon!</p>

                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        <strong>The Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """

        text = f"""
Hi {name},

Our call starts in 1 hour!

{call_time}

{"Join the call: " + meeting_link if meeting_link else ""}

See you soon!

Best regards,
The Team
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }


def main():
    """Test email templates."""
    templates = EmailTemplates()

    # Test data
    test_data = {
        'name': 'John',
        'call_time': 'Monday, Jan 15 at 2:00 PM EST',
        'call_duration': 30,
        'meeting_link': 'https://zoom.us/j/123456789'
    }

    print("=== Welcome Email ===")
    welcome = templates.get_welcome_email(
        test_data['name'],
        test_data['call_time'],
        test_data['call_duration']
    )
    print(f"Subject: {welcome['subject']}\n")
    print("HTML Preview:")
    print(welcome['html'][:200] + "...\n")

    print("\n=== Midpoint Email ===")
    midpoint = templates.get_midpoint_email(
        test_data['name'],
        test_data['call_time']
    )
    print(f"Subject: {midpoint['subject']}\n")

    print("\n=== Day Before Email ===")
    day_before = templates.get_day_before_email(
        test_data['name'],
        test_data['call_time'],
        test_data['meeting_link']
    )
    print(f"Subject: {day_before['subject']}\n")

    print("\n=== Hour Before Email ===")
    hour_before = templates.get_hour_before_email(
        test_data['name'],
        test_data['call_time'],
        test_data['meeting_link']
    )
    print(f"Subject: {hour_before['subject']}\n")


if __name__ == "__main__":
    main()
