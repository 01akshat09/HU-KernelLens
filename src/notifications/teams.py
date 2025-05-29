import aiohttp
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

TEAMS_WEBHOOK_URL= "https://deloitte.webhook.office.com/webhookb2/d8b0550a-d43c-4000-8ce2-93d2010adf6c@36da45f1-dd2c-4d1f-af13-5abe46b99921/IncomingWebhook/60af043c1b75420d8eb493a4c39ea838/08fed489-9e16-4170-929b-19df7e99159d/V2ulfuB6BTY3A2RIQgY7RD9WNd02SXZkecz8uLWH6neRE1"

async def send_teams_alert(alarm_data, alarm_type):
    """Send a Teams alert using webhook."""
    try:
        message = ""
        if alarm_type == "CPU":
            message = "High CPU utilization has been detected for the following process(es)."
        elif alarm_type == "User Activity":
            message = "Suspicious user activity detected."
        elif alarm_type == "Privileged Process":
            message = "Privileged process activity detected."
        else:
            message = "Alert from monitoring system."

        # Format facts based on alarm type
        facts = []
        for item in alarm_data:
            if alarm_type == "CPU":
                facts.extend([
                    {"name": "PID", "value": str(item.get("pid", "N/A"))},
                    {"name": "Command", "value": str(item.get("comm", "N/A"))},
                    {"name": "CPU Usage", "value": f"{item.get('cpu', 0)} ms"},
                    {"name": "Threshold", "value": f"{item.get('threshold', 0)} ms"}
                ])
            elif alarm_type == "User Activity":
                facts.extend([
                    {"name": "PID", "value": str(item.get("pid", "N/A"))},
                    {"name": "Command", "value": str(item.get("comm", "N/A"))},
                    {"name": "User ID", "value": str(item.get("uid", "N/A"))},
                    {"name": "Arguments", "value": str(item.get("args", "N/A"))},
                    {"name": "Timestamp", "value": str(item.get("timestamp", "N/A"))}
                ])
            elif alarm_type == "Privileged Process":
                facts.extend([
                    {"name": "PID", "value": str(item.get("pid", "N/A"))},
                    {"name": "Command", "value": str(item.get("comm", "N/A"))},
                    {"name": "User ID", "value": str(item.get("uid", "N/A"))},
                    {"name": "Arguments", "value": str(item.get("args", "N/A"))},
                    {"name": "Syscall", "value": str(item.get("syscall", "N/A"))},
                    {"name": "Filename", "value": str(item.get("filename", "N/A"))},
                    {"name": "Privilege Level", "value": str(item.get("privilege", "N/A"))},
                    {"name": "Insight", "value": str(item.get("insight", "N/A"))},
                    {"name": "Timestamp", "value": str(item.get("time", "N/A"))}
                ])

        teams_message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "size": "Large",
                                "weight": "Bolder",
                                "text": f"🚨 {alarm_type} Alert",
                                "color": "attention",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": message,
                                "wrap": True,
                                "spacing": "medium"
                            }
                        ] + [
                            {
                                "type": "Container",
                                "style": "emphasis",
                                "spacing": "medium",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": "Alert Details:",
                                        "weight": "bolder",
                                        "size": "medium"
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": (
                                            f"**Process ID (PID):** {item.get('pid', 'N/A')}\n\n" +
                                            f"**Process Name:** {item.get('comm', 'N/A')}\n\n" +
                                            f"**User ID:** {item.get('uid', 'N/A')}\n\n" +
                                            (f"**Command Arguments:** {item.get('args', 'N/A')}\n\n" if alarm_type in ["User Activity", "Privileged Process"] else "") +
                                            (f"**Syscall:** {item.get('syscall', 'N/A')}\n\n" +
                                             f"**Filename:** {item.get('filename', 'N/A')}\n\n" +
                                             f"**Insight:** {item.get('insight', 'N/A')}\n\n" if alarm_type == "Privileged Process" else "") +
                                            (f"**CPU Usage:** {item.get('cpu', 'N/A')} ms\n\n" +
                                             f"**Threshold:** {item.get('threshold', 'N/A')} ms\n\n" if alarm_type == "CPU" else "") +
                                            (f"**Timestamp:** {item.get('time', 'N/A')}" if alarm_type == "Privileged Process" else 
                                             f"**Timestamp:** {item.get('timestamp', 'N/A')}")
                                        ),
                                        "wrap": True,
                                        "color": "attention" if alarm_type == "Privileged Process" else "default"
                                    }
                                ]
                            } for item in alarm_data
                        ]
                    }
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(TEAMS_WEBHOOK_URL, json=teams_message) as response:
                if response.status != 200:
                    logger.error(f"Failed to send Teams notification: {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response: {response_text}")
                else:
                    logger.info("Successfully sent Teams notification")

    except Exception as e:
        logger.error(f"Failed to send Teams notification: {e}")
        raise
