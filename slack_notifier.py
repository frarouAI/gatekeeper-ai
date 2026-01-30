"""
Slack Notifier — Owner-Aware Notifications

Sends targeted Slack notifications based on file ownership.
"""

import os
import json
import requests
from typing import Dict, List, Optional


def get_slack_webhook() -> Optional[str]:
    """Get Slack webhook URL from environment or config."""
    
    # Try environment variable first
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if webhook:
        return webhook
    
    # Try config file
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path(".gatekeeper.yml")
        if config_path.exists():
            config = yaml.safe_load(config_path.read_text())
            return config.get("slack", {}).get("webhook_url")
    except:
        pass
    
    return None


def format_slack_message(notification: Dict) -> Dict:
    """Format notification as Slack message."""
    
    notification_type = notification["type"]
    
    if notification_type == "team_escalation":
        # Critical team notification
        files_list = "\n".join(f"• `{f}`" for f in notification["files"][:5])
        if len(notification["files"]) > 5:
            files_list += f"\n• ...and {len(notification['files']) - 5} more"
        
        return {
            "text": f"🚨 *Gatekeeper Alert: Unowned Files Failing*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Unowned Files Failing"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": notification["message"]
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Files:*\n{files_list}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Action required: Assign owners in CODEOWNERS"
                        }
                    ]
                }
            ]
        }
    
    elif notification_type == "owner_notification":
        # Owner-specific notification
        owner = notification["owner"]
        files_list = "\n".join(f"• `{f}`" for f in notification["files"][:3])
        if len(notification["files"]) > 3:
            files_list += f"\n• ...and {len(notification['files']) - 3} more"
        
        return {
            "text": f"📋 Quality issues in your files",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Hey {owner}!* {notification['message']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Your files:*\n{files_list}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Run `gatekeeper repair <file> --dry-run` locally"
                        }
                    ]
                }
            ]
        }
    
    return {"text": notification["message"]}


def send_slack_notification(notification: Dict, webhook_url: Optional[str] = None) -> bool:
    """Send notification to Slack."""
    
    if webhook_url is None:
        webhook_url = get_slack_webhook()
    
    if not webhook_url:
        print("⚠️  SLACK_WEBHOOK_URL not configured - skipping notification")
        return False
    
    message = format_slack_message(notification)
    
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Slack notification sent: {notification['type']}")
            return True
        else:
            print(f"⚠️  Slack notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Slack notification error: {e}")
        return False


def send_all_notifications(notifications: List[Dict]) -> Dict:
    """Send all notifications and return summary."""
    
    webhook_url = get_slack_webhook()
    
    if not webhook_url:
        print("ℹ️  Slack notifications disabled (no webhook configured)")
        return {
            "sent": 0,
            "failed": 0,
            "skipped": len(notifications)
        }
    
    sent = 0
    failed = 0
    
    for notification in notifications:
        if send_slack_notification(notification, webhook_url):
            sent += 1
        else:
            failed += 1
    
    return {
        "sent": sent,
        "failed": failed,
        "skipped": 0
    }
