import streamlit as st
import requests
from datetime import datetime
import subprocess
import socket
import psutil
import pytz
import webbrowser

# Page Configuration
st.set_page_config(
    page_title="RHEL 9 System Dashboard",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.card {
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    margin-bottom: 20px;
}
.status-card {
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.success {
    background-color: #d4edda;
    border-left: 5px solid #28a745;
}
.info {
    background-color: #d1ecf1;
    border-left: 5px solid #17a2b8;
}
.header-font {
    font-size: 1.4rem !important;
    color: #2c3e50 !important;
}
</style>
""", unsafe_allow_html=True)

def get_system_info():
    """Collect comprehensive system information"""
    system_info = {}
    try:
        # Public IP
        system_info['public_ip'] = requests.get('https://api.ipify.org').text
        
        # Network Interfaces
        result = subprocess.run(['ip', '-br', '-4', 'addr'], capture_output=True, text=True)
        system_info['network_interfaces'] = result.stdout
        
        # System load
        system_info['load'] = psutil.getloadavg()
        system_info['cpu_percent'] = psutil.cpu_percent()
        system_info['memory'] = psutil.virtual_memory()
        
        return system_info
    except Exception as e:
        st.error(f"Error collecting system info: {str(e)}")
        return None

def get_ip_location(ip_address):
    """Get geolocation data for IP"""
    try:
        if not ip_address:
            return None
        
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Geolocation error: {str(e)}")
        return None

def format_time_with_timezone():
    """Get current time with timezone info"""
    tz = pytz.timezone('America/New_York')  # Change to your preferred timezone
    return datetime.now(tz).strftime("%H:%M:%S [%Z]")

# Sidebar Navigation
with st.sidebar:
    st.header("🛠️ System Tools")
    menu_option = st.radio(
        "Select Tool:",
        ["Dashboard", "IP Tools", "Date & Time", "Browser Control", "System Monitor"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("**System Status:**")
    
    # Live system status indicators
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU", f"{psutil.cpu_percent()}%")
    
    with col2:
        st.metric("Memory", f"{psutil.virtual_memory().percent}%")

# Main Content Area
if menu_option == "Dashboard":
    st.header("📊 RHEL 9 System Dashboard")
    
    # System Overview Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander("🌐 Network Overview", expanded=True):
            system_info = get_system_info()
            if system_info:
                st.code(f"Public IP: {system_info['public_ip']}", language="text")
                st.code("Local Interfaces:\n" + system_info['network_interfaces'], language="text")
    
    with col2:
        with st.expander("⏱️ Current Time", expanded=True):
            st.markdown(f"""
            <div style="font-size: 24px; text-align: center; padding: 20px;">
            {format_time_with_timezone()}
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.expander("📅 Current Date", expanded=True):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            st.markdown(f"""
            <div style="font-size: 24px; text-align: center; padding: 20px;">
            {current_date}
            </div>
            """, unsafe_allow_html=True)

elif menu_option == "IP Tools":
    st.header("🔧 IP Tools")
    
    tab1, tab2 = st.tabs(["IP Information", "IP Geolocation"])
    
    with tab1:
        system_info = get_system_info()
        if system_info:
            st.subheader("Network Details")
            st.code(system_info['network_interfaces'], language="text", line_numbers=True)
    
    with tab2:
        ip_address = st.text_input("Enter IP Address (or leave blank for your public IP):")
        if not ip_address:
            ip_address = system_info['public_ip'] if system_info else "8.8.8.8"  # Fallback
        
        if st.button("Locate IP"):
            with st.spinner("Fetching location data..."):
                location_data = get_ip_location(ip_address)
                if location_data:
                    st.subheader("🌍 Geolocation Results")
                    st.json(location_data)
                    
                    # Map visualization
                    try:
                        df = pd.DataFrame({
                            'lat': [location_data['lat']],
                            'lon': [location_data['lon']]
                        })
                        st.map(df, zoom=6)
                    except:
                        st.warning("Couldn't display map (pandas required)")

elif menu_option == "Date & Time":
    st.header("📅 Date & Time Tools")
    
    tz_col, format_col = st.columns(2)
    
    with tz_col:
        selected_tz = st.selectbox(
            "Select Timezone:",
            pytz.all_timezones,
            index=pytz.all_timezones.index('America/New_York')
        )
    
    with format_col:
        time_format = st.selectbox(
            "Time Format:",
            ["24-hour", "12-hour"]
        )
    
    st.markdown("---")
    st.subheader("Current Time")
    tz = pytz.timezone(selected_tz)
    current_time = datetime.now(tz)
    
    if time_format == "12-hour":
        time_str = current_time.strftime("%I:%M:%S %p [%Z]")
    else:
        time_str = current_time.strftime("%H:%M:%S [%Z]")
    
    st.markdown(f"""
    <div style="font-size: 36px; text-align: center; padding: 30px; border-radius: 10px; background: #f5f7fa;">
    {time_str}
    </div>
    """, unsafe_allow_html=True)

elif menu_option == "Browser Control":
    st.header("🌐 Browser Control")
    
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Controls")
            if st.button("🦊 Launch Firefox"):
                try:
                    subprocess.Popen(["firefox"])
                    st.success("Firefox launched successfully!")
                except Exception as e:
                    st.error(f"Failed to launch Firefox: {str(e)}")
            
            if st.button("🧹 Clear Browser Cache"):
                st.warning("Feature in development")
        
        with col2:
            st.subheader("Quick Links")
            if st.button("Red Hat Portal"):
                webbrowser.open_new_tab("https://redhat.com")
            if st.button("RHEL Documentation"):
                webbrowser.open_new_tab("https://access.redhat.com/documentation")

elif menu_option == "System Monitor":
    st.header("📈 System Monitor")
    
    # Real-time metrics
    st.subheader("Live System Metrics")
    
    # CPU Usage
    cpu_chart = st.empty()
    
    # Memory Usage
    mem_chart = st.empty()
    
    # Update charts in real-time
    while menu_option == "System Monitor":
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        with cpu_chart:
            st.progress(cpu_usage, text=f"CPU Usage: {cpu_usage}%")
        
        with mem_chart:
            st.progress(memory.percent, text=f"Memory Usage: {memory.percent}%")
        
        time.sleep(1)
        if st.button("Stop Monitoring"):
            break

# Footer
st.markdown("---")
st.markdown("Built with 🐍 Python & ❤️ for RHEL 9")

# Installation Instructions (hidden)
st.sidebar.markdown("---")
with st.sidebar.expander("Installation Help"):
    st.code("""
# To install dependencies:
sudo dnf install python3-pip firefox
pip install streamlit requests psutil pytz
    """, language="bash")

