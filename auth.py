import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Auth:
    def __init__(self, database):
        self.db = database

    def login(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user and return user info if successful"""
        try:
            logger.info(f"Attempting login for user: {username}")
            user = self.db.get_user(username)
            logger.info(f"Retrieved user data: {user}")
            
            if user and user['password'] == password:  # In production, use proper password hashing
                user_data = {
                    'username': user['username'],
                    'organization': user['organization'],
                    'organization_id': user['organization_id'],
                    'role': user['role']
                }
                logger.info(f"Login successful for user: {username}")
                return user_data
            logger.warning(f"Login failed for user: {username}")
            return None
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return None

    def render_login_page(self):
        """Render the login page"""
        st.markdown("""
            <div class="login-container">
                <div class="login-header">
                    <h2>🎯 Campaign Dashboard</h2>
                    <p>Sign in to your account</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if username and password:
                    user = self.login(username, password)
                    if user:
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")

    def check_authentication(self):
        """Check if user is authenticated"""
        is_auth = 'user' in st.session_state
        logger.info(f"Authentication check - Is authenticated: {is_auth}")
        return is_auth

    def logout(self):
        """Log out the user"""
        if 'user' in st.session_state:
            logger.info(f"Logging out user: {st.session_state.user['username']}")
            del st.session_state.user 