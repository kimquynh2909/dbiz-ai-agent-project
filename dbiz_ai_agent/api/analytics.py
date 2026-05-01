import frappe
from frappe import _
from datetime import datetime, timedelta
import json

def _check_table_exists(table_name):
    """Check if a database table exists"""
    try:
        result = frappe.db.sql("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name = %s
        """, (frappe.conf.db_name, table_name))
        return result[0][0] > 0 if result else False
    except Exception as e:
        frappe.log_error(f"Error checking table existence: {str(e)}")
        return False

@frappe.whitelist()
def Get_Analytics_Data(filter_type='7_days', start_date=None, end_date=None):
    """
    Get analytics data with date filters
    
    Args:
        filter_type: '7_days', 'month', 'custom'
        start_date: Start date for custom filter (YYYY-MM-DD)
        end_date: End date for custom filter (YYYY-MM-DD)
    """
    try:
        # Check if required tables exist
        conversation_table_exists = _check_table_exists('tabAI Conversation')
        message_table_exists = _check_table_exists('tabAI Conversation Message')
        
        # If tables don't exist, return mock data
        if not conversation_table_exists or not message_table_exists:
            frappe.log_error(
                "AI Conversation tables not found. Returning mock data.",
                "Analytics Warning"
            )
            return _get_mock_analytics_data(filter_type, start_date, end_date)
        
        # Calculate date range based on filter type
        end = datetime.now()
        
        if filter_type == '7_days':
            start = end - timedelta(days=7)
        elif filter_type == 'month':
            start = end - timedelta(days=30)
        elif filter_type == 'custom':
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                frappe.throw(_("Vui lòng chọn ngày bắt đầu và kết thúc"))
        else:
            start = end - timedelta(days=7)
        
        # Get conversation statistics
        conversations = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_conversations,
                SUM(message_count) as total_messages,
                AVG(message_count) as avg_messages_per_conversation
            FROM `tabAI Conversation`
            WHERE created_date BETWEEN %s AND %s
                AND status = 'Active'
        """, (start, end), as_dict=True)
        
        # Get message statistics by role
        message_stats = frappe.db.sql("""
            SELECT 
                role,
                COUNT(*) as count,
                AVG(TIMESTAMPDIFF(SECOND, timestamp, NOW())) as avg_response_time
            FROM `tabAI Conversation Message`
            WHERE timestamp BETWEEN %s AND %s
            GROUP BY role
        """, (start, end), as_dict=True)
        
        # Get feedback statistics
        feedback_stats = frappe.db.sql("""
            SELECT 
                feedback,
                COUNT(*) as count
            FROM `tabAI Conversation Message`
            WHERE timestamp BETWEEN %s AND %s
                AND feedback IS NOT NULL
            GROUP BY feedback
        """, (start, end), as_dict=True)
        
        # Get daily trend data
        daily_trends = frappe.db.sql("""
            SELECT 
                DATE(created_date) as date,
                COUNT(*) as conversation_count,
                SUM(message_count) as message_count
            FROM `tabAI Conversation`
            WHERE created_date BETWEEN %s AND %s
                AND status = 'Active'
            GROUP BY DATE(created_date)
            ORDER BY date
        """, (start, end), as_dict=True)
        
        # Calculate automation rate (messages handled by AI vs total)
        total_messages = sum(stat['count'] for stat in message_stats)
        assistant_messages = next((stat['count'] for stat in message_stats if stat['role'] == 'assistant'), 0)
        automation_rate = (assistant_messages / total_messages * 100) if total_messages > 0 else 0
        
        # Calculate satisfaction rate from feedback
        positive_feedback = sum(stat['count'] for stat in feedback_stats if stat['feedback'] == 'helpful')
        total_feedback = sum(stat['count'] for stat in feedback_stats)
        satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        # Calculate average latency (mock data for now - would need actual timing data)
        avg_latency = 145  # ms - placeholder
        
        return {
            "overview": {
                "automationRate": round(automation_rate, 1),
                "errorRate": 2.3,  # Mock data - would need error tracking
                "avgLatency": avg_latency,
                "minLatency": 89,  # Mock data
                "maxLatency": 312,  # Mock data
                "totalConversations": conversations[0]['total_conversations'] if conversations else 0,
                "totalMessages": conversations[0]['total_messages'] if conversations else 0,
                "satisfactionRate": round(satisfaction_rate, 1)
            },
            "messageStats": message_stats,
            "feedbackStats": feedback_stats,
            "dailyTrends": daily_trends,
            "dateRange": {
                "start": start.strftime('%Y-%m-%d'),
                "end": end.strftime('%Y-%m-%d'),
                "filterType": filter_type
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Analytics Error: {str(e)}")
        frappe.throw(_("Không thể tải dữ liệu analytics: {0}").format(str(e)))


@frappe.whitelist()
def Get_Agent_Performance(filter_type='7_days', start_date=None, end_date=None):
    """
    Get individual agent performance metrics
    """
    try:
        # Calculate date range
        end = datetime.now()
        
        if filter_type == '7_days':
            start = end - timedelta(days=7)
        elif filter_type == 'month':
            start = end - timedelta(days=30)
        elif filter_type == 'custom':
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                start = end - timedelta(days=7)
        else:
            start = end - timedelta(days=7)
        
        # Get agent conversation counts
        agent_stats = frappe.db.sql("""
            SELECT 
                'AI Chatbot' as name,
                COUNT(*) as requests,
                AVG(message_count) as avg_messages,
                SUM(CASE WHEN message_count > 0 THEN 1 ELSE 0 END) as resolved_count
            FROM `tabAI Conversation`
            WHERE created_date BETWEEN %s AND %s
                AND status = 'Active'
        """, (start, end), as_dict=True)
        
        # Mock agent performance data (would be expanded with real agent tracking)
        agents = [
            {
                "name": "Xử lý chứng từ tự động",
                "type": "Document Processing",
                "bgColor": "bg-blue-500",
                "icon": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
                "resolutionRate": 94.2,
                "handoffRate": 5.8,
                "satisfaction": 4.7,
                "requests": agent_stats[0]['requests'] if agent_stats else 0,
                "avgTime": 1.8
            },
            {
                "name": "Chatbot AI Agent",
                "type": "Conversational AI",
                "bgColor": "bg-purple-500",
                "icon": "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
                "resolutionRate": 96.2,
                "handoffRate": 3.8,
                "satisfaction": 4.8,
                "requests": agent_stats[0]['requests'] if agent_stats else 0,
                "avgTime": 1.2
            }
        ]
        
        return agents
        
    except Exception as e:
        frappe.log_error(f"Agent Performance Error: {str(e)}")
        return []


@frappe.whitelist()
def Get_Error_Logs(filter_type='7_days', start_date=None, end_date=None, limit=20):
    """
    Get error logs with date filters
    """
    try:
        # Calculate date range
        end = datetime.now()
        
        if filter_type == '7_days':
            start = end - timedelta(days=7)
        elif filter_type == 'month':
            start = end - timedelta(days=30)
        elif filter_type == 'custom':
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                start = end - timedelta(days=7)
        else:
            start = end - timedelta(days=7)
        
        # Get error logs from Frappe's error log
        error_logs = frappe.db.sql("""
            SELECT 
                name,
                error,
                method,
                creation,
                modified
            FROM `tabError Log`
            WHERE creation BETWEEN %s AND %s
            ORDER BY creation DESC
            LIMIT %s
        """, (start, end, limit), as_dict=True)
        
        # Format error logs
        formatted_logs = []
        for log in error_logs:
            # Determine severity based on error content
            error_text = str(log.get('error', '')).lower()
            if 'critical' in error_text or 'fatal' in error_text:
                severity = 'critical'
            elif 'error' in error_text:
                severity = 'error'
            else:
                severity = 'warning'
            
            # Calculate time ago
            time_diff = datetime.now() - log['creation']
            if time_diff.seconds < 3600:
                time_ago = f"{time_diff.seconds // 60} phút trước"
            elif time_diff.seconds < 86400:
                time_ago = f"{time_diff.seconds // 3600} giờ trước"
            else:
                time_ago = f"{time_diff.days} ngày trước"
            
            formatted_logs.append({
                "severity": severity,
                "agent": log.get('method', 'Unknown').split('.')[-1],
                "time": time_ago,
                "message": log.get('error', '')[:100],
                "details": log.get('method', '')
            })
        
        return formatted_logs
        
    except Exception as e:
        frappe.log_error(f"Error Logs Fetch Error: {str(e)}")
        return []


def _get_mock_analytics_data(filter_type='7_days', start_date=None, end_date=None):
    """
    Return mock analytics data when database tables don't exist
    This allows the dashboard to display even before DocTypes are created
    """
    # Calculate date range
    end = datetime.now()
    
    if filter_type == '7_days':
        start = end - timedelta(days=7)
    elif filter_type == 'month':
        start = end - timedelta(days=30)
    elif filter_type == 'custom':
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            start = end - timedelta(days=7)
    else:
        start = end - timedelta(days=7)
    
    # Generate mock daily trends
    days = (end - start).days
    daily_trends = []
    for i in range(days + 1):
        date = start + timedelta(days=i)
        daily_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'conversation_count': 10 + (i % 5),
            'message_count': 45 + (i * 3)
        })
    
    # Return mock data structure matching the real analytics
    return {
        "overview": {
            "automationRate": 94.5,
            "errorRate": 2.3,
            "avgLatency": 145,
            "minLatency": 89,
            "maxLatency": 312,
            "totalConversations": 127,
            "totalMessages": 856,
            "satisfactionRate": 92.8
        },
        "messageStats": [
            {"role": "user", "count": 428, "avg_response_time": 0},
            {"role": "assistant", "count": 428, "avg_response_time": 145}
        ],
        "feedbackStats": [
            {"feedback": "helpful", "count": 284},
            {"feedback": "not_helpful", "count": 28}
        ],
        "dailyTrends": daily_trends,
        "dateRange": {
            "start": start.strftime('%Y-%m-%d'),
            "end": end.strftime('%Y-%m-%d'),
            "filterType": filter_type
        },
        "_isMockData": True  # Flag to indicate this is mock data
    }

