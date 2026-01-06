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
    def get_email_1(name: str) -> Dict[str, str]:
        """
        Email 1: Sent immediately after booking - Setting expectations.

        Args:
            name: Lead's first name

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = "[Important] Your Ops Audit Call is Confirmed"

        text = f"""Hey! Doby here.

You booked time because something in your business isn't clicking the way it should.

Not broken enough to panic.
Not smooth enough to ignore.

Before we talk, I want to set expectations so this doesn't feel like another "agency call."

I'm not here to sell you software.
I'm not here to pitch AI buzzwords.
And I'm definitely not here to duct-tape Zapier automations together.

Over the next few days, I'll send a couple short notes explaining:

• how we actually approach automation
• who this works well for
• and where it absolutely doesn't

If anything you read sparks a question — reply directly.
That context makes the call far more useful.

Talk soon,
Doby"""

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <p>Hey! Doby here.</p>

                    <p>You booked time because something in your business isn't clicking the way it should.</p>

                    <p>Not broken enough to panic.<br>
                    Not smooth enough to ignore.</p>

                    <p>Before we talk, I want to set expectations so this doesn't feel like another "agency call."</p>

                    <p>I'm not here to sell you software.<br>
                    I'm not here to pitch AI buzzwords.<br>
                    And I'm definitely not here to duct-tape Zapier automations together.</p>

                    <p>Over the next few days, I'll send a couple short notes explaining:</p>

                    <ul>
                        <li>how we actually approach automation</li>
                        <li>who this works well for</li>
                        <li>and where it absolutely doesn't</li>
                    </ul>

                    <p>If anything you read sparks a question — reply directly.<br>
                    That context makes the call far more useful.</p>

                    <p style="margin-top: 30px;">Talk soon,<br>
                    Doby</p>
                </div>
            </body>
        </html>
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_email_2(name: str) -> Dict[str, str]:
        """
        Email 2: Sent 6 hours after booking - Will automation actually help?

        Args:
            name: Lead's first name

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = "Will automation actually improve your operations?"

        text = """A reasonable thought you might be having:

"This sounds interesting… but would this actually move the needle?"

That skepticism is healthy.

Most automation fails because it's built after the business is already messy — or worse, without understanding how decisions are actually made.

Our starting point isn't tools.
It's behavior.

We look at:

• where humans are making repetitive decisions
• where information gets lost or delayed
• where the business slows down as volume increases

Only then do we design systems around it.

Even if we never build a single automation together, founders usually leave the first phase with a much clearer understanding of:

• what's causing friction
• what's draining their time
• and what not to fix yet

That clarity alone is often the unlock.

More context coming next.

— Doby"""

        html = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <p>A reasonable thought you might be having:</p>

                    <p><em>"This sounds interesting… but would this actually move the needle?"</em></p>

                    <p>That skepticism is healthy.</p>

                    <p>Most automation fails because it's built after the business is already messy — or worse, without understanding how decisions are actually made.</p>

                    <p>Our starting point isn't tools.<br>
                    It's behavior.</p>

                    <p>We look at:</p>

                    <ul>
                        <li>where humans are making repetitive decisions</li>
                        <li>where information gets lost or delayed</li>
                        <li>where the business slows down as volume increases</li>
                    </ul>

                    <p>Only then do we design systems around it.</p>

                    <p>Even if we never build a single automation together, founders usually leave the first phase with a much clearer understanding of:</p>

                    <ul>
                        <li>what's causing friction</li>
                        <li>what's draining their time</li>
                        <li>and what not to fix yet</li>
                    </ul>

                    <p>That clarity alone is often the unlock.</p>

                    <p>More context coming next.</p>

                    <p style="margin-top: 30px;">— Doby</p>
                </div>
            </body>
        </html>
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_email_3(name: str) -> Dict[str, str]:
        """
        Email 3: Sent 12 hours after booking - Who DobotAI is built for.

        Args:
            name: Lead's first name

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = "Who DobotAI is built for (and who it isn't)"

        text = """People always ask what industries we work with.

The truth?
Industry matters less than operational maturity.

This works best if:

• leads are already coming in
• delivery is proven
• and the business is starting to feel heavier as it grows

It works especially well when:

• the founder is still too involved
• the CRM doesn't reflect reality
• follow-ups rely on memory
• or your team keeps asking for "one more person"

This does not work if:

• you're still figuring out product-market fit
• you want quick hacks
• or you're allergic to structure

We build systems meant to last — not automations you babysit.

If you're nodding along, the call will make sense.

