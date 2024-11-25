from requests_oauthlib import OAuth2Session
import streamlit as st
import os

# Allow OAuth for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class GithubAuthManager:
    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.auth_endpoint = "https://github.com/login/oauth/authorize"
        self.token_endpoint = "https://github.com/login/oauth/access_token"
        self.redirect_uri = os.getenv("REDIRECT_URI")
        
    def begin_auth(self):
        """Start the authentication process"""
        if st.button("Login with GitHub", type="primary"):
            try:
                # Create OAuth session without scope
                oauth = OAuth2Session(
                    client_id=self.client_id,
                    redirect_uri=self.redirect_uri
                )
                
                # Get authorization URL with scope
                auth_url, state = oauth.authorization_url(
                    self.auth_endpoint
                )
                
                # Store state
                st.session_state['oauth_state'] = state
                
                # Redirect to GitHub
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={auth_url}">', 
                    unsafe_allow_html=True
                )
                
            except Exception as e:
                st.error(f"Failed to start authentication: {str(e)}")
    
    def complete_auth(self):
        """Complete the authentication process"""
        params = st.experimental_get_query_params()
        
        if 'code' in params and not self.is_authenticated():
            try:
                code = params['code'][0]
                
                # Create new OAuth session
                oauth = OAuth2Session(
                    client_id=self.client_id,
                    redirect_uri=self.redirect_uri,
                    state=st.session_state.get('oauth_state')
                )
                
                # Exchange code for token
                token = oauth.fetch_token(
                    self.token_endpoint,
                    client_secret=self.client_secret,
                    code=code
                )
                
                # Store token
                st.session_state['token'] = token
                
                # Get and store user data
                user_response = oauth.get('https://api.github.com/user')
                if user_response.status_code == 200:
                    st.session_state['user'] = user_response.json()
                else:
                    raise Exception(f"Failed to get user data: {user_response.text}")
                
                # Clean up
                if 'oauth_state' in st.session_state:
                    del st.session_state['oauth_state']
                st.experimental_set_query_params()
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Authentication failed")
                self.logout()
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return 'token' in st.session_state and 'user' in st.session_state
    
    def show_user_info(self):
        """Display user information in sidebar"""
        if self.is_authenticated():
            user = st.session_state['user']
            
            col1, col2 = st.sidebar.columns([1, 3])
            with col1:
                st.image(user.get('avatar_url', ''), width=50)
            with col2:
                st.write(f"Welcome, {user.get('name') or user.get('login')}")
            
            if st.sidebar.button('Logout', type="secondary"):
                self.logout()
                st.experimental_rerun()
    
    def logout(self):
        """Clear all authentication data"""
        for key in ['token', 'user', 'oauth_state']:
            if key in st.session_state:
                del st.session_state[key]