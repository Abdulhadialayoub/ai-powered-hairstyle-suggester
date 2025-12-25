"""
Usage Tracker for Stable Image Ultra Service

Tracks API usage, costs, and statistics for monitoring and budget management.
Logs each API call with metadata to a JSON file for persistence.

Pricing: $0.08 per image
"""

import json
import os
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
from pathlib import Path


logger = logging.getLogger('usage_tracker')
logger.setLevel(logging.INFO)


class UsageTracker:
    """
    Track API usage for monitoring and cost management.
    
    Logs each API call with metadata including timestamp, user session,
    hairstyle_id, success status, and processing time. Provides methods
    to retrieve statistics and calculate cost estimates.
    """
    
    # Cost per image in USD
    COST_PER_IMAGE = 0.08
    
    def __init__(self, log_file: str = None):
        """
        Initialize UsageTracker.
        
        Args:
            log_file: Path to JSON file for storing usage logs
        """
        if log_file is None:
            # Default path in data/ folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            log_file = os.path.join(parent_dir, 'data', 'usage_log.json')
        
        self.log_file = log_file
        self._ensure_log_file_exists()
        logger.info(f"UsageTracker initialized with log file: {log_file}")
    
    def _ensure_log_file_exists(self):
        """Create log file with empty array if it doesn't exist or is empty."""
        # Check if file exists and has content
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            with open(self.log_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created/initialized log file: {self.log_file}")
    
    def log_api_call(
        self,
        timestamp: str,
        user_session: str,
        hairstyle_id: str,
        success: bool,
        processing_time: float,
        error: Optional[str] = None
    ):
        """
        Log each API call with metadata.
        
        Args:
            timestamp: ISO format timestamp of the API call
            user_session: Anonymized user session identifier
            hairstyle_id: ID of the hairstyle being tried on
            success: Whether the API call succeeded
            processing_time: Time taken to process in seconds
            error: Error message if the call failed (optional)
        """
        try:
            # Read existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Create log entry
            log_entry = {
                "timestamp": timestamp,
                "user_session": user_session,
                "hairstyle_id": hairstyle_id,
                "success": success,
                "processing_time": processing_time,
                "error": error
            }
            
            # Append new entry
            logs.append(log_entry)
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.info(f"Logged API call: session={user_session}, hairstyle={hairstyle_id}, success={success}")
        
        except Exception as e:
            logger.error(f"Failed to log API call: {str(e)}", exc_info=True)
    
    def get_daily_stats(self, target_date: str) -> Dict:
        """
        Get statistics for a specific date.
        
        Args:
            target_date: Date in YYYY-MM-DD format
        
        Returns:
            Dict with statistics including:
                - date: The target date
                - total_calls: Total number of API calls
                - successful_calls: Number of successful calls
                - failed_calls: Number of failed calls
                - total_cost: Estimated cost in USD
                - average_processing_time: Average time in seconds
                - error_breakdown: Dict of error types and counts
        """
        try:
            # Read logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Filter logs for target date
            date_logs = [
                log for log in logs
                if log['timestamp'].startswith(target_date)
            ]
            
            # Calculate statistics
            total_calls = len(date_logs)
            successful_calls = sum(1 for log in date_logs if log['success'])
            failed_calls = total_calls - successful_calls
            
            # Calculate cost (only for successful calls)
            total_cost = successful_calls * self.COST_PER_IMAGE
            
            # Calculate average processing time
            if total_calls > 0:
                total_time = sum(log['processing_time'] for log in date_logs)
                average_processing_time = total_time / total_calls
            else:
                average_processing_time = 0.0
            
            # Error breakdown
            error_breakdown = {}
            for log in date_logs:
                if not log['success'] and log.get('error'):
                    error_type = log['error']
                    error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1
            
            stats = {
                "date": target_date,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "total_cost": round(total_cost, 2),
                "average_processing_time": round(average_processing_time, 2),
                "error_breakdown": error_breakdown
            }
            
            logger.info(f"Retrieved daily stats for {target_date}: {total_calls} calls, ${total_cost:.2f}")
            return stats
        
        except Exception as e:
            logger.error(f"Failed to get daily stats: {str(e)}", exc_info=True)
            return {
                "date": target_date,
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_cost": 0.0,
                "average_processing_time": 0.0,
                "error_breakdown": {}
            }
    
    def get_cost_estimate(self, start_date: str, end_date: str) -> float:
        """
        Calculate estimated costs for date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
        
        Returns:
            Total estimated cost in USD for the date range
        """
        try:
            # Read logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            # Filter logs for date range
            range_logs = [
                log for log in logs
                if start_date <= log['timestamp'][:10] <= end_date
            ]
            
            # Count successful calls (only these incur costs)
            successful_calls = sum(1 for log in range_logs if log['success'])
            
            # Calculate cost
            total_cost = successful_calls * self.COST_PER_IMAGE
            
            logger.info(
                f"Cost estimate for {start_date} to {end_date}: "
                f"{successful_calls} successful calls = ${total_cost:.2f}"
            )
            
            return round(total_cost, 2)
        
        except Exception as e:
            logger.error(f"Failed to calculate cost estimate: {str(e)}", exc_info=True)
            return 0.0
    
    def get_all_logs(self) -> List[Dict]:
        """
        Get all usage logs.
        
        Returns:
            List of all log entries
        """
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            return logs
        except Exception as e:
            logger.error(f"Failed to read logs: {str(e)}", exc_info=True)
            return []
