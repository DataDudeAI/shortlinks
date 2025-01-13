import streamlit as st
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class Organization:
    def __init__(self, database):
        self.db = database

    def get_organization_details(self, org_id: int) -> Optional[Dict]:
        """Get organization details"""
        try:
            org = self.db.execute_query(
                "SELECT * FROM organizations WHERE id = ?",
                (org_id,),
                fetch_one=True
            )
            if org:
                return {
                    'id': org['id'],
                    'name': org['name'],
                    'domain': org['domain'],
                    'created_at': org['created_at']
                }
            return None
        except Exception as e:
            logger.error(f"Error getting organization details: {str(e)}")
            return None

    def render_organization_settings(self):
        """Render organization settings page"""
        if not st.session_state.get('user') or st.session_state.user['role'] != 'admin':
            st.error("You don't have permission to access organization settings")
            return

        st.title("🏢 Organization Settings")
        
        org_id = st.session_state.user.get('organization_id')
        org_details = self.get_organization_details(org_id)

        if not org_details:
            st.error("Organization not found")
            return

        # Organization Details
        st.header("Organization Details")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Organization Name", value=org_details['name'], disabled=True)
        with col2:
            st.text_input("Domain", value=org_details['domain'], disabled=True)

        # User Management
        st.header("👥 User Management")
        
        # Add New User
        with st.expander("Add New User", expanded=False):
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["user", "admin"])
                
                if st.form_submit_button("Add User"):
                    if new_username and new_password:
                        if self.db.add_user(new_username, new_password, org_id, new_role):
                            st.success(f"User {new_username} added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add user")
                    else:
                        st.error("Please fill in all fields")

        # List Users
        users = self.db.get_organization_users(org_id)
        if users:
            st.subheader("Current Users")
            for user in users:
                col1, col2, col3 = st.columns([3,2,1])
                with col1:
                    st.text(user['username'])
                with col2:
                    st.text(user['role'])
                with col3:
                    if user['username'] != 'admin':  # Prevent removing admin
                        if st.button("Remove", key=f"remove_{user['username']}"):
                            if self.db.remove_user(user['username'], org_id):
                                st.success(f"User {user['username']} removed")
                                st.rerun()
                            else:
                                st.error("Failed to remove user") 