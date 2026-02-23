"""
Social Media MCP (Model Context Protocol) Server for AI Employee

This MCP server enables Claude to interact with Facebook, Instagram, and Twitter
for posting messages and generating summaries.
"""

import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
import os
from urllib.parse import urlencode


class SocialMediaMCP:
    """Social Media MCP Server implementation."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(exist_ok=True)

        # Load social media credentials from environment or config
        self.facebook_access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.instagram_access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET')

    def post_to_facebook(self, message, image_url=None, link=None):
        """Post a message to Facebook Page."""
        if not self.facebook_access_token:
            return {"error": "Facebook access token not configured"}

        try:
            # Assuming we're posting to a Facebook Page
            # First, we'll need the Page ID (could be stored in config)
            page_id = os.getenv('FACEBOOK_PAGE_ID')

            if not page_id:
                return {"error": "Facebook Page ID not configured"}

            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"

            payload = {
                'message': message,
                'access_token': self.facebook_access_token
            }

            if link:
                payload['link'] = link

            response = requests.post(url, data=payload)
            result = response.json()

            if 'id' in result:
                post_id = result['id']
                self._save_log('facebook_post', 'success', {
                    'post_id': post_id,
                    'message': message[:100] + "..." if len(message) > 100 else message
                })
                return {"success": True, "post_id": post_id}
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                self._save_log('facebook_post', 'error', {'error': error_msg})
                return {"error": error_msg}

        except Exception as e:
            error_msg = str(e)
            self._save_log('facebook_post', 'error', {'exception': error_msg})
            return {"error": error_msg}

    def post_to_instagram(self, caption, image_url):
        """Post to Instagram (using Facebook Graph API)."""
        if not self.instagram_access_token:
            return {"error": "Instagram access token not configured"}

        try:
            # Get Instagram account ID (should be stored in config)
            instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')

            if not instagram_account_id:
                return {"error": "Instagram Account ID not configured"}

            # Step 1: Create the media object
            media_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"
            media_payload = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.instagram_access_token
            }

            media_response = requests.post(media_url, data=media_payload)
            media_result = media_response.json()

            if 'id' not in media_result:
                error_msg = media_result.get('error', {}).get('message', 'Failed to create media object')
                self._save_log('instagram_post', 'error', {'error': error_msg})
                return {"error": error_msg}

            creation_id = media_result['id']

            # Step 2: Publish the media
            publish_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"
            publish_payload = {
                'creation_id': creation_id,
                'access_token': self.instagram_access_token
            }

            publish_response = requests.post(publish_url, data=publish_payload)
            publish_result = publish_response.json()

            if 'id' in publish_result:
                post_id = publish_result['id']
                self._save_log('instagram_post', 'success', {
                    'post_id': post_id,
                    'caption': caption[:100] + "..." if len(caption) > 100 else caption
                })
                return {"success": True, "post_id": post_id}
            else:
                error_msg = publish_result.get('error', {}).get('message', 'Failed to publish media')
                self._save_log('instagram_post', 'error', {'error': error_msg})
                return {"error": error_msg}

        except Exception as e:
            error_msg = str(e)
            self._save_log('instagram_post', 'error', {'exception': error_msg})
            return {"error": error_msg}

    def post_to_twitter(self, tweet_text, media_urls=None):
        """Post a tweet to Twitter/X."""
        if not self.twitter_bearer_token:
            return {"error": "Twitter Bearer token not configured"}

        try:
            # Using Twitter API v2
            url = "https://api.twitter.com/2/tweets"

            headers = {
                "Authorization": f"Bearer {self.twitter_bearer_token}",
                "Content-Type": "application/json"
            }

            data = {
                "text": tweet_text
            }

            if media_urls:
                # Note: Uploading media to Twitter requires a separate step
                # This is a simplified implementation
                pass

            response = requests.post(url, headers=headers, json=data)
            result = response.json()

            if response.status_code in [200, 201]:
                tweet_id = result.get('data', {}).get('id')
                self._save_log('twitter_post', 'success', {
                    'tweet_id': tweet_id,
                    'text': tweet_text[:100] + "..." if len(tweet_text) > 100 else tweet_text
                })
                return {"success": True, "tweet_id": tweet_id}
            else:
                error_msg = result.get('detail', 'Unknown error')
                self._save_log('twitter_post', 'error', {'error': error_msg})
                return {"error": error_msg}

        except Exception as e:
            error_msg = str(e)
            self._save_log('twitter_post', 'error', {'exception': error_msg})
            return {"error": error_msg}

    def get_facebook_insights(self, page_id=None, metric='page_impressions', since_days=7):
        """Get insights for Facebook page."""
        if not self.facebook_access_token:
            return {"error": "Facebook access token not configured"}

        page_id = page_id or os.getenv('FACEBOOK_PAGE_ID')
        if not page_id:
            return {"error": "Facebook Page ID not configured"}

        try:
            since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
            until_date = datetime.now().strftime('%Y-%m-%d')

            url = f"https://graph.facebook.com/v18.0/{page_id}/insights"
            params = {
                'metric': metric,
                'since': since_date,
                'until': until_date,
                'access_token': self.facebook_access_token
            }

            response = requests.get(url, params=params)
            result = response.json()

            return result

        except Exception as e:
            return {"error": str(e)}

    def get_twitter_insights(self, since_days=7):
        """Get basic Twitter insights."""
        if not self.twitter_bearer_token:
            return {"error": "Twitter Bearer token not configured"}

        try:
            # Using Twitter API v2 for user metrics
            # Note: This is a simplified version - actual implementation would be more complex
            since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')

            url = f"https://api.twitter.com/2/users/by/username/{os.getenv('TWITTER_USERNAME')}"
            headers = {
                "Authorization": f"Bearer {self.twitter_bearer_token}"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "followers_count": user_data.get('data', {}).get('public_metrics', {}).get('followers_count'),
                    "following_count": user_data.get('data', {}).get('public_metrics', {}).get('following_count'),
                    "tweet_count": user_data.get('data', {}).get('public_metrics', {}).get('tweet_count')
                }
            else:
                return {"error": "Could not retrieve Twitter insights"}

        except Exception as e:
            return {"error": str(e)}

    def generate_social_summary(self, days=7):
        """Generate a summary of social media activity."""
        summary = {
            "summary_date": datetime.now().isoformat(),
            "days_back": days,
            "facebook": {},
            "instagram": {},
            "twitter": {},
            "recommendations": []
        }

        # Get Facebook insights
        fb_insights = self.get_facebook_insights(since_days=days)
        summary["facebook"] = fb_insights

        # Get Twitter insights
        tw_insights = self.get_twitter_insights(since_days=days)
        summary["twitter"] = tw_insights

        # For Instagram, we'd need to implement similar insight retrieval
        # For now, we'll add a placeholder
        summary["instagram"] = {"posts_last_period": "Data not available yet"}

        # Generate recommendations based on data
        if 'error' not in summary['facebook']:
            # Add Facebook-specific recommendations
            summary['recommendations'].append("Review Facebook engagement metrics")
        if 'error' not in summary['twitter']:
            # Add Twitter-specific recommendations
            summary['recommendations'].append("Engage with followers on Twitter")

        return summary

    def _save_log(self, action, result, details=None):
        """Save action log to file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "details": details or {}
        }

        log_file = self.logs_dir / f"social_media_mcp_log_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
                if isinstance(logs, dict):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)

        # Write logs back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)


