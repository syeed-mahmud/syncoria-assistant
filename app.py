import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

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
    /* Target the main app container in a stable way */
    [data-testid="stAppViewContainer"] {
        padding-bottom: 1rem;
    }
    .stApp {
        background-color: #f5f5ff;
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
        background-color: #2a333740;
        color: #0e101a;
        padding: 1rem;
        border-radius: 1rem 1rem 0.25rem 1rem;
        margin: 0.5rem 0;
        margin-left: 20%;
        border: 1px solid #0e101a;
    }
    .assistant-message {
        background-color: white;
        color: #333;
        padding: 1rem;
        border-radius: 1rem 1rem 1rem 0.25rem;
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
            
    .st-emotion-cache-18wcnp {
        background-color: #d9d9d9;
        color: #0e101a;
        border: 1px solid #0e101a;
    }
    .st-emotion-cache-18wcnp:hover {
        background-color: #31333f99;
        color: #0e101a;
        border: 1px solid #0e101a;
    }
    
            
    .st-emotion-cache-1yskf17 {
        background-color: #4d617a;
        color: #fafafa;
        border: 1px solid #fafafa;
    }
    .st-emotion-cache-1yskf17:hover {
        background-color: #2a4971;
        color: #fafafa;
        border: 1px solid #fafafa;
    }
    
    .st-emotion-cache-9ajs8n {
        color: #0e101a;
    }
            
    .st-emotion-cache-17r1dd6{
        color: #0e101a;
    }
    

</style>
""", unsafe_allow_html=True)

# API base URL
API_BASE_URL = "http://35.175.139.3:8000"

# Initialize session state
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}

# --- Helper Functions ---

def create_new_session():
    """Create a new chat session"""
    try:
        response = requests.get(f"{API_BASE_URL}/session")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data['session_id']
        st.session_state.current_session_id = session_id
        st.session_state.chat_history = []
        st.session_state.sessions[session_id] = {
            'created_at': session_data['created_at'],
            'title': f"New chat {len(st.session_state.sessions) + 1}"
        }
        return session_id
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create new session: {e}")
        return None

def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        response = requests.post(f"{API_BASE_URL}/history", json={"session_id": session_id, "limit": 50})
        response.raise_for_status()
        data = response.json()
        messages = data.get('messages', [])
        if messages and 'sequence_number' in messages[0]:
            messages.sort(key=lambda msg: msg.get('sequence_number', 0))
        return messages
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to get chat history: {e}")
    return []

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    if not timestamp_str: return ""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%m/%d/%Y %H:%M")
    except:
        return timestamp_str

def process_and_display_stream(query, session_id):
    """Handles the streaming API call and shows only the current event."""
    final_response = {}
    
    try:
        with st.status("Waiting for API response...", expanded=True) as status:
            # This placeholder will be cleared and rewritten on each event
            event_placeholder = status.empty()

            response = requests.post(
                f"{API_BASE_URL}/query/stream",
                json={"query": query, "session_id": session_id, "include_debug": False},
                stream=True
            )
            response.raise_for_status()
            
            event_type = ""
            
            for line in response.iter_lines():
                if not line: continue
                decoded_line = line.decode('utf-8')

                if decoded_line.startswith('event:'):
                    event_type = decoded_line.split(':', 1)[1].strip()
                elif decoded_line.startswith('data:'):
                    data_str = decoded_line.split(':', 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                        
                        # Update the main status label if the event is a 'status' message
                        if event_type == "status":
                            status.update(label=data.get("message", "Processing..."))
                        
                        # Overwrite the placeholder with the current event's details
                        with event_placeholder.container():
                            st.markdown(f"**Event:** `{event_type}`")
                            st.json(data)

                        # Store the final payload when the 'complete' event is received
                        if event_type == "complete":
                            final_response = data
                            
                    except json.JSONDecodeError:
                        continue
            
            # After the loop finishes, update the status box to its final state
            status.update(label="Stream complete! Processing final response.", state="complete", expanded=False)

    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        final_response = {"analysis": "Sorry, I encountered an error connecting to the API."}

    # --- Post-stream processing ---
    dataframe = None
    if final_response.get('csv_url'):
        try:
            dataframe = pd.read_csv(final_response['csv_url'])
        except Exception as e:
            st.warning(f"Could not display data table: {e}")

    # Update session state with the final message, including the dataframe
    assistant_message = {
        'role': 'assistant',
        'analysis': final_response.get('analysis', "No analysis provided."),
        'dataframe': dataframe,
        'chart_generated': final_response.get('chart_generated', False),
        'chart_s3_url': final_response.get('chart_s3_url'),
        'csv_url': final_response.get('csv_url'),
        'xlsx_url': final_response.get('xlsx_url'),
        'chart_decision_reason': final_response.get('chart_decision_reason', ''),
        'timestamp': final_response.get('timestamp', datetime.now().isoformat()),
        'is_thinking': False
    }
    # Update the placeholder 'thinking' message with the final results
    if st.session_state.chat_history and st.session_state.chat_history[-1].get('is_thinking'):
        st.session_state.chat_history[-1] = assistant_message
    else:
        st.session_state.chat_history.append(assistant_message)

    # Update session title with the first real query
    if len(st.session_state.chat_history) == 2:
        title = query[:45] + "..." if len(query) > 45 else query
        st.session_state.sessions[session_id]['title'] = title

    st.rerun()

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'><h3>Syncoria Assistant</h3></div>", unsafe_allow_html=True)
    st.image("images/logo.png", width=100)
    
    if st.button("New Chat", use_container_width=True, type="primary"):
        create_new_session()
        st.rerun()
    
    if st.session_state.sessions:
        st.subheader("Recent Chats")
        sorted_sessions = sorted(st.session_state.sessions.items(), key=lambda i: i[1]['created_at'], reverse=True)
        for session_id, info in sorted_sessions:
            if st.button(
                info['title'], key=f"session_{session_id}", use_container_width=True,
                type="primary" if session_id == st.session_state.current_session_id else "secondary"
            ):
                st.session_state.current_session_id = session_id
                messages = get_chat_history(session_id)
                st.session_state.chat_history = messages
                st.rerun()

# --- Main Page UI ---
st.markdown(f"""
<div class="main-header">
    <h1>Syncoria Odoo Assistant</h1>
    <p>Session ID: {st.session_state.current_session_id or "No active session"}</p>
</div>
""", unsafe_allow_html=True)

# Display welcome message if no chat history
if not st.session_state.chat_history:
    st.info("👋 Hello! I'm your Syncoria Odoo Assistant. How can I help you today?")

# st.markdown(f"<br><div class='assistant-message'><strong>Syncoria Assistant:</strong><br>{msg.get('analysis', '')}</div>", unsafe_allow_html=True)
# Display chat history
for msg in st.session_state.chat_history:
    role = msg.get('role', '').lower()
    if role == 'user':
        st.markdown(f"<div class='user-message'><strong>You:</strong><br>{msg.get('content') or msg.get('query', '')}</div>", unsafe_allow_html=True)
    elif role == 'assistant' and not msg.get('is_thinking'):
        st.markdown("<strong>Syncoria Assistant:</strong>", unsafe_allow_html=True)
        # Handle both 'analysis' (new messages) and 'content' (historical messages) fields
        analysis_text = msg.get('analysis', '') or msg.get('content', '')
        st.markdown(analysis_text)

        # Display dataframe if available (either stored or from CSV URL)
        dataframe_to_show = None
        if 'dataframe' in msg and msg['dataframe'] is not None:
            dataframe_to_show = msg['dataframe']
        elif msg.get('csv_url'):
            try:
                dataframe_to_show = pd.read_csv(msg['csv_url'])
            except Exception as e:
                st.warning(f"Could not load data table from previous session: {e}")
        
        if dataframe_to_show is not None:
            st.dataframe(dataframe_to_show, use_container_width=True)

        # Display chart if URL is available (works for both new and historical messages)
        if msg.get('chart_s3_url'):
            st.image(msg['chart_s3_url'], use_container_width=True)
    

# Handle input and processing
if user_input := st.chat_input("Ask about your Odoo data..."):
    if not st.session_state.current_session_id:
        session_id = create_new_session()
        if not session_id:
            st.error("Failed to create a new session. Please try again.")
            st.stop()
    
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})
    st.session_state.chat_history.append({'role': 'assistant', 'is_thinking': True})
    st.rerun()

# This logic block triggers the stream processing
if st.session_state.chat_history and st.session_state.chat_history[-1].get('is_thinking'):
    user_query = st.session_state.chat_history[-2].get('content', '')
    session_id = st.session_state.current_session_id
    process_and_display_stream(user_query, session_id)