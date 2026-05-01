# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from datetime import datetime, timedelta


class ChatbotAccessLog(Document):
	def before_insert(self):
		"""Set additional fields before inserting"""
		if not self.session_id:
			self.session_id = frappe.session.sid
		
		if not self.ip_address:
			self.ip_address = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None
		
		if not self.user_agent and hasattr(frappe.local, 'request') and frappe.local.request:
			self.user_agent = frappe.local.request.headers.get('User-Agent', '')


@frappe.whitelist()
def log_chatbot_access(query_text, query_type="General Chat", accessed_documents=None, 
                      vector_collections_used=None, permissions_applied=None, 
                      response_time_ms=None, results_count=0, sensitive_data_masked=False,
                      rate_limit_hit=False, security_flags=None, blocked_reason=None,
                      message_id=None, agent_name=None):
	"""Log chatbot access for audit trail"""
	try:
		log_doc = frappe.new_doc("Chatbot Access Log")
		log_doc.user = frappe.session.user
		log_doc.query_text = query_text
		log_doc.query_type = query_type
		log_doc.response_time_ms = response_time_ms
		log_doc.results_count = results_count
		log_doc.sensitive_data_masked = sensitive_data_masked
		log_doc.rate_limit_hit = rate_limit_hit
		log_doc.blocked_reason = blocked_reason
		
		# Thêm message_id và agent_name để group logs
		if message_id:
			log_doc.message_id = message_id
		if agent_name:
			log_doc.agent_name = agent_name
		
		if accessed_documents:
			log_doc.accessed_documents = json.dumps(accessed_documents)
		
		if vector_collections_used:
			log_doc.vector_collections_used = vector_collections_used
		
		if permissions_applied:
			log_doc.permissions_applied = json.dumps(permissions_applied)
		
		if security_flags:
			log_doc.security_flags = security_flags
		
		log_doc.insert(ignore_permissions=True)
		frappe.db.commit()
		
		return log_doc.name
		
	except Exception as e:
		frappe.log_error(f"Failed to log chatbot access: {str(e)}")
		return None


@frappe.whitelist()
def get_user_access_stats(user=None, days=30):
	"""Get access statistics for a user"""
	if not user:
		user = frappe.session.user
	
	from_date = datetime.now() - timedelta(days=days)
	
	stats = frappe.db.sql("""
		SELECT 
			COUNT(*) as total_queries,
			COUNT(DISTINCT DATE(timestamp)) as active_days,
			AVG(response_time_ms) as avg_response_time,
			SUM(CASE WHEN rate_limit_hit = 1 THEN 1 ELSE 0 END) as rate_limit_hits,
			SUM(CASE WHEN sensitive_data_masked = 1 THEN 1 ELSE 0 END) as masked_responses,
			SUM(CASE WHEN blocked_reason IS NOT NULL THEN 1 ELSE 0 END) as blocked_queries
		FROM `tabChatbot Access Log`
		WHERE user = %s AND timestamp >= %s
	""", (user, from_date), as_dict=True)
	
	query_types = frappe.db.sql("""
		SELECT query_type, COUNT(*) as count
		FROM `tabChatbot Access Log`
		WHERE user = %s AND timestamp >= %s
		GROUP BY query_type
		ORDER BY count DESC
	""", (user, from_date), as_dict=True)
	
	return {
		"stats": stats[0] if stats else {},
		"query_types": query_types,
		"period_days": days
	}


