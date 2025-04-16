import time
import json
import os
from datetime import datetime, timedelta
import tiktoken

# File to store token usage data
TOKEN_USAGE_FILE = "token_usage.json"

# Default token limits
DEFAULT_DAILY_LIMIT = 100000  # 100k tokens per day
DEFAULT_REQUEST_LIMIT = 10000  # 10k tokens per request

class TokenCounter:
    def __init__(self, daily_limit=None, request_limit=None):
        self.daily_limit = daily_limit or DEFAULT_DAILY_LIMIT
        self.request_limit = request_limit or DEFAULT_REQUEST_LIMIT
        self.usage_data = self._load_usage_data()
        self._check_reset_daily()
    
    def _load_usage_data(self):
        """Load token usage data from file or create new"""
        if os.path.exists(TOKEN_USAGE_FILE):
            try:
                with open(TOKEN_USAGE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default structure if file doesn't exist or is invalid
        return {
            "daily": {
                "count": 0,
                "reset_timestamp": time.time() + 86400  # 24 hours from now
            },
            "threads": {}  # Store per-thread usage
        }
    
    def _save_usage_data(self):
        """Save token usage data to file"""
        with open(TOKEN_USAGE_FILE, 'w') as f:
            json.dump(self.usage_data, f)
    
    def _check_reset_daily(self):
        """Check if daily counter needs to be reset"""
        if time.time() >= self.usage_data["daily"]["reset_timestamp"]:
            # Reset daily count and set new reset time (next midnight)
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            tomorrow_midnight = datetime(
                year=tomorrow.year, 
                month=tomorrow.month, 
                day=tomorrow.day, 
                hour=0, minute=0, second=0
            )
            
            self.usage_data["daily"]["count"] = 0
            self.usage_data["daily"]["reset_timestamp"] = tomorrow_midnight.timestamp()
            self._save_usage_data()
    
    def count_tokens(self, text):
        """Count tokens in text using tiktoken"""
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough approximation (4 chars ≈ 1 token)
            return len(text) // 4
    
    def track_tokens(self, thread_id, token_count):
        """Track token usage for a request"""
        # Update thread specific count
        if thread_id not in self.usage_data["threads"]:
            self.usage_data["threads"][thread_id] = 0
        self.usage_data["threads"][thread_id] += token_count
        
        # Update daily count
        self.usage_data["daily"]["count"] += token_count
        
        # Save updated data
        self._save_usage_data()
    
    def check_limits(self, thread_id, token_estimate):
        """Check if request would exceed limits"""
        # Always check for reset first
        self._check_reset_daily()
        
        # Check request limit
        if token_estimate > self.request_limit:
            return False, f"Request exceeds the maximum token limit of {self.request_limit}"
        
        # Check daily limit
        daily_count = self.usage_data["daily"]["count"]
        if daily_count + token_estimate > self.daily_limit:
            reset_time = datetime.fromtimestamp(self.usage_data["daily"]["reset_timestamp"])
            reset_in = reset_time - datetime.now()
            hours, remainder = divmod(reset_in.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return False, f"Daily token limit reached. Limit resets in {hours}h {minutes}m"
        
        return True, "Within limits"
    
    def get_usage_stats(self, thread_id=None):
        """Get usage statistics"""
        stats = {
            "daily_usage": self.usage_data["daily"]["count"],
            "daily_limit": self.daily_limit,
            "daily_remaining": max(0, self.daily_limit - self.usage_data["daily"]["count"]),
            "reset_timestamp": self.usage_data["daily"]["reset_timestamp"]
        }
        
        if thread_id and thread_id in self.usage_data["threads"]:
            stats["thread_usage"] = self.usage_data["threads"][thread_id]
        
        return stats