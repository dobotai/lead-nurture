#!/usr/bin/env python3
"""
Close.io CRM API Client
Handles all interactions with Close.io API for lead management and call tracking.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time

load_dotenv()

class CloseIOClient:
    """Client for interacting with Close.io API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Close.io client.

        Args:
            api_key: Close.io API key (if not provided, loads from env)
        """
        self.api_key = api_key or os.getenv('CLOSE_IO_API_KEY')
        if not self.api_key:
            raise ValueError("Close.io API key not found in environment variables")

        self.base_url = "https://api.close.com/api/v1"
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

        # Rate limiting
        self.requests_per_minute = 600
        self.request_times = []

    def _rate_limit(self):
        """Implement rate limiting to stay within API limits."""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.requests_per_minute:
            # Wait until oldest request is 60 seconds old
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_times = []

        self.request_times.append(now)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make API request with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON as dict

        Raises:
            Exception: If request fails
        """
        self._rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)

        if response.status_code >= 400:
            raise Exception(f"Close.io API error: {response.status_code} - {response.text}")

        return response.json()

    def get_leads_with_upcoming_calls(self, days_ahead: int = 30) -> List[Dict]:
        """
        Get all leads that have calls scheduled in the next X days.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of lead dictionaries with call information
        """
        # Get all leads
        leads = []
        has_more = True
        skip = 0

        while has_more:
            response = self._make_request(
                'GET',
                '/lead/',
                params={
                    '_skip': skip,
                    '_limit': 100
                }
            )

            leads.extend(response.get('data', []))
            has_more = response.get('has_more', False)
            skip += 100

        # For each lead, check if they have upcoming calls
        leads_with_calls = []
        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)

        for lead in leads:
            lead_id = lead['id']

            # Get activities for this lead
            activities = self._make_request(
                'GET',
                '/activity/',
                params={
                    'lead_id': lead_id,
                    '_type': 'Meeting'  # Close.io uses Meeting for scheduled calls
                }
            )

            for activity in activities.get('data', []):
                # Check if this is an upcoming call
                if activity.get('date_scheduled'):
                    scheduled_date = datetime.fromisoformat(
                        activity['date_scheduled'].replace('Z', '+00:00')
                    )

                    if now <= scheduled_date <= future_date:
                        lead['call_info'] = {
                            'activity_id': activity['id'],
                            'scheduled_time': activity['date_scheduled'],
                            'duration': activity.get('duration'),
                            'title': activity.get('title', 'Call'),
                            'status': activity.get('status', 'scheduled')
                        }
                        leads_with_calls.append(lead)
                        break  # Only track the next upcoming call

        return leads_with_calls

    def get_lead(self, lead_id: str) -> Dict:
        """
        Get detailed information about a specific lead.

        Args:
            lead_id: Close.io lead ID

        Returns:
            Lead data dictionary
        """
        return self._make_request('GET', f'/lead/{lead_id}/')

    def add_note_to_lead(self, lead_id: str, note: str) -> Dict:
        """
        Add a note to a lead (used to track email activity).

        Args:
            lead_id: Close.io lead ID
            note: Note text to add

        Returns:
            Created note data
        """
        return self._make_request(
            'POST',
            '/activity/note/',
            json={
                'lead_id': lead_id,
                'note': note
            }
        )

    def get_call_status(self, activity_id: str) -> str:
        """
        Get the current status of a scheduled call.

        Args:
            activity_id: Close.io activity ID

        Returns:
            Status string ('scheduled', 'completed', 'cancelled', etc.)
        """
        activity = self._make_request('GET', f'/activity/{activity_id}/')
        return activity.get('status', 'unknown')

    def get_lead_email(self, lead: Dict) -> Optional[str]:
        """
        Extract primary email from lead data.

        Args:
            lead: Lead dictionary from Close.io

        Returns:
            Email address or None if not found
        """
        # Check contacts for email
        contacts = lead.get('contacts', [])
        for contact in contacts:
            emails = contact.get('emails', [])
            if emails:
                return emails[0].get('email')

        return None

    def get_lead_name(self, lead: Dict) -> str:
        """
        Extract lead/contact name from lead data.

        Args:
            lead: Lead dictionary from Close.io

        Returns:
            Contact name or "there" as fallback
        """
        contacts = lead.get('contacts', [])
        if contacts:
            name = contacts[0].get('name', '')
            if name:
                return name.split()[0]  # First name only

        # Fallback to company name or generic
        return lead.get('display_name', 'there')


def main():
    """Test the Close.io client."""
    try:
        client = CloseIOClient()
        print("Close.io client initialized successfully")

        # Test: Get leads with upcoming calls
        print("\nFetching leads with upcoming calls...")
        leads = client.get_leads_with_upcoming_calls(days_ahead=30)

        print(f"\nFound {len(leads)} leads with upcoming calls:")
        for lead in leads[:5]:  # Show first 5
            email = client.get_lead_email(lead)
            name = client.get_lead_name(lead)
            call_time = lead['call_info']['scheduled_time']
            print(f"  - {name} ({email}) - Call at {call_time}")

        if leads:
            # Test: Add note to first lead
            first_lead = leads[0]
            print(f"\nAdding test note to lead: {client.get_lead_name(first_lead)}")
            client.add_note_to_lead(
                first_lead['id'],
                "Test note from lead nurture workflow"
            )
            print("Note added successfully")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