@frappe.whitelist()
def get_security_alerts(days=7):
	"""Get security alerts from access logs"""
	if not frappe.has_permission("Chatbot Access Log", "read"):
		frappe.throw("Insufficient permissions")
	
	from_date = datetime.now() - timedelta(days=days)
	
	# Rate limit violations
	rate_limit_alerts = frappe.db.sql("""
		SELECT user, COUNT(*) as violations, MAX(timestamp) as last_violation
		FROM `tabChatbot Access Log`
		WHERE rate_limit_hit = 1 AND timestamp >= %s
		GROUP BY user
		ORDER BY violations DESC
		LIMIT 10
	""", (from_date,), as_dict=True)
	
	# Blocked queries
	blocked_queries = frappe.db.sql("""
		SELECT user, blocked_reason, COUNT(*) as count, MAX(timestamp) as last_blocked
		FROM `tabChatbot Access Log`
		WHERE blocked_reason IS NOT NULL AND timestamp >= %s
		GROUP BY user, blocked_reason
		ORDER BY count DESC
		LIMIT 10
	""", (from_date,), as_dict=True)
	
	# Suspicious patterns
	suspicious_users = frappe.db.sql("""
		SELECT user, 
			COUNT(*) as total_queries,
			COUNT(DISTINCT ip_address) as ip_count,
			AVG(response_time_ms) as avg_response_time
		FROM `tabChatbot Access Log`
		WHERE timestamp >= %s
		GROUP BY user
		HAVING total_queries > 1000 OR ip_count > 5
		ORDER BY total_queries DESC
		LIMIT 10
	""", (from_date,), as_dict=True)
	
	return {
		"rate_limit_alerts": rate_limit_alerts,
		"blocked_queries": blocked_queries,
		"suspicious_users": suspicious_users,
		"period_days": days
	}


@frappe.whitelist()
def cleanup_old_logs(days=90):
	"""Clean up old access logs"""
	if not frappe.has_permission("Chatbot Access Log", "delete"):
		frappe.throw("Insufficient permissions")
	
	cutoff_date = datetime.now() - timedelta(days=days)
	
	deleted_count = frappe.db.sql("""
		DELETE FROM `tabChatbot Access Log`
		WHERE timestamp < %s
	""", (cutoff_date,))
	
	frappe.db.commit()
	
	return {
		"deleted_count": deleted_count,
		"cutoff_date": cutoff_date
	}