def main():
    """Main function to demonstrate the Social Media MCP."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python social_media_mcp.py <vault_path> [--test]")
        print("Example: python social_media_mcp.py ./AI_Employee_Vault --test")
        print("\nEnvironment variables needed:")
        print("  FACEBOOK_ACCESS_TOKEN=your_fb_token")
        print("  FACEBOOK_PAGE_ID=your_page_id")
        print("  INSTAGRAM_ACCESS_TOKEN=your_ig_token")
        print("  INSTAGRAM_ACCOUNT_ID=your_ig_account_id")
        print("  TWITTER_BEARER_TOKEN=your_twitter_bearer")
        print("  TWITTER_ACCESS_TOKEN=your_twitter_token")
        print("  TWITTER_ACCESS_SECRET=your_twitter_secret")
        print("  TWITTER_USERNAME=your_twitter_username")
        return

    vault_path = sys.argv[1]
    social_mcp = SocialMediaMCP(vault_path)

    if "--test" in sys.argv:
        print("Testing Social Media MCP Server...")

        # Test generating summary
        summary = social_mcp.generate_social_summary(days=7)
        print(f"Generated social media summary: {len(summary.get('recommendations', []))} recommendations")

        print("Social Media MCP test completed.")
    else:
        print("Social Media MCP Server initialized.")
        print("Ready to process social media requests from Claude.")


if __name__ == "__main__":
    main()