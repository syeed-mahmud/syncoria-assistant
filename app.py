import streamlit as st
import requests
import json
from datetime import datetime
import uuid
import time

# Page configuration
st.set_page_config(
    page_title="Syncoria Odoo Assistant",
    page_icon="images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS for background color and basic styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    
    .main-header {
        background-color: #875A7B;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .user-message {
        background-color: #875A7B;
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    
    .assistant-message {
        background-color: white;
        color: #333;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        margin-right: 20%;
        border: 1px solid #ddd;
    }
    
    .sidebar-header {
        background-color: #875A7B;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# API base URL
API_BASE_URL = "http://52.72.249.33:8000"

# Initialize session state
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}

def create_new_session():
    """Create a new chat session"""
    try:
        response = requests.get(f"{API_BASE_URL}/session")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data['session_id']
            st.session_state.current_session_id = session_id
            st.session_state.chat_history = []
            st.session_state.sessions[session_id] = {
                'created_at': session_data['created_at'],
                'title': f"New chat {len(st.session_state.sessions) + 1}"
            }
            return session_id
        else:
            st.error(f"Failed to create session: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Failed to create new session: {e}")
        return None

def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/history",
            json={"session_id": session_id, "limit": 50}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to get chat history: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to get chat history: {e}")
    return None

def send_query(query, session_id):
    """Send query to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={
                "query": query,
                "session_id": session_id,
                "include_debug": False
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to send query: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to send query: {e}")
    return None

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    if not timestamp_str:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%m/%d/%Y %H:%M")
    except:
        return timestamp_str

def process_markdown(content):
    """Convert basic markdown to HTML"""
    import re
    
    # Handle headers
    content = re.sub(r'^### (.*$)', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*$)', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*$)', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Handle bold text
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    
    # Handle line breaks
    content = content.replace('\n', '<br>')
    
    return content

def get_session_title(session_id):
    """Get a meaningful title for the session"""
    if session_id in st.session_state.sessions:
        return st.session_state.sessions[session_id]['title']
    return f"Chat {session_id[:8]}"

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h3>Syncoria Assistant</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.image("images/logo.png", width=100):
        pass
    
    # New chat button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_new_session()
        st.rerun()
    
    # Chat sessions
    if st.session_state.sessions:
        st.subheader("Recent Chats")
        
        for session_id, session_info in st.session_state.sessions.items():
            is_active = session_id == st.session_state.current_session_id
            
            if st.button(
                session_info['title'],
                key=f"session_{session_id}",
                help=f"Created: {format_timestamp(session_info['created_at'])}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                st.session_state.current_session_id = session_id
                # Load chat history
                history_data = get_chat_history(session_id)
                if history_data:
                    processed_messages = []
                    for msg in history_data.get('messages', []):
                        if msg['role'].lower() == 'user':
                            processed_messages.append({
                                'role': 'user',
                                'content': msg.get('query', msg.get('content', '')),
                                'timestamp': msg.get('timestamp', '')
                            })
                        else:
                            processed_messages.append({
                                'role': 'assistant',
                                'content': msg.get('content', ''),
                                'analysis': msg.get('analysis', msg.get('content', '')),
                                'chart_generated': bool(msg.get('chart_s3_url')),
                                'chart_s3_url': msg.get('chart_s3_url'),
                                'chart_decision_reason': msg.get('chart_decision_reason'),
                                'timestamp': msg.get('timestamp', '')
                            })
                    st.session_state.chat_history = processed_messages
                st.rerun()

# Main content area
st.markdown("""
<div class="main-header">
    <h1>Syncoria Odoo Assistant</h1>
    <p>Session ID: {}</p>
</div>
""".format(st.session_state.current_session_id if st.session_state.current_session_id else "None"), unsafe_allow_html=True)

# Create session if none exists
if not st.session_state.current_session_id:
    create_new_session()

# Chat messages display
if st.session_state.current_session_id:
    # Welcome message
    if not st.session_state.chat_history:
        st.info("👋 Hello! I'm your Syncoria Odoo Assistant. I can help you analyze your business data, generate insights, and create visualizations. What would you like to explore today?")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong><br>
                {message['content']}<br>
                <small>{format_timestamp(message.get('timestamp', ''))}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if this is a thinking message
            is_thinking = message.get('is_thinking', False)
            content = message.get('analysis', message.get('content', ''))
            
            if is_thinking:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>Syncoria Assistant:</strong><br>
                    {content} <em>thinking...</em>
                </div>
                """, unsafe_allow_html=True)
            else:
                processed_content = process_markdown(content)
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>Syncoria Assistant:</strong><br>
                    {processed_content}<br>
                    <small>{format_timestamp(message.get('timestamp', ''))}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Display chart if available
                if message.get('chart_generated', False) and message.get('chart_s3_url'):
                    st.image(message.get('chart_s3_url'), caption="Generated Chart", use_column_width=True)
                
                # Show chart decision reason if chart not generated
                elif message.get('chart_generated', None) is False:
                    reason = message.get('chart_decision_reason', '')
                    if reason:
                        st.warning(f"Chart Decision: {reason}")

# Input form at the bottom
st.markdown("---")
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "",
        placeholder="Type your question here...",
        key="user_input"
    )
    
    submit_button = st.form_submit_button("Send", type="primary", use_container_width=True)

# Handle form submission
if submit_button and user_input and st.session_state.current_session_id:
    # Add user message to chat history immediately
    user_message = {
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.chat_history.append(user_message)
    
    # Add thinking message
    thinking_message = {
        'role': 'assistant',
        'content': 'Analyzing your question...',
        'analysis': 'Analyzing your question...',
        'is_thinking': True,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.chat_history.append(thinking_message)
    
    # Rerun to show messages
    st.rerun()

# Process pending query
if (st.session_state.chat_history and 
    st.session_state.chat_history[-1].get('is_thinking', False)):
    
    # Get the user query
    user_query = st.session_state.chat_history[-2]['content']
    
    # Send query to API
    with st.spinner("Processing your request..."):
        response = send_query(user_query, st.session_state.current_session_id)
    
    if response:
        # Replace thinking message with actual response
        assistant_message = {
            'role': 'assistant',
            'content': response.get('analysis', ''),
            'analysis': response.get('analysis', ''),
            'chart_generated': response.get('chart_generated', False),
            'chart_s3_url': response.get('chart_s3_url'),
            'chart_decision_reason': response.get('chart_decision_reason'),
            'timestamp': response.get('timestamp')
        }
        st.session_state.chat_history[-1] = assistant_message
        
        # Update session title with first query
        if len(st.session_state.chat_history) == 2:  # First exchange
            st.session_state.sessions[st.session_state.current_session_id]['title'] = user_query[:50] + "..." if len(user_query) > 50 else user_query
    else:
        # Replace thinking message with error message
        error_message = {
            'role': 'assistant',
            'content': "I'm sorry, I encountered an error processing your request. Please try again.",
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_history[-1] = error_message
    
    # Rerun to show actual response
    st.rerun()