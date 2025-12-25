"""
Unit tests for UsageTracker

Tests log entry creation, daily statistics calculation, cost estimation,
and log file persistence.
"""

import unittest
import os
import json
import tempfile
from datetime import datetime, date
from usage_tracker import UsageTracker


class TestUsageTracker(unittest.TestCase):
    """Test cases for UsageTracker class."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.log_file = self.temp_file.name
        
        # Create tracker instance with temp file
        self.tracker = UsageTracker(log_file=self.log_file)
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary file
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_log_file_creation(self):
        """Test that log file is created if it doesn't exist."""
        # File should exist after initialization
        self.assertTrue(os.path.exists(self.log_file))
        
        # File should contain empty array
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        self.assertEqual(logs, [])
    
    def test_log_api_call_success(self):
        """Test logging a successful API call."""
        timestamp = "2024-01-15T10:30:00"
        user_session = "session_123"
        hairstyle_id = "hs001"
        success = True
        processing_time = 2.5
        
        self.tracker.log_api_call(
            timestamp=timestamp,
            user_session=user_session,
            hairstyle_id=hairstyle_id,
            success=success,
            processing_time=processing_time
        )
        
        # Read log file
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        # Verify log entry
        self.assertEqual(len(logs), 1)
        log_entry = logs[0]
        self.assertEqual(log_entry['timestamp'], timestamp)
        self.assertEqual(log_entry['user_session'], user_session)
        self.assertEqual(log_entry['hairstyle_id'], hairstyle_id)
        self.assertEqual(log_entry['success'], success)
        self.assertEqual(log_entry['processing_time'], processing_time)
        self.assertIsNone(log_entry['error'])
    
    def test_log_api_call_failure(self):
        """Test logging a failed API call with error message."""
        timestamp = "2024-01-15T10:35:00"
        user_session = "session_456"
        hairstyle_id = "hs002"
        success = False
        processing_time = 1.2
        error = "AuthenticationError"
        
        self.tracker.log_api_call(
            timestamp=timestamp,
            user_session=user_session,
            hairstyle_id=hairstyle_id,
            success=success,
            processing_time=processing_time,
            error=error
        )
        
        # Read log file
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        # Verify log entry
        self.assertEqual(len(logs), 1)
        log_entry = logs[0]
        self.assertEqual(log_entry['success'], False)
        self.assertEqual(log_entry['error'], error)
    
    def test_multiple_log_entries(self):
        """Test that multiple log entries are persisted correctly."""
        # Log multiple calls
        for i in range(5):
            self.tracker.log_api_call(
                timestamp=f"2024-01-15T10:{30+i}:00",
                user_session=f"session_{i}",
                hairstyle_id=f"hs00{i}",
                success=True,
                processing_time=2.0 + i * 0.5
            )
        
        # Read log file
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        # Verify all entries are present
        self.assertEqual(len(logs), 5)
        
        # Verify entries are in order
        for i, log_entry in enumerate(logs):
            self.assertEqual(log_entry['user_session'], f"session_{i}")
            self.assertEqual(log_entry['hairstyle_id'], f"hs00{i}")
    
    def test_get_daily_stats_empty(self):
        """Test getting daily stats when no logs exist."""
        target_date = "2024-01-15"
        stats = self.tracker.get_daily_stats(target_date)
        
        self.assertEqual(stats['date'], target_date)
        self.assertEqual(stats['total_calls'], 0)
        self.assertEqual(stats['successful_calls'], 0)
        self.assertEqual(stats['failed_calls'], 0)
        self.assertEqual(stats['total_cost'], 0.0)
        self.assertEqual(stats['average_processing_time'], 0.0)
        self.assertEqual(stats['error_breakdown'], {})
    
    def test_get_daily_stats_with_data(self):
        """Test calculating daily statistics with actual data."""
        target_date = "2024-01-15"
        
        # Log successful calls
        for i in range(3):
            self.tracker.log_api_call(
                timestamp=f"{target_date}T10:{30+i}:00",
                user_session=f"session_{i}",
                hairstyle_id=f"hs00{i}",
                success=True,
                processing_time=2.0
            )
        
        # Log failed calls
        for i in range(2):
            self.tracker.log_api_call(
                timestamp=f"{target_date}T11:{30+i}:00",
                user_session=f"session_{i+3}",
                hairstyle_id=f"hs00{i+3}",
                success=False,
                processing_time=1.0,
                error="RateLimitError"
            )
        
        # Get stats
        stats = self.tracker.get_daily_stats(target_date)
        
        # Verify statistics
        self.assertEqual(stats['date'], target_date)
        self.assertEqual(stats['total_calls'], 5)
        self.assertEqual(stats['successful_calls'], 3)
        self.assertEqual(stats['failed_calls'], 2)
        
        # Cost should be 3 successful calls * $0.08
        self.assertEqual(stats['total_cost'], 0.24)
        
        # Average processing time: (3*2.0 + 2*1.0) / 5 = 8.0 / 5 = 1.6
        self.assertEqual(stats['average_processing_time'], 1.6)
        
        # Error breakdown
        self.assertEqual(stats['error_breakdown']['RateLimitError'], 2)
    
    def test_get_daily_stats_filters_by_date(self):
        """Test that daily stats only includes logs from the target date."""
        # Log calls on different dates
        self.tracker.log_api_call(
            timestamp="2024-01-14T10:30:00",
            user_session="session_1",
            hairstyle_id="hs001",
            success=True,
            processing_time=2.0
        )
        
        self.tracker.log_api_call(
            timestamp="2024-01-15T10:30:00",
            user_session="session_2",
            hairstyle_id="hs002",
            success=True,
            processing_time=2.0
        )
        
        self.tracker.log_api_call(
            timestamp="2024-01-16T10:30:00",
            user_session="session_3",
            hairstyle_id="hs003",
            success=True,
            processing_time=2.0
        )
        
        # Get stats for Jan 15
        stats = self.tracker.get_daily_stats("2024-01-15")
        
        # Should only include the one call from Jan 15
        self.assertEqual(stats['total_calls'], 1)
        self.assertEqual(stats['successful_calls'], 1)
    
    def test_cost_estimate_single_day(self):
        """Test cost estimation for a single day."""
        target_date = "2024-01-15"
        
        # Log 10 successful calls
        for i in range(10):
            self.tracker.log_api_call(
                timestamp=f"{target_date}T10:{30+i}:00",
                user_session=f"session_{i}",
                hairstyle_id=f"hs00{i}",
                success=True,
                processing_time=2.0
            )
        
        # Get cost estimate
        cost = self.tracker.get_cost_estimate(target_date, target_date)
        
        # 10 successful calls * $0.08 = $0.80
        self.assertEqual(cost, 0.80)
    
    def test_cost_estimate_date_range(self):
        """Test cost estimation across multiple days."""
        # Log calls on different dates
        dates = ["2024-01-15", "2024-01-16", "2024-01-17"]
        
        for date_str in dates:
            for i in range(5):
                self.tracker.log_api_call(
                    timestamp=f"{date_str}T10:{30+i}:00",
                    user_session=f"session_{i}",
                    hairstyle_id=f"hs00{i}",
                    success=True,
                    processing_time=2.0
                )
        
        # Get cost estimate for the range
        cost = self.tracker.get_cost_estimate("2024-01-15", "2024-01-17")
        
        # 15 successful calls * $0.08 = $1.20
        self.assertEqual(cost, 1.20)
    
    def test_cost_estimate_excludes_failed_calls(self):
        """Test that cost estimation only counts successful calls."""
        target_date = "2024-01-15"
        
        # Log 5 successful calls
        for i in range(5):
            self.tracker.log_api_call(
                timestamp=f"{target_date}T10:{30+i}:00",
                user_session=f"session_{i}",
                hairstyle_id=f"hs00{i}",
                success=True,
                processing_time=2.0
            )
        
        # Log 3 failed calls
        for i in range(3):
            self.tracker.log_api_call(
                timestamp=f"{target_date}T11:{30+i}:00",
                user_session=f"session_{i+5}",
                hairstyle_id=f"hs00{i+5}",
                success=False,
                processing_time=1.0,
                error="RateLimitError"
            )
        
        # Get cost estimate
        cost = self.tracker.get_cost_estimate(target_date, target_date)
        
        # Only 5 successful calls should be counted: 5 * $0.08 = $0.40
        self.assertEqual(cost, 0.40)
    
    def test_cost_per_image_constant(self):
        """Test that cost per image is correctly set to $0.08."""
        self.assertEqual(UsageTracker.COST_PER_IMAGE, 0.08)
    
    def test_error_breakdown_multiple_types(self):
        """Test error breakdown with multiple error types."""
        target_date = "2024-01-15"
        
        # Log different error types
        errors = [
            "AuthenticationError",
            "RateLimitError",
            "RateLimitError",
            "TimeoutError",
            "ServerError",
            "ServerError",
            "ServerError"
        ]
        
        for i, error in enumerate(errors):
            self.tracker.log_api_call(
                timestamp=f"{target_date}T10:{30+i}:00",
                user_session=f"session_{i}",
                hairstyle_id=f"hs00{i}",
                success=False,
                processing_time=1.0,
                error=error
            )
        
        # Get stats
        stats = self.tracker.get_daily_stats(target_date)
        
        # Verify error breakdown
        self.assertEqual(stats['error_breakdown']['AuthenticationError'], 1)
        self.assertEqual(stats['error_breakdown']['RateLimitError'], 2)
        self.assertEqual(stats['error_breakdown']['TimeoutError'], 1)
        self.assertEqual(stats['error_breakdown']['ServerError'], 3)
    
    def test_log_file_persistence(self):
        """Test that logs persist across tracker instances."""
        # Log with first tracker instance
        self.tracker.log_api_call(
            timestamp="2024-01-15T10:30:00",
            user_session="session_1",
            hairstyle_id="hs001",
            success=True,
            processing_time=2.0
        )
        
        # Create new tracker instance with same log file
        new_tracker = UsageTracker(log_file=self.log_file)
        
        # Log with new tracker
        new_tracker.log_api_call(
            timestamp="2024-01-15T10:35:00",
            user_session="session_2",
            hairstyle_id="hs002",
            success=True,
            processing_time=2.5
        )
        
        # Read log file directly
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        # Both entries should be present
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]['user_session'], "session_1")
        self.assertEqual(logs[1]['user_session'], "session_2")
    
    def test_get_all_logs(self):
        """Test retrieving all logs."""
        # Log multiple calls
        for i in range(3):
            self.tracker.log_api_call(
                timestamp=f"2024-01-15T10:{30+i}:00",
                user_session=f"session_{i}",
                hairstyle_id=f"hs00{i}",
                success=True,
                processing_time=2.0
            )
        
        # Get all logs
        all_logs = self.tracker.get_all_logs()
        
        # Verify all logs are returned
        self.assertEqual(len(all_logs), 3)
        for i, log in enumerate(all_logs):
            self.assertEqual(log['user_session'], f"session_{i}")


if __name__ == '__main__':
    unittest.main()
