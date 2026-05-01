#!/usr/bin/env python3
"""
Script to sync new DocTypes
Run: bench --site localerp.dbiz.com execute dbiz_ai_agent.helpers.sync_doctypes.sync_new_doctypes
"""

import frappe
from frappe.model.sync import sync_for

def sync_new_doctypes():
    """Sync new DocTypes for dbiz_ai_agent"""
    print("Syncing DocTypes for dbiz_ai_agent...")
    
    try:
        # Clear cache first
        frappe.clear_cache()
        
        # Sync DocTypes
        sync_for("dbiz_ai_agent", force=True, reset_permissions=True)
        
        frappe.db.commit()
        print("✅ DocTypes synced successfully!")
        
        # List new DocTypes
        doctypes = frappe.get_all(
            "DocType",
            filters={"module": "AI Agent"},
            fields=["name"]
        )
        
        print(f"\nFound {len(doctypes)} DocTypes in DBIZ AI Agent module:")
        for dt in doctypes:
            print(f"  - {dt.name}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        frappe.db.rollback()
        raise

if __name__ == "__main__":
    sync_new_doctypes()