@frappe.whitelist()
def get_audit_logs(
	page=1,
	page_size=50,
	date_filter='today',
	action_filter='',
	search_query='',
	group_by_message=True
):
	"""
	Get audit logs with filtering and pagination, grouped by message_id
	
	Args:
		page: Page number (1-indexed)
		page_size: Items per page
		date_filter: 'today', 'week', 'month', 'all'
		action_filter: Filter by query_type (empty for all)
		search_query: Search in query_text or user
		group_by_message: If True, group logs by message_id (default: True)
	
	Returns:
		dict with grouped logs and pagination info
	"""
	try:
		# Check permissions
		if not frappe.has_permission("Chatbot Access Log", "read"):
			frappe.throw("Không có quyền xem audit logs")
		
		# Build filters
		filters = []
		
		# Date filter
		if date_filter != 'all':
			now = datetime.now()
			if date_filter == 'today':
				from_date = now - timedelta(days=1)
			elif date_filter == 'week':
				from_date = now - timedelta(days=7)
			elif date_filter == 'month':
				from_date = now - timedelta(days=30)
			else:
				from_date = None
			
			if from_date:
				filters.append(f"timestamp >= '{from_date.strftime('%Y-%m-%d %H:%M:%S')}'")
		
		# Action filter (query_type)
		if action_filter:
			filters.append(f"query_type = '{frappe.db.escape(action_filter)}'")
		
		# Search filter
		if search_query:
			search_escaped = frappe.db.escape(f"%{search_query}%")
			filters.append(f"(query_text LIKE {search_escaped} OR user LIKE {search_escaped})")
		
		where_clause = " AND ".join(filters) if filters else "1=1"
		
		# Get total count
		total_count = frappe.db.sql(f"""
			SELECT COUNT(*) as count
			FROM `tabChatbot Access Log`
			WHERE {where_clause}
		""", as_dict=True)[0]['count']
		
		# Calculate pagination
		page = max(1, int(page))
		page_size = max(1, min(5000, int(page_size)))  # Increase limit to 5000 for admin view
		offset = (page - 1) * page_size
		total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
		
		# Get logs with message_id and agent_name
		logs = frappe.db.sql(f"""
			SELECT 
				name as id,
				timestamp,
				user,
				query_type as action,
				query_text as query,
				response_time_ms,
				results_count,
				vector_collections_used as collection,
				ip_address,
				rate_limit_hit,
				blocked_reason,
				message_id,
				agent_name,
				conversation_id,
				permissions_applied,
				CASE 
					WHEN blocked_reason IS NOT NULL THEN 'Failed'
					ELSE 'Success'
				END as status
			FROM `tabChatbot Access Log`
			WHERE {where_clause}
			ORDER BY timestamp DESC
			LIMIT {page_size} OFFSET {offset}
		""", as_dict=True)
		
		# Group logs by message_id if requested
		if group_by_message:
			grouped_logs = _group_logs_by_message(logs)
			formatted_logs = grouped_logs
		else:
			# Format logs for frontend (non-grouped)
			formatted_logs = []
			for log in logs:
				formatted_logs.append(_format_log_entry(log))
		
		return {
			'success': True,
			'logs': formatted_logs,
			'pagination': {
				'page': page,
				'page_size': page_size,
				'total_count': total_count,
				'total_pages': total_pages,
				'has_next': page < total_pages,
				'has_prev': page > 1
			}
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting audit logs: {str(e)}")
		return {
			'success': False,
			'error': str(e),
			'logs': [],
			'pagination': {
				'page': 1,
				'page_size': page_size,
				'total_count': 0,
				'total_pages': 1,
				'has_next': False,
				'has_prev': False
			}
		}


@frappe.whitelist()
def export_audit_logs(date_filter='today', action_filter=''):
	"""
	Export audit logs as CSV
	
	Args:
		date_filter: 'today', 'week', 'month', 'all'
		action_filter: Filter by query_type
	
	Returns:
		CSV file content
	"""
	try:
		if not frappe.has_permission("Chatbot Access Log", "read"):
			frappe.throw("Không có quyền export audit logs")
		
		# Build filters (same as get_audit_logs)
		filters = []
		
		if date_filter != 'all':
			now = datetime.now()
			if date_filter == 'today':
				from_date = now - timedelta(days=1)
			elif date_filter == 'week':
				from_date = now - timedelta(days=7)
			elif date_filter == 'month':
				from_date = now - timedelta(days=30)
			else:
				from_date = None
			
			if from_date:
				filters.append(f"timestamp >= '{from_date.strftime('%Y-%m-%d %H:%M:%S')}'")
		
		if action_filter:
			filters.append(f"query_type = '{frappe.db.escape(action_filter)}'")
		
		where_clause = " AND ".join(filters) if filters else "1=1"
		
		# Get all logs matching filters
		logs = frappe.db.sql(f"""
			SELECT 
				timestamp,
				user,
				query_type as action,
				query_text as query,
				response_time_ms,
				results_count,
				vector_collections_used as collection,
				ip_address,
				CASE 
					WHEN blocked_reason IS NOT NULL THEN 'Failed'
					ELSE 'Success'
				END as status
			FROM `tabChatbot Access Log`
			WHERE {where_clause}
			ORDER BY timestamp DESC
		""", as_dict=True)
		
		# Generate CSV
		import csv
		from io import StringIO
		
		output = StringIO()
		writer = csv.writer(output)
		
		# Write header
		writer.writerow([
			'Timestamp',
			'User',
			'Action',
			'Query',
			'Response Time (ms)',
			'Results Count',
			'Collection',
			'IP Address',
			'Status'
		])
		
		# Write data
		for log in logs:
			writer.writerow([
				log.get('timestamp', ''),
				log.get('user', ''),
				log.get('action', ''),
				log.get('query', ''),
				log.get('response_time_ms', ''),
				log.get('results_count', ''),
				log.get('collection', ''),
				log.get('ip_address', ''),
				log.get('status', '')
			])
		
		csv_content = output.getvalue()
		output.close()
		
		return {
			'success': True,
			'csv_content': csv_content,
			'filename': f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
		}
		
	except Exception as e:
		frappe.log_error(f"Error exporting audit logs: {str(e)}")
		return {
			'success': False,
			'error': str(e)
		}


def _format_log_entry(log):
	"""Format a single log entry for frontend"""
	# Format timestamp
	ts = log.get('timestamp')
	if isinstance(ts, datetime):
		timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')
	else:
		timestamp_str = str(ts) if ts else ''
	
	# Format response time
	response_time = log.get('response_time_ms', 0)
	if response_time:
		response_time_str = f"{response_time / 1000:.1f}s"
	else:
		response_time_str = "N/A"
	
	# Calculate tokens used (estimate based on query + response)
	query_length = len(log.get('query', ''))
	tokens_used = max(50, query_length // 4)  # Rough estimate
	
	# Extract result_summary from permissions_applied
	result_summary = None
	permissions_applied = log.get('permissions_applied')
	if permissions_applied:
		try:
			if isinstance(permissions_applied, str):
				parsed = json.loads(permissions_applied)
			else:
				parsed = permissions_applied
			result_summary = parsed.get('result_summary', {})
		except (json.JSONDecodeError, TypeError):
			result_summary = None
	
	return {
		'id': log.get('id'),
		'timestamp': timestamp_str,
		'user': log.get('user', 'Unknown'),
		'action': log.get('action', 'Unknown'),
		'query': log.get('query', '')[:200],  # Truncate long queries
		'responseTime': response_time_str,
		'tokensUsed': tokens_used,
		'collection': log.get('collection', 'N/A'),
		'ipAddress': log.get('ip_address', 'N/A'),
		'status': log.get('status', 'Unknown'),
		'messageId': log.get('message_id'),
		'agentName': log.get('agent_name'),
		'conversationId': log.get('conversation_id'),
		'resultSummary': result_summary
	}


def _group_logs_by_message(logs):
	"""
	Group logs by message_id (như hóa đơn và chi tiết hóa đơn)
	
	Returns:
		List of grouped messages with agent details
	"""
	from collections import defaultdict
	
	# Group by message_id
	grouped = defaultdict(list)
	for log in logs:
		message_id = log.get('message_id') or log.get('id')  # Fallback to log id if no message_id
		grouped[message_id].append(log)
	
	# Format grouped logs
	formatted_groups = []
	for message_id, message_logs in grouped.items():
		# Sort logs by timestamp (earliest first to show agent execution order)
		message_logs.sort(key=lambda x: x.get('timestamp', ''))
		
		# Get main info from first log (hoặc log có agent_name rỗng - user query)
		main_log = message_logs[0]
		
		# Calculate aggregated stats
		total_response_time = sum(log.get('response_time_ms', 0) for log in message_logs)
		total_tokens = sum(max(50, len(log.get('query', '')) // 4) for log in message_logs)
		agent_count = len(message_logs)
		
		# Format timestamp
		ts = main_log.get('timestamp')
		if isinstance(ts, datetime):
			timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')
		else:
			timestamp_str = str(ts) if ts else ''
		
		# Check if any agent failed
		has_failure = any(log.get('status') == 'Failed' for log in message_logs)
		status = 'Failed' if has_failure else 'Success'
		
		# Format agent details (chi tiết hóa đơn)
		agent_details = []
		for log in message_logs:
			agent_details.append(_format_log_entry(log))
		
		# Create grouped entry (hóa đơn)
		formatted_groups.append({
			'id': message_id,
			'messageId': message_id,
			'timestamp': timestamp_str,
			'user': main_log.get('user', 'Unknown'),
			'action': f"Message ({agent_count} agents)",
			'query': main_log.get('query', '')[:200],
			'responseTime': f"{total_response_time / 1000:.1f}s",
			'tokensUsed': total_tokens,
			'collection': main_log.get('collection', 'N/A'),
			'ipAddress': main_log.get('ip_address', 'N/A'),
			'status': status,
			'agentCount': agent_count,
			'conversationId': main_log.get('conversation_id'),
			'agents': agent_details  # Chi tiết các agents đã chạy
		})
	
	return formatted_groups