— Doby"""

        html = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <p>People always ask what industries we work with.</p>

                    <p>The truth?<br>
                    Industry matters less than operational maturity.</p>

                    <p><strong>This works best if:</strong></p>

                    <ul>
                        <li>leads are already coming in</li>
                        <li>delivery is proven</li>
                        <li>and the business is starting to feel heavier as it grows</li>
                    </ul>

                    <p><strong>It works especially well when:</strong></p>

                    <ul>
                        <li>the founder is still too involved</li>
                        <li>the CRM doesn't reflect reality</li>
                        <li>follow-ups rely on memory</li>
                        <li>or your team keeps asking for "one more person"</li>
                    </ul>

                    <p><strong>This does not work if:</strong></p>

                    <ul>
                        <li>you're still figuring out product-market fit</li>
                        <li>you want quick hacks</li>
                        <li>or you're allergic to structure</li>
                    </ul>

                    <p>We build systems meant to last — not automations you babysit.</p>

                    <p>If you're nodding along, the call will make sense.</p>

                    <p style="margin-top: 30px;">— Doby</p>
                </div>
            </body>
        </html>
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_email_4(name: str) -> Dict[str, str]:
        """
        Email 4: Sent 18 hours after booking - Why systems don't break.

        Args:
            name: Lead's first name

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = "Why our automation systems don't break as you scale"

        text = """Most automations follow rules.

Rules work… until reality changes.

We design systems that account for:

• missing information
• edge cases
• delays
• human inconsistency

Instead of rigid triggers, we build logic that:

• evaluates context
• chooses actions
• and escalates when needed

That's why our systems don't fall apart when:

• volume increases
• team members change
• or processes evolve

I'll show you real examples of this on the call — not slides, not theory.

Just how it actually works.

— Doby"""

        html = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <p>Most automations follow rules.</p>

                    <p>Rules work… until reality changes.</p>

                    <p>We design systems that account for:</p>

                    <ul>
                        <li>missing information</li>
                        <li>edge cases</li>
                        <li>delays</li>
                        <li>human inconsistency</li>
                    </ul>

                    <p>Instead of rigid triggers, we build logic that:</p>

                    <ul>
                        <li>evaluates context</li>
                        <li>chooses actions</li>
                        <li>and escalates when needed</li>
                    </ul>

                    <p>That's why our systems don't fall apart when:</p>

                    <ul>
                        <li>volume increases</li>
                        <li>team members change</li>
                        <li>or processes evolve</li>
                    </ul>

                    <p>I'll show you real examples of this on the call — not slides, not theory.</p>

                    <p>Just how it actually works.</p>

                    <p style="margin-top: 30px;">— Doby</p>
                </div>
            </body>
        </html>
        """

        return {
            'subject': subject,
            'html': html.strip(),
            'text': text.strip()
        }

    @staticmethod
    def get_email_5(name: str) -> Dict[str, str]:
        """
        Email 5: Sent 24 hours after booking - What we'll cover on the call.

        Args:
            name: Lead's first name

        Returns:
            Dictionary with 'subject', 'html', 'text'
        """
        subject = "What we'll cover on our DobotAI call"

        text = """Here's how I think about our call:

It's not a pitch.
It's a working session.

We'll:

• walk through how things operate today
• identify where decisions pile up
• and see whether automation creates real leverage

If there's a fit, I'll outline a path forward.
If there isn't, you'll still leave with clarity on what's holding things back.

No pressure either way.

Come ready to talk honestly about what feels heavier than it should.

Looking forward to it,
Doby"""

        html = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <p>Here's how I think about our call:</p>

                    <p>It's not a pitch.<br>
                    It's a working session.</p>

                    <p><strong>We'll:</strong></p>

                    <ul>
                        <li>walk through how things operate today</li>
                        <li>identify where decisions pile up</li>
                        <li>and see whether automation creates real leverage</li>
                    </ul>

                    <p>If there's a fit, I'll outline a path forward.<br>
                    If there isn't, you'll still leave with clarity on what's holding things back.</p>

                    <p>No pressure either way.</p>

                    <p>Come ready to talk honestly about what feels heavier than it should.</p>

                    <p style="margin-top: 30px;">Looking forward to it,<br>
                    Doby</p>
                </div>
            </body>
        </html>
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
    test_name = 'John'

    print("=== Email 1: Call Confirmed ===")
    email_1 = templates.get_email_1(test_name)
    print(f"Subject: {email_1['subject']}\n")
    print(f"Text preview:\n{email_1['text'][:200]}...\n")

    print("\n=== Email 2: Will Automation Help? ===")
    email_2 = templates.get_email_2(test_name)
    print(f"Subject: {email_2['subject']}\n")

    print("\n=== Email 3: Who It's For ===")
    email_3 = templates.get_email_3(test_name)
    print(f"Subject: {email_3['subject']}\n")

    print("\n=== Email 4: Why Systems Don't Break ===")
    email_4 = templates.get_email_4(test_name)
    print(f"Subject: {email_4['subject']}\n")

    print("\n=== Email 5: What We'll Cover ===")
    email_5 = templates.get_email_5(test_name)
    print(f"Subject: {email_5['subject']}\n")


if __name__ == "__main__":
    main()
