import streamlit as st
import requests
import json
import re
import random
import uuid
import math
import base64
from datetime import datetime
from functools import lru_cache
import io
from PIL import Image
import urllib.parse
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from PIL import ImageDraw, ImageFont
import logging
import traceback
import concurrent.futures
import time
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AskFlowChart")

# Set page configuration once at startup
st.set_page_config(page_title="Ask Flow Chart", layout="wide")

# Add FontAwesome for icons
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)

# Define design themes
DESIGN_THEMES = {
    "modern": {
        "name": "Modern Minimal",
        "node_styles": {
            "start": {"bg": "#4361EE", "text": "#FFFFFF", "shadow": "0 4px 6px rgba(67, 97, 238, 0.3)", "shape": "rounded"},
            "process": {"bg": "#F8F9FA", "text": "#212529", "shadow": "0 2px 5px rgba(0,0,0,0.08)", "shape": "rounded"},
            "decision": {"bg": "#FFF8E1", "text": "#1C1C1C", "shadow": "0 2px 5px rgba(0,0,0,0.08)", "shape": "diamond"},
            "end": {"bg": "#4CC9F0", "text": "#FFFFFF", "shadow": "0 4px 6px rgba(76, 201, 240, 0.3)", "shape": "rounded"},
        },
        "connector": {"color": "#CED4DA", "style": "curved", "thickness": "1.5px"},
        "font": "'Roboto', sans-serif",
        "icons": True
    },
    "corporate": {
        "name": "Corporate Professional",
        "node_styles": {
            "start": {"bg": "#2C3E50", "text": "#FFFFFF", "shadow": "0 4px 6px rgba(44, 62, 80, 0.3)", "shape": "rounded"},
            "process": {"bg": "#FFFFFF", "text": "#34495E", "shadow": "0 2px 4px rgba(0,0,0,0.1)", "shape": "rectangle"},
            "decision": {"bg": "#ECF0F1", "text": "#2C3E50", "shadow": "0 2px 4px rgba(0,0,0,0.1)", "shape": "diamond"},
            "end": {"bg": "#3498DB", "text": "#FFFFFF", "shadow": "0 4px 6px rgba(52, 152, 219, 0.3)", "shape": "rounded"},
        },
        "connector": {"color": "#95A5A6", "style": "straight", "thickness": "1.5px"},
        "font": "'Open Sans', sans-serif",
        "icons": True
    },
    "creative": {
        "name": "Creative Colorful",
        "node_styles": {
            "start": {"bg": "#FF6B6B", "text": "#FFFFFF", "shadow": "0 5px 15px rgba(255, 107, 107, 0.4)", "shape": "capsule"},
            "process": {"bg": "#FFFFFF", "text": "#2F2E41", "shadow": "0 5px 15px rgba(0,0,0,0.08)", "shape": "capsule"},
            "decision": {"bg": "#FFEAA7", "text": "#2F2E41", "shadow": "0 5px 15px rgba(0,0,0,0.08)", "shape": "diamond"},
            "end": {"bg": "#4ECDC4", "text": "#FFFFFF", "shadow": "0 5px 15px rgba(78, 205, 196, 0.4)", "shape": "capsule"},
        },
        "connector": {"color": "#A5A6F6", "style": "dashed", "thickness": "1.5px"},
        "font": "'Comfortaa', cursive",
        "icons": True
    },
    "tech": {
        "name": "Tech Blueprint",
        "node_styles": {
            "start": {"bg": "#3A0CA3", "text": "#FFFFFF", "shadow": "0 4px 8px rgba(58, 12, 163, 0.3)", "shape": "pill"},
            "process": {"bg": "#0F1724", "text": "#F8F9FA", "shadow": "0 3px 6px rgba(0,0,0,0.2)", "shape": "rectangle"},
            "decision": {"bg": "#4895EF", "text": "#FFFFFF", "shadow": "0 3px 6px rgba(72, 149, 239, 0.3)", "shape": "diamond"},
            "end": {"bg": "#4CC9F0", "text": "#FFFFFF", "shadow": "0 4px 8px rgba(76, 201, 240, 0.3)", "shape": "pill"},
        },
        "connector": {"color": "#4361EE", "style": "gradient", "thickness": "1.5px"},
        "font": "'IBM Plex Sans', sans-serif",
        "icons": True
    },
    "healthcare": {
        "name": "Healthcare",
        "node_styles": {
            "start": {"bg": "#00B4D8", "text": "#FFFFFF", "shadow": "0 3px 6px rgba(0, 180, 216, 0.3)", "shape": "rounded"},
            "process": {"bg": "#FFFFFF", "text": "#023E8A", "shadow": "0 2px 5px rgba(0,0,0,0.08)", "shape": "rounded"},
            "decision": {"bg": "#CAF0F8", "text": "#023E8A", "shadow": "0 2px 5px rgba(0,0,0,0.08)", "shape": "diamond"},
            "end": {"bg": "#0077B6", "text": "#FFFFFF", "shadow": "0 3px 6px rgba(0, 119, 182, 0.3)", "shape": "rounded"},
        },
        "connector": {"color": "#90E0EF", "style": "straight", "thickness": "1.5px"},
        "font": "'Quicksand', sans-serif",
        "icons": True
    },
    "finance": {
        "name": "Finance & Banking",
        "node_styles": {
            "start": {"bg": "#1B4332", "text": "#FFFFFF", "shadow": "0 3px 6px rgba(27, 67, 50, 0.3)", "shape": "rectangle"},
            "process": {"bg": "#FFFFFF", "text": "#081C15", "shadow": "0 2px 4px rgba(0,0,0,0.1)", "shape": "rectangle"},
            "decision": {"bg": "#D8F3DC", "text": "#081C15", "shadow": "0 2px 4px rgba(0,0,0,0.1)", "shape": "diamond"},
            "end": {"bg": "#2D6A4F", "text": "#FFFFFF", "shadow": "0 3px 6px rgba(45, 106, 79, 0.3)", "shape": "rectangle"},
        },
        "connector": {"color": "#95D5B2", "style": "straight", "thickness": "1.5px"},
        "font": "'Montserrat', sans-serif",
        "icons": True
    },
}

# Function to generate flowchart description using Mistral
def generate_flowchart_description(prompt, api_key, industry=None):
    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Create a prompt that instructs the model to generate a flowchart description
    industry_context = f"The flowchart is for the {industry} industry." if industry else ""
    
    system_message = f"""You are a flowchart designer specializing in creating detailed, professional flowcharts. {industry_context}
    Generate a detailed description of a flowchart based on the user's prompt.
    
    For each node in the flowchart, specify:
    1. Node ID (unique identifier)
    2. Node text content (keep it concise but clear)
    3. Node type (choose from: process, decision, start, end)
    4. Connections to other nodes (with IDs)
    5. An appropriate icon name that represents this step (use FontAwesome 5 icon names like fa-check, fa-user, fa-cog, etc.)
    6. Description - a detailed explanation including:
       - Purpose: What this step does and why it's important
       - Implementation: How this step is typically executed or implemented
       - Technical details: For programming flowcharts, include relevant code concepts, functions or methods
       - Best practices: Recommendations for this step
       - Common issues: Potential problems or edge cases to be aware of
    
    Format your response as JSON with this structure:
    {{
        "nodes": [
            {{
                "id": "node1", 
                "text": "Start Process", 
                "type": "start", 
                "connections": ["node2"], 
                "icon": "fa-play-circle", 
                "description": "Purpose: This is the entry point of the flowchart where execution begins. Implementation: Typically initializes variables and sets up the environment. Technical details: Often includes parameter validation and initial state configuration."
            }}
        ]
    }}
    
    IMPORTANT: Ensure the JSON is properly formatted with correct commas, quotes, and brackets. It must be valid JSON that can be parsed by Python's json.loads() function.
    """
    
    data = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"}  # Request JSON format specifically
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        
        # Extract the JSON content from the response
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Remove debug expander
        # First attempt: Try to parse the content directly as JSON
        try:
            flowchart_data = json.loads(content)
            # Validate basic structure
            if "nodes" not in flowchart_data:
                st.warning("Response didn't contain 'nodes' field. Adding default structure.")
                flowchart_data = {"nodes": [
                    {"id": "node1", "text": "Start", "type": "start", "connections": ["node2"], "icon": "fa-play-circle", 
                     "description": "Starting point of the process."},
                    {"id": "node2", "text": "End", "type": "end", "connections": [], "icon": "fa-flag-checkered", 
                     "description": "End of the process."}
                ]}
            return flowchart_data
            
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {str(e)}")
            
            # Second attempt: Clean up the content to extract JSON
            match = re.search(r'\{[\s\S]*"nodes"[\s\S]*\}', content)
            if match:
                try:
                    json_str = match.group(0)
                    # Fix common JSON errors
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    flowchart_data = json.loads(json_str)
                    st.success("Successfully parsed JSON after cleanup.")
                    return flowchart_data
                except json.JSONDecodeError as e2:
                    st.error(f"Failed to parse JSON after cleanup: {str(e2)}")
                    
            # Last resort: Create a minimal default flowchart
            st.warning("Creating a default flowchart structure")
            return {
                "nodes": [
                    {"id": "node1", "text": "Start", "type": "start", "connections": ["node2"], "icon": "fa-play-circle", 
                     "description": "Starting point of the process."},
                    {"id": "node2", "text": "Process", "type": "process", "connections": ["node3"], "icon": "fa-cog", 
                     "description": "Main processing step."},
                    {"id": "node3", "text": "End", "type": "end", "connections": [], "icon": "fa-flag-checkered", 
                     "description": "End of the process."}
                ]
            }
        
    except Exception as e:
        st.error(f"Error calling Mistral API: {str(e)}")
        st.info("Creating a default flowchart as fallback.")
        return {
            "nodes": [
                {"id": "node1", "text": "Start", "type": "start", "connections": ["node2"], "icon": "fa-play-circle", 
                 "description": "Starting point of the process."},
                {"id": "node2", "text": "Process", "type": "process", "connections": ["node3"], "icon": "fa-cog", 
                 "description": "Main processing step."},
                {"id": "node3", "text": "End", "type": "end", "connections": [], "icon": "fa-flag-checkered", 
                 "description": "End of the process."}
            ]
        }

# Helper function to create a default flowchart
def create_default_flowchart():
    logger.info("Creating default flowchart")
    return {
        "nodes": [
            {"id": "node1", "text": "Start", "type": "start", "connections": ["node2"], "icon": "fa-play-circle", 
             "description": "Starting point of the process."},
            {"id": "node2", "text": "Process", "type": "process", "connections": ["node3"], "icon": "fa-cog", 
             "description": "Main processing step."},
            {"id": "node3", "text": "End", "type": "end", "connections": [], "icon": "fa-flag-checkered", 
             "description": "End of the process."}
        ]
    }

# Function to calculate layout for nodes
def calculate_layout(nodes, orientation="landscape"):
    # Basic layout algorithm - arrange nodes in a tree-like structure
    node_map = {node["id"]: node for node in nodes}
    layout = []
    
    # Find start node (typically has no incoming connections)
    incoming_connections = set()
    for node in nodes:
        for conn in node.get("connections", []):
            incoming_connections.add(conn)
    
    start_nodes = [node for node in nodes if node["id"] not in incoming_connections]
    
    if not start_nodes:
        # If no clear start node, use the first node
        start_nodes = [nodes[0]]
    
    # Calculate positions using a simple hierarchical layout
    level_width = 300  # Increased from 200
    level_height = 200  # Increased from 150
    current_level = 0
    levels = {current_level: start_nodes}
    processed = set()
    
    # Track decision nodes for special handling
    decision_nodes = []
    
    while levels.get(current_level, []):
        level_nodes = levels[current_level]
        levels[current_level + 1] = []
        
        # Sort level nodes by their connections to minimize crossings
        if current_level > 0:
            level_nodes.sort(key=lambda n: sorted(n.get("connections", [])))
        
        for i, node in enumerate(level_nodes):
            # Skip if already processed
            if node["id"] in processed:
                continue
                
            processed.add(node["id"])
            
            # Calculate position based on orientation
            x = 0
            y = 0
            if orientation == "landscape":
                x = 50 + (1000 / (len(level_nodes) + 1)) * (i + 1) - 60
                y = 50 + current_level * level_height
            else:  # portrait
                x = 50 + current_level * level_width
                y = 50 + (800 / (len(level_nodes) + 1)) * (i + 1) - 60
            
            layout.append({
                "node": node,
                "x": x,
                "y": y,
                "width": 120,  # Standard node width
                "height": 80   # Standard node height
            })
            
            # Track decision nodes
            if node["type"] == "decision":
                decision_nodes.append(node["id"])
            
            # Add connected nodes to the next level
            for conn_id in node.get("connections", []):
                if conn_id not in processed and conn_id in node_map:
                    levels[current_level + 1].append(node_map[conn_id])
        
        current_level += 1
    
    return layout

# Function to calculate connector points at node borders
def calculate_connector_points(source_node, target_node):
    # Get node positions and dimensions
    source_x = source_node["x"]
    source_y = source_node["y"]
    target_x = target_node["x"]
    target_y = target_node["y"]
    
    # Node dimensions
    source_width = source_node["width"]
    source_height = source_node["height"]
    target_width = target_node["width"]
    target_height = target_node["height"]
    
    # Calculate center points
    source_center_x = source_x + source_width / 2
    source_center_y = source_y + source_height / 2
    target_center_x = target_x + target_width / 2
    target_center_y = target_y + target_height / 2
    
    # Calculate angle between centers
    angle = math.atan2(target_center_y - source_center_y, target_center_x - source_center_x)
    
    # Calculate intersection points with node borders
    # For source node
    if abs(math.cos(angle)) > abs(math.sin(angle)):
        # Horizontal intersection
        if target_center_x > source_center_x:
            source_point_x = source_x + source_width
        else:
            source_point_x = source_x
        source_point_y = source_center_y
    else:
        # Vertical intersection
        if target_center_y > source_center_y:
            source_point_y = source_y + source_height
        else:
            source_point_y = source_y
        source_point_x = source_center_x
    
    # For target node
    if abs(math.cos(angle)) > abs(math.sin(angle)):
        # Horizontal intersection
        if target_center_x > source_center_x:
            target_point_x = target_x
        else:
            target_point_x = target_x + target_width
        target_point_y = target_center_y
    else:
        # Vertical intersection
        if target_center_y > source_center_y:
            target_point_y = target_y
        else:
            target_point_y = target_y + target_height
        target_point_x = target_center_x
    
    # Adjust for decision nodes
    if source_node["node"]["type"] == "decision":
        # Adjust the source point for diamond shape
        # Calculate based on angle to determine which point of the diamond to use
        diagonal_angle = math.atan2(target_center_y - source_center_y, target_center_x - source_center_x)
        diagonal_deg = math.degrees(diagonal_angle) % 360
        
        if diagonal_deg >= 315 or diagonal_deg < 45:  # Right point
            source_point_x = source_center_x + source_width / 2
            source_point_y = source_center_y
        elif diagonal_deg >= 45 and diagonal_deg < 135:  # Bottom point
            source_point_x = source_center_x
            source_point_y = source_center_y + source_height / 2
        elif diagonal_deg >= 135 and diagonal_deg < 225:  # Left point
            source_point_x = source_center_x - source_width / 2
            source_point_y = source_center_y
        else:  # Top point (225-315)
            source_point_x = source_center_x
            source_point_y = source_center_y - source_height / 2
    
    if target_node["node"]["type"] == "decision":
        # Adjust the target point for diamond shape
        # Calculate based on angle to determine which point of the diamond to use
        diagonal_angle = math.atan2(target_center_y - source_center_y, target_center_x - source_center_x)
        diagonal_deg = math.degrees(diagonal_angle) % 360
        
        if diagonal_deg >= 315 or diagonal_deg < 45:  # Right point (coming from left)
            target_point_x = target_center_x - target_width / 2
            target_point_y = target_center_y
        elif diagonal_deg >= 45 and diagonal_deg < 135:  # Bottom point (coming from top)
            target_point_x = target_center_x
            target_point_y = target_center_y - target_height / 2
        elif diagonal_deg >= 135 and diagonal_deg < 225:  # Left point (coming from right)
            target_point_x = target_center_x + target_width / 2
            target_point_y = target_center_y
        else:  # Top point (coming from bottom) (225-315)
            target_point_x = target_center_x
            target_point_y = target_center_y + target_height / 2
    
    return source_point_x, source_point_y, target_point_x, target_point_y

# Helper function to generate CSS for connectors based on theme and style
def generate_connector_css(theme, source_x, source_y, target_x, target_y, angle, length):
    style = theme["connector"]["style"]
    color = theme["connector"]["color"]
    thickness = theme["connector"]["thickness"]
    
    css = f"left: {source_x}px; top: {source_y}px; width: {length}px; transform: rotate({angle}deg); transform-origin: 0 0;"
    
    if style == "straight":
        return f"background-color: {color}; height: {thickness}; {css}"
    elif style == "dashed":
        return f"background-color: {color}; height: {thickness}; border-top-style: dashed; {css}"
    elif style == "curved":
        # For curved, we'll still use straight but add a different class
        return f"background-color: {color}; height: {thickness}; {css}"
    elif style == "gradient":
        return f"background: linear-gradient(90deg, {color}, {color}FF); height: {thickness}; {css}"
    else:
        return f"background-color: {color}; height: {thickness}; {css}"

# Helper function to get shape CSS based on node type and theme
def get_node_shape_css(node_type, theme):
    shape = theme["node_styles"][node_type]["shape"]
    
    if shape == "rounded":
        return "border-radius: 8px;"
    elif shape == "rectangle":
        return "border-radius: 2px;"
    elif shape == "diamond":
        return "transform: rotate(45deg); width: 120px; height: 120px;"
    elif shape == "pill" or shape == "capsule":
        return "border-radius: 50px;"
    else:
        return "border-radius: 8px;"  # Default

# Function to get Font Awesome icon for node type
def get_icon_for_node(node):
    # Check if node has a custom icon
    if "icon" in node and node["icon"]:
        # Make sure it has the fa- prefix
        if not node["icon"].startswith("fa-"):
            return f"fa-{node['icon']}"
        return node["icon"]
    
    # Default icons based on node type
    default_icons = {
        "start": "fa-play-circle",
        "process": "fa-cog",
        "decision": "fa-question-circle",
        "end": "fa-flag-checkered"
    }
    
    return default_icons.get(node["type"], "fa-circle")

# Function to generate HTML/CSS for the flowchart
def generate_flowchart_html(flowchart_data, theme_key, orientation="landscape", zoom_level=1.0):
    # Generate unique IDs for this flowchart
    chart_id = f"flowchart-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get the selected theme
    theme = DESIGN_THEMES[theme_key]
    
    # CSS for the flowchart
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&family=Open+Sans:wght@400;600&family=Comfortaa:wght@400;700&family=IBM+Plex+Sans:wght@400;500&family=Quicksand:wght@500;600&family=Montserrat:wght@400;500&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
        
        #{chart_id} {{
            font-family: {theme["font"]};
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            overflow: hidden;
            background-color: white;
            border-radius: 12px;
            min-height: 700px;
            position: relative;
            transition: background-color 0.3s ease;
        }}
        
        #{chart_id}.dark-mode {{
            background-color: #1a1a1a;
        }}
        
        #{chart_id} .flowchart-container {{
            position: relative;
            background-color: transparent;
            border-radius: 12px;
            padding: 20px;
            transform-origin: center center;
            transform: scale({zoom_level}) translate(0px, 0px);
            transition: transform 0.3s ease;
            margin: auto;
        }}
        
        #{chart_id} .controls {{
            position: fixed;
            bottom: 15px;
            right: 15px;
            z-index: 1000;
            background: white;
            padding: 3px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            display: flex;
            gap: 3px;
            align-items: center;
            transition: background-color 0.3s ease;
        }}
        
        #{chart_id}.dark-mode .controls {{
            background: #2d2d2d;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        #{chart_id} .navigation-controls {{
            position: fixed;
            left: 15px;
            bottom: 15px;
            z-index: 1000;
            background: white;
            padding: 3px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1px;
            transition: background-color 0.3s ease;
        }}
        
        #{chart_id}.dark-mode .navigation-controls {{
            background: #2d2d2d;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        #{chart_id} .controls button,
        #{chart_id} .navigation-controls button {{
            background: {theme["node_styles"]["process"]["bg"]};
            color: {theme["node_styles"]["process"]["text"]};
            border: none;
            padding: 3px 6px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 24px;
            min-height: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        #{chart_id}.dark-mode .controls button,
        #{chart_id}.dark-mode .navigation-controls button {{
            background: #3d3d3d;
            color: #ffffff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }}
        
        #{chart_id} .controls button:hover,
        #{chart_id} .navigation-controls button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        #{chart_id}.dark-mode .controls button:hover,
        #{chart_id}.dark-mode .navigation-controls button:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        }}
        
        #{chart_id} .controls .reset-btn:hover,
        #{chart_id} .navigation-controls .reset-btn:hover {{
            background: {theme["node_styles"]["start"]["bg"]}DD;
        }}
        
        #{chart_id}.dark-mode .controls .reset-btn:hover,
        #{chart_id}.dark-mode .navigation-controls .reset-btn:hover {{
            background: #4a4a4a;
            color: #ffffff;
        }}
        
        #{chart_id} .navigation-controls .up-btn {{
            grid-column: 2;
        }}
        
        #{chart_id} .navigation-controls .left-btn {{
            grid-column: 1;
            grid-row: 2;
        }}
        
        #{chart_id} .navigation-controls .center-btn {{
            grid-column: 2;
            grid-row: 2;
        }}
        
        #{chart_id} .navigation-controls .right-btn {{
            grid-column: 3;
            grid-row: 2;
        }}
        
        #{chart_id} .navigation-controls .down-btn {{
            grid-column: 2;
            grid-row: 3;
        }}
        
        #{chart_id} .controls .zoom-level {{
            background: {theme["node_styles"]["process"]["bg"]};
            color: {theme["node_styles"]["process"]["text"]};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            min-width: 50px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        #{chart_id}.dark-mode .controls .zoom-level {{
            background: #3d3d3d;
            color: #ffffff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }}
        
        #{chart_id} .controls .theme-toggle {{
            background: #f0f0f0;
            color: #333;
        }}
        
        #{chart_id}.dark-mode .controls .theme-toggle {{
            background: #4a4a4a;
            color: #fff;
        }}
        
        #{chart_id} .node {{
            position: absolute;
            padding: 15px;
            min-width: 120px;
            text-align: center;
            font-weight: 500;
            font-size: 14px;
            z-index: 3;
            transition: transform 0.1s, box-shadow 0.1s;
            border: 2px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            cursor: move;
            user-select: none;
            touch-action: none;
        }}
        
        #{chart_id} .node.dragging {{
            opacity: 0.8;
            z-index: 1000;
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }}
        
        #{chart_id}.dark-mode .node {{
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        
        #{chart_id} .node:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
            border-color: rgba(0, 0, 0, 0.2);
        }}
        
        #{chart_id}.dark-mode .node:hover {{
            box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
        }}
        
        #{chart_id} .node-start {{
            background-color: {theme["node_styles"]["start"]["bg"]};
            color: {theme["node_styles"]["start"]["text"]};
            box-shadow: {theme["node_styles"]["start"]["shadow"]};
            {get_node_shape_css("start", theme)}
            border-color: {theme["node_styles"]["start"]["bg"]}CC;
        }}
        
        #{chart_id} .node-end {{
            background-color: {theme["node_styles"]["end"]["bg"]};
            color: {theme["node_styles"]["end"]["text"]};
            box-shadow: {theme["node_styles"]["end"]["shadow"]};
            {get_node_shape_css("end", theme)}
            border-color: {theme["node_styles"]["end"]["bg"]}CC;
        }}
        
        #{chart_id} .node-process {{
            background-color: {theme["node_styles"]["process"]["bg"]};
            color: {theme["node_styles"]["process"]["text"]};
            box-shadow: {theme["node_styles"]["process"]["shadow"]};
            {get_node_shape_css("process", theme)}
            border-color: {theme["node_styles"]["process"]["bg"]}CC;
        }}
        
        #{chart_id} .node-decision {{
            background-color: {theme["node_styles"]["decision"]["bg"]};
            color: {theme["node_styles"]["decision"]["text"]};
            box-shadow: {theme["node_styles"]["decision"]["shadow"]};
            {get_node_shape_css("decision", theme)}
            display: flex;
            align-items: center;
            justify-content: center;
            transform: rotate(45deg);
            border-color: {theme["node_styles"]["decision"]["bg"]}CC;
            min-width: 120px;
            min-height: 120px;
            max-width: 120px;
            max-height: 120px;
        }}
        
        #{chart_id} .node-decision:hover {{
            transform: rotate(45deg) translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15) !important;
            border-color: {theme["node_styles"]["decision"]["bg"]}EE;
        }}
        
        #{chart_id}.dark-mode .node-decision:hover {{
            box-shadow: 0 8px 15px rgba(0,0,0,0.4) !important;
        }}
        
        #{chart_id} .node-decision .content {{
            transform: rotate(-45deg);
            width: 130px;
            height: 130px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 5px;
            font-size: 0.95em;
        }}
        
        #{chart_id} .node-decision .icon {{
            margin-bottom: 5px;
            font-size: 22px;
        }}
        
        #{chart_id} .connector {{
            position: absolute;
            height: {theme["connector"]["thickness"]};
            z-index: 2;
            pointer-events: none;
        }}
        
        #{chart_id} .connector-line {{
            position: absolute;
            height: {theme["connector"]["thickness"]};
            z-index: 2;
            pointer-events: all;
            cursor: pointer;
            background-color: transparent;
        }}
        
       
        
        #{chart_id} .connector.curved:after {{
            right: 50%;
            top: -5px;
            border-width: 6px 0 6px 10px;
            border-color: transparent transparent transparent green;
            z-index: 5;
        }}
        
        #{chart_id} .connector.dashed:after {{
            border-style: dashed;
            border-width: 5px 0 5px 8px;
            right: 50%;
            border-color: transparent transparent transparent green;
            z-index: 5;
        }}
         #{chart_id} .connector:after {{
            content: '';
            position: absolute;
            right: 5%;
            top: -4px;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 5px 0 5px 8px;
            border-color: transparent transparent transparent green;
            z-index: 5;
        }}
        #{chart_id} .connector.gradient:after {{
            border-color: transparent transparent transparent green;
            right: 50%;
            z-index: 5;
        }}
        
        #{chart_id} .label {{
            position: absolute;
            background-color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            z-index: 4;
            border: 1px solid rgba(0,0,0,0.1);
            transform: translate(-50%, -50%);
            white-space: nowrap;
            cursor: move;
            user-select: none;
            touch-action: none;
        }}
        
        #{chart_id}.dark-mode .label {{
            background-color: #2d2d2d;
            color: white;
            border-color: rgba(255,255,255,0.1);
        }}
        
        #{chart_id} .label.dragging {{
            opacity: 0.8;
            z-index: 1000;
        }}
        
        #{chart_id} .label.yes {{
            background-color: #4CAF50;
            color: white;
            border: none;
        }}
        
        #{chart_id} .label.no {{
            background-color: #f44336;
            color: white;
            border: none;
        }}
        
        #{chart_id}.dark-mode .label.yes {{
            background-color: #2E7D32;
        }}
        
        #{chart_id}.dark-mode .label.no {{
            background-color: #C62828;
        }}
        
        #{chart_id} .icon {{
            display: block;
            margin-bottom: 8px;
            font-size: 24px;
        }}
        
        /* Tooltip styles */
        #{chart_id} .tooltip {{
            position: absolute;
            background-color: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 12px 15px;
            border-radius: 6px;
            font-size: 12px;
            z-index: 1000;
            max-width: 320px;
            min-width: 180px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            visibility: hidden;
            word-wrap: break-word;
            line-height: 1.4;
        }}
        
        #{chart_id} .tooltip.visible {{
            opacity: 1;
            visibility: visible;
        }}
        
        #{chart_id}.dark-mode .tooltip {{
            background-color: rgba(40, 40, 40, 0.95);
            color: #f0f0f0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        }}
    </style>
    """
    
    # Calculate layout based on orientation
    layout = calculate_layout(flowchart_data["nodes"], orientation)
    
    # Set container dimensions based on orientation
    container_width = 900 if orientation == "landscape" else 650
    container_height = 650 if orientation == "landscape" else 900
    
    # Generate HTML for nodes and connections
    nodes_html = ""
    connections_html = ""
    
    # First generate all nodes
    for node_info in layout:
        node = node_info["node"]
        x = node_info["x"]
        y = node_info["y"]
        
        # Get icon for this node
        icon = get_icon_for_node(node)
        icon_html = f'<i class="icon fas {icon}"></i>' if theme["icons"] else ''
        
        # Get description for tooltip if available
        description = node.get("description", "")
        description_attr = f'data-description="{description}"' if description else ''
        
        # Different styling based on node type
        if node["type"] == "decision":
            nodes_html += f"""
            <div id="{node['id']}" class="node node-{node['type']}" style="left: {x}px; top: {y}px;" {description_attr}>
                <div class="content">
                    {icon_html}
                    {node['text']}
                </div>
            </div>
            """
        else:
            nodes_html += f"""
            <div id="{node['id']}" class="node node-{node['type']}" style="left: {x}px; top: {y}px;" {description_attr}>
                {icon_html}
                {node['text']}
            </div>
            """
    
    # Then generate all connections
    for source_info in layout:
        source_node = source_info["node"]
        
        for target_id in source_node.get("connections", []):
            # Find target node info
            target_info = next((n for n in layout if n["node"]["id"] == target_id), None)
            if target_info:
                # Calculate connector points at node borders
                source_x, source_y, target_x, target_y = calculate_connector_points(source_info, target_info)
                
                # Calculate distance and angle for the connector
                dx = target_x - source_x
                dy = target_y - source_y
                length = (dx**2 + dy**2)**0.5
                angle = math.atan2(dy, dx) * (180 / math.pi)
                
                # Generate connection HTML with arrow
                conn_id = f"conn-{source_node['id']}-{target_id}"
                connector_style = generate_connector_css(theme, source_x, source_y, target_x, target_y, angle, length)
                connector_class = f"connector {theme['connector']['style']}"
                
                connections_html += f"""
                <div id="{conn_id}" class="{connector_class}" style="{connector_style}"></div>
                <div id="line-{conn_id}" class="connector-line" style="{connector_style}"></div>
                """
                
                # Add labels for decision paths if node is a decision
                if source_node["type"] == "decision":
                    # Calculate label position
                    midx = source_x + (dx / 2)
                    midy = source_y + (dy / 2)
                    
                    # Determine label text based on connection order
                    label_text = "Yes" if source_node["connections"].index(target_id) == 0 else "No"
                    label_class = "yes" if label_text == "Yes" else "no"
                    
                    connections_html += f"""
                    <div class="label {label_class}" id="label-{source_node['id']}-{target_id}" 
                         data-connector-id="{conn_id}" 
                         data-source-id="{source_node['id']}" 
                         data-target-id="{target_id}"
                         style="left: {midx}px; top: {midy}px;">{label_text}</div>
                    """
    
    # Add zoom controls with improved styling
    controls_html = f"""
    <div class="controls">
        <button class="theme-toggle" onclick="toggleTheme()">
            <i class="fas fa-moon"></i>
        </button>
        <button class="reset-btn" onclick="resetZoom()">
            <i class="fas fa-sync-alt"></i>
        </button>
        <button onclick="zoomOut()">
            <i class="fas fa-search-minus"></i>
        </button>
        <div class="zoom-level">{int(zoom_level * 100)}%</div>
        <button onclick="zoomIn()">
            <i class="fas fa-search-plus"></i>
        </button>
        <button class="reset-layout-btn" onclick="resetLayout()">
            <i class="fas fa-undo"></i>
        </button>
    </div>
    
    <div class="navigation-controls">
        <button class="up-btn" onclick="moveUp()">
            <i class="fas fa-arrow-up"></i>
        </button>
        <button class="left-btn" onclick="moveLeft()">
            <i class="fas fa-arrow-left"></i>
        </button>
        <button class="center-btn reset-btn" onclick="resetPosition()">
            <i class="fas fa-crosshairs"></i>
        </button>
        <button class="right-btn" onclick="moveRight()">
            <i class="fas fa-arrow-right"></i>
        </button>
        <button class="down-btn" onclick="moveDown()">
            <i class="fas fa-arrow-down"></i>
        </button>
    </div>
    
    <div id="{chart_id}-tooltip" class="tooltip"></div>
    
    <script>
        let currentX = 0;
        let currentY = 0;
        const moveStep = 50;
        let currentScale = {zoom_level};
        let isDarkMode = false;
        
        function toggleTheme() {{
            const container = document.getElementById('{chart_id}');
            const themeToggle = container.querySelector('.theme-toggle i');
            
            isDarkMode = !isDarkMode;
            container.classList.toggle('dark-mode');
            
            if (isDarkMode) {{
                themeToggle.classList.remove('fa-moon');
                themeToggle.classList.add('fa-sun');
            }} else {{
                themeToggle.classList.remove('fa-sun');
                themeToggle.classList.add('fa-moon');
            }}
        }}
        
        function getCurrentTransform() {{
            const container = document.getElementById('{chart_id}').querySelector('.flowchart-container');
            const transform = container.style.transform;
            const scaleMatch = transform.match(/scale\(([^)]+)\)/);
            const translateMatch = transform.match(/translate\(([^)]+)\)/);
            
            return {{
                scale: scaleMatch ? parseFloat(scaleMatch[1]) : currentScale,
                translate: translateMatch ? translateMatch[1].split(',').map(Number) : [currentX, currentY]
            }};
        }}
        
        function updateTransform() {{
            const container = document.getElementById('{chart_id}').querySelector('.flowchart-container');
            container.style.transform = `scale(${{currentScale}}) translate(${{currentX}}px, ${{currentY}}px)`;
        }}
        
        function moveUp() {{
            currentY += moveStep;
            updateTransform();
        }}
        
        function moveDown() {{
            currentY -= moveStep;
            updateTransform();
        }}
        
        function moveLeft() {{
            currentX += moveStep;
            updateTransform();
        }}
        
        function moveRight() {{
            currentX -= moveStep;
            updateTransform();
        }}
        
        function resetPosition() {{
            currentX = 0;
            currentY = 0;
            updateTransform();
        }}
        
        function zoomIn() {{
            if (currentScale < 2.0) {{
                currentScale += 0.1;
                updateTransform();
                updateZoomLevel();
            }}
        }}
        
        function zoomOut() {{
            if (currentScale > 0.5) {{
                currentScale -= 0.1;
                updateTransform();
                updateZoomLevel();
            }}
        }}
        
        function resetZoom() {{
            currentScale = 1.0;
            updateTransform();
            updateZoomLevel();
        }}
        
        function updateZoomLevel() {{
            const zoomLevel = document.getElementById('{chart_id}').querySelector('.zoom-level');
            zoomLevel.textContent = Math.round(currentScale * 100) + '%';
        }}
        
        // Dragging functionality
        let isDragging = false;
        let currentNode = null;
        let offsetX = 0;
        let offsetY = 0;
        let nodePositions = new Map();
        
        // Store initial positions
        function initializeNodePositions() {{
            const nodes = document.querySelectorAll('#{chart_id} .node');
            nodes.forEach(node => {{
                nodePositions.set(node.id, {{
                    x: parseInt(node.style.left),
                    y: parseInt(node.style.top),
                    width: node.offsetWidth,
                    height: node.offsetHeight
                }});
            }});
        }}
        
        // Store initial positions for reset functionality
        let initialNodePositions = new Map();
        
        // Initialize after DOM loads
        document.addEventListener('DOMContentLoaded', () => {{
            initializeNodePositions();
            // Store initial positions for reset
            const nodes = document.querySelectorAll('#{chart_id} .node');
            nodes.forEach(node => {{
                initialNodePositions.set(node.id, {{
                    x: parseInt(node.style.left),
                    y: parseInt(node.style.top),
                    width: node.offsetWidth,
                    height: node.offsetHeight
                }});
            }});
        }});
        
        // Reset layout to original positions
        function resetLayout() {{
            const nodes = document.querySelectorAll('#{chart_id} .node');
            nodes.forEach(node => {{
                const initialPos = initialNodePositions.get(node.id);
                if (initialPos) {{
                    node.style.left = `${{initialPos.x}}px`;
                    node.style.top = `${{initialPos.y}}px`;
                    nodePositions.set(node.id, initialPos);
                }}
            }});
            
            // Reset zoom and position
            currentScale = 1.0;
            currentX = 0;
            currentY = 0;
            updateTransform();
            updateZoomLevel();
            
            // Update connectors
            updateConnectors();
        }}
        
        // Calculate connector points
        function calculateConnectorPoints(source, target, isSourceDecision, isTargetDecision) {{
            const sourceCenter = {{
                x: source.x + source.width / 2,
                y: source.y + source.height / 2
            }};
            const targetCenter = {{
                x: target.x + target.width / 2,
                y: target.y + target.height / 2
            }};
            
            let sourcePoint, targetPoint;
            
            if (isSourceDecision) {{
                // Calculate angle to determine which point of the diamond to use
                const angle = Math.atan2(targetCenter.y - sourceCenter.y, targetCenter.x - sourceCenter.x);
                const degrees = angle * (180 / Math.PI);
                const normalizedDegrees = ((degrees % 360) + 360) % 360;
                
                if (normalizedDegrees >= 315 || normalizedDegrees < 45) {{  // Right point
                    sourcePoint = {{
                        x: sourceCenter.x + source.width / 2,
                        y: sourceCenter.y
                    }};
                }} else if (normalizedDegrees >= 45 && normalizedDegrees < 135) {{  // Bottom point
                sourcePoint = {{
                    x: sourceCenter.x,
                    y: sourceCenter.y + source.height / 2
                }};
                }} else if (normalizedDegrees >= 135 && normalizedDegrees < 225) {{  // Left point
                    sourcePoint = {{
                        x: sourceCenter.x - source.width / 2,
                        y: sourceCenter.y
                    }};
                }} else {{  // Top point (225-315)
                    sourcePoint = {{
                        x: sourceCenter.x,
                        y: sourceCenter.y - source.height / 2
                    }};
                }}
            }} else {{
                // Calculate border intersection for regular nodes
                sourcePoint = calculateBorderIntersection(sourceCenter, targetCenter, source);
            }}
            
            if (isTargetDecision) {{
                // Calculate angle to determine which point of the diamond to use
                const angle = Math.atan2(targetCenter.y - sourceCenter.y, targetCenter.x - sourceCenter.x);
                const degrees = angle * (180 / Math.PI);
                const normalizedDegrees = ((degrees % 360) + 360) % 360;
                
                if (normalizedDegrees >= 315 || normalizedDegrees < 45) {{  // Right point (coming from left)
                    targetPoint = {{
                        x: targetCenter.x - target.width / 2,
                        y: targetCenter.y
                    }};
                }} else if (normalizedDegrees >= 45 && normalizedDegrees < 135) {{  // Bottom point (coming from top)
                targetPoint = {{
                    x: targetCenter.x,
                    y: targetCenter.y - target.height / 2
                }};
                }} else if (normalizedDegrees >= 135 && normalizedDegrees < 225) {{  // Left point (coming from right)
                    targetPoint = {{
                        x: targetCenter.x + target.width / 2,
                        y: targetCenter.y
                    }};
                }} else {{  // Top point (coming from bottom) (225-315)
                    targetPoint = {{
                        x: targetCenter.x,
                        y: targetCenter.y + target.height / 2
                    }};
                }}
            }} else {{
                // Calculate border intersection for regular nodes
                targetPoint = calculateBorderIntersection(targetCenter, sourceCenter, target);
            }}
            
            return [sourcePoint.x, sourcePoint.y, targetPoint.x, targetPoint.y];
        }}
        
        // Calculate intersection point with node border
        function calculateBorderIntersection(from, to, node) {{
            const angle = Math.atan2(to.y - from.y, to.x - from.x);
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);
            
            // Determine intersection point
            let x, y;
            if (Math.abs(cos) > Math.abs(sin)) {{
                // Intersect with left or right border
                x = cos > 0 ? node.x + node.width : node.x;
                y = from.y + (x - from.x) * sin / cos;
            }} else {{
                // Intersect with top or bottom border
                y = sin > 0 ? node.y + node.height : node.y;
                x = from.x + (y - from.y) * cos / sin;
            }}
            
            return {{ x, y }};
        }}
        
        // Update connector positions
        function updateConnectors() {{
            const container = document.getElementById('{chart_id}');
            const connectors = container.querySelectorAll('.connector');
            
            connectors.forEach(connector => {{
                const [_, sourceId, targetId] = connector.id.split('-');
                const sourceNode = document.getElementById(sourceId);
                const targetNode = document.getElementById(targetId);
                
                if (sourceNode && targetNode) {{
                    const sourcePos = nodePositions.get(sourceId);
                    const targetPos = nodePositions.get(targetId);
                    
                    if (sourcePos && targetPos) {{
                        // Calculate new connector points
                        const [sx, sy, tx, ty] = calculateConnectorPoints(
                            sourcePos,
                            targetPos,
                            sourceNode.classList.contains('node-decision'),
                            targetNode.classList.contains('node-decision')
                        );
                        
                        // Calculate new angle and length
                        const dx = tx - sx;
                        const dy = ty - sy;
                        const length = Math.sqrt(dx * dx + dy * dy);
                        const angle = Math.atan2(dy, dx) * (180 / Math.PI);
                        
                        // Update connector position and rotation
                        connector.style.left = `${{sx}}px`;
                        connector.style.top = `${{sy}}px`;
                        connector.style.width = `${{length}}px`;
                        connector.style.transform = `rotate(${{angle}}deg)`;
                        
                        // Update the invisible line for label dragging
                        const lineId = `line-${{connector.id}}`;
                        const line = document.getElementById(lineId);
                        if (line) {{
                            line.style.left = `${{sx}}px`;
                            line.style.top = `${{sy}}px`;
                            line.style.width = `${{length}}px`;
                            line.style.transform = `rotate(${{angle}}deg)`;
                        }}
                        
                        // Update decision labels if needed
                        if (sourceNode.classList.contains('node-decision')) {{
                            const labelId = `label-${{sourceId}}-${{targetId}}`;
                            const label = document.querySelector(`#${{labelId}}`);
                            if (label && !label.classList.contains('dragging')) {{
                                // Only update if not being dragged
                                const position = parseFloat(label.dataset.position || '0.5');
                                label.style.left = `${{sx + dx * position}}px`;
                                label.style.top = `${{sy + dy * position}}px`;
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Add label dragging functionality
        let isLabelDragging = false;
        let currentLabel = null;
        let currentLine = null;
        
        // Enhanced mouse event handlers
        document.addEventListener('mousedown', e => {{
            const label = e.target.closest('.label');
            if (label) {{
                isLabelDragging = true;
                currentLabel = label;
                currentLine = document.getElementById(`line-${{label.dataset.connectorId}}`);
                label.classList.add('dragging');
                e.preventDefault();
            }} else {{
                const node = e.target.closest('#{chart_id} .node');
                if (node) {{
                    isDragging = true;
                    currentNode = node;
                    const rect = node.getBoundingClientRect();
                    offsetX = e.clientX - rect.left;
                    offsetY = e.clientY - rect.top;
                    node.classList.add('dragging');
                    e.preventDefault();
                }}
            }}
        }}, true);
        
        document.addEventListener('mousemove', e => {{
            if (isLabelDragging && currentLabel && currentLine) {{
                const lineRect = currentLine.getBoundingClientRect();
                const containerRect = document.getElementById('{chart_id}').getBoundingClientRect();
                
                // Calculate position along the line
                const lineLength = Math.sqrt(
                    Math.pow(lineRect.width, 2) + Math.pow(lineRect.height, 2)
                );
                
                // Get mouse position relative to the line
                const mouseX = e.clientX - containerRect.left;
                const mouseY = e.clientY - containerRect.top;
                
                // Project mouse position onto the line
                const lineStartX = parseFloat(currentLine.style.left);
                const lineStartY = parseFloat(currentLine.style.top);
                const lineEndX = lineStartX + lineRect.width * Math.cos(parseFloat(currentLine.style.transform.match(/rotate\(([^)]+)\)/)[1]) * Math.PI / 180);
                const lineEndY = lineStartY + lineRect.width * Math.sin(parseFloat(currentLine.style.transform.match(/rotate\(([^)]+)\)/)[1]) * Math.PI / 180);
                
                // Calculate position along the line (0 to 1)
                const position = Math.max(0, Math.min(1, 
                    ((mouseX - lineStartX) * (lineEndX - lineStartX) + 
                     (mouseY - lineStartY) * (lineEndY - lineStartY)) / 
                    (lineLength * lineLength)
                ));
                
                // Update label position
                currentLabel.style.left = `${{lineStartX + (lineEndX - lineStartX) * position}}px`;
                currentLabel.style.top = `${{lineStartY + (lineEndY - lineStartY) * position}}px`;
                
                // Store position for later updates
                currentLabel.dataset.position = position;
            }} else if (isDragging && currentNode) {{
                // Get mouse position relative to the container
                const container = document.getElementById('{chart_id}');
                const containerRect = container.getBoundingClientRect();
                const mouseX = e.clientX - containerRect.left;
                const mouseY = e.clientY - containerRect.top;
                
                // Update node position directly
                currentNode.style.left = `${{mouseX - offsetX}}px`;
                currentNode.style.top = `${{mouseY - offsetY}}px`;
                
                // Update stored position
                nodePositions.set(currentNode.id, {{
                    x: mouseX - offsetX,
                    y: mouseY - offsetY,
                    width: currentNode.offsetWidth,
                    height: currentNode.offsetHeight
                }});
                
                // Update connectors
                updateConnectors();
            }}
        }}, true);
        
        document.addEventListener('mouseup', () => {{
            if (currentLabel) {{
                currentLabel.classList.remove('dragging');
                currentLabel = null;
                currentLine = null;
            }}
            if (currentNode) {{
                currentNode.classList.remove('dragging');
            }}
            isLabelDragging = false;
            isDragging = false;
            currentNode = null;
        }}, true);
        
        // Add touch event support
        document.addEventListener('touchstart', e => {{
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {{
                clientX: touch.clientX,
                clientY: touch.clientY
            }});
            document.dispatchEvent(mouseEvent);
        }});
        
        document.addEventListener('touchmove', e => {{
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {{
                clientX: touch.clientX,
                clientY: touch.clientY
            }});
            document.dispatchEvent(mouseEvent);
        }});
        
        document.addEventListener('touchend', () => {{
            const mouseEvent = new MouseEvent('mouseup');
            document.dispatchEvent(mouseEvent);
        }});

        // Add tooltip functionality for nodes
        const tooltip = document.getElementById('{chart_id}-tooltip');
        
        document.addEventListener('DOMContentLoaded', () => {{
            const nodes = document.querySelectorAll('#{chart_id} .node');
            
            nodes.forEach(node => {{
                const description = node.getAttribute('data-description');
                if (description) {{
                    node.addEventListener('mouseenter', (e) => {{
                        // Format description with HTML for better readability
                        let formattedDesc = description;
                        
                        // Look for key terms to format
                        const keyTermsList = ["Purpose:", "Implementation:", "Technical details:", "Best practices:", "Common issues:"];
                        
                        // Create styled HTML
                        let htmlContent = `<div class="tooltip-content">`;
                        
                        // Add node title
                        htmlContent += `<div class="tooltip-title">${{node.textContent.trim()}}</div>`;
                        
                        // Split description into paragraphs for better readability
                        const paragraphs = formattedDesc.split(/(?=Purpose:|Implementation:|Technical details:|Best practices:|Common issues:)/g);
                        
                        // Add formatted description with paragraphs
                        htmlContent += `<div class="tooltip-description">`;
                        paragraphs.forEach(para => {{
                            if (para.trim()) {{
                                let formattedPara = para;
                                
                                // Add styling to headings
                                keyTermsList.forEach(term => {{
                                    if (formattedPara.startsWith(term)) {{
                                        formattedPara = formattedPara.replace(term, `<span class="tooltip-heading">${{term}}</span>`);
                                    }}
                                }});
                                
                                htmlContent += `<p class="tooltip-paragraph">${{formattedPara}}</p>`;
                            }}
                        }});
                        htmlContent += `</div>`;
                        
                        
                        htmlContent += `</div>`;
                        
                        // Set the HTML content
                        tooltip.innerHTML = htmlContent;
                        tooltip.classList.add('visible');
                        
                        // Position the tooltip near the node
                        const rect = node.getBoundingClientRect();
                        const chartRect = document.getElementById('{chart_id}').getBoundingClientRect();
                        
                        // Calculate position - above the node
                        let top = rect.top - chartRect.top - tooltip.offsetHeight - 10;
                        let left = rect.left - chartRect.left + (rect.width / 2) - (tooltip.offsetWidth / 2);
                        
                        // Adjust if tooltip would go off the chart
                        if (top < 0) {{
                            // Place below instead
                            top = rect.bottom - chartRect.top + 10;
                        }}
                        
                        if (left < 10) {{
                            left = 10;
                        }} else if (left + tooltip.offsetWidth > chartRect.width - 10) {{
                            left = chartRect.width - tooltip.offsetWidth - 10;
                        }}
                        
                        tooltip.style.top = `${{top}}px`;
                        tooltip.style.left = `${{left}}px`;
                    }});
                    
                    node.addEventListener('mouseleave', () => {{
                        tooltip.classList.remove('visible');
                    }});
                }}
            }});
        }});

        // Add additional tooltip styles
        document.head.insertAdjacentHTML('beforeend', `
            <style>
                #{chart_id} .tooltip-content {{
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }}
                
                #{chart_id} .tooltip-title {{
                    font-weight: bold;
                    font-size: 14px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                    padding-bottom: 4px;
                    margin-bottom: 4px;
                }}
                
                #{chart_id} .tooltip-description {{
                    white-space: pre-line;
                    max-height: 250px;
                    overflow-y: auto;
                    padding-right: 5px;
                    font-size: 11px;
                }}
                
                #{chart_id} .tooltip-description::-webkit-scrollbar {{
                    width: 4px;
                }}
                
                #{chart_id} .tooltip-description::-webkit-scrollbar-track {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 2px;
                }}
                
                #{chart_id} .tooltip-description::-webkit-scrollbar-thumb {{
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 2px;
                }}
                
                #{chart_id} .tooltip-paragraph {{
                    margin: 0 0 6px 0;
                    padding: 0;
                    line-height: 1.3;
                }}
                
                #{chart_id} .tooltip-paragraph:last-child {{
                    margin-bottom: 0;
                }}
                
                #{chart_id} .tooltip-heading {{
                    font-weight: bold;
                    font-size: 12px;
                    color: #4361EE;
                    display: block;
                    margin-top: 6px;
                }}
                
                #{chart_id}.dark-mode .tooltip-heading {{
                    color: #4cc9f0;
                }}
                
                #{chart_id} .tooltip {{
                    max-width: 320px;
                    max-height: 350px;
                    overflow: hidden;
                }}
            </style>
        `);

        // Initialize other functions
        initializeNodePositions();
    </script>
                    """
    
    # Complete HTML
    html = f"""
    {css}
    <div id="{chart_id}">
        <div class="flowchart-container" style="width: {container_width}px; height: {container_height}px;">
            {nodes_html}
            {connections_html}
        </div>
        {controls_html}
    </div>
    
    <script>
        // Wait for DOM to be fully loaded
        document.addEventListener('DOMContentLoaded', function() {{
            // Get the container elements
            const chartContainer = document.getElementById('{chart_id}');
            const flowchartContainer = chartContainer.querySelector('.flowchart-container');
            
            // Basic initialization functions only - export functionality removed
            console.log("Flowchart initialized");
        }});
    </script>
    """
    
    return html

# Function to generate a download link for the HTML
def get_download_link(html, filename="flowchart.html"):
    try:
        logger.info(f"Generating download link for {filename}")
        
        # Validate HTML
        if not html or not isinstance(html, str):
            logger.error("Invalid HTML content provided")
            st.error("Error generating download link: Invalid HTML content")
            return ""
            
        # Encode HTML to base64
        try:
            b64 = base64.b64encode(html.encode()).decode()
        except Exception as e:
            logger.error(f"Error encoding HTML content: {str(e)}")
            st.error("Error creating download link: Unable to encode HTML content")
            return ""
    
        # Add additional HTML header with complete doctype and styling
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flowchart</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&family=Open+Sans:wght@400;600&family=Comfortaa:wght@400;700&family=IBM+Plex+Sans:wght@400;500&family=Quicksand:wght@500;600&family=Montserrat:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
</head>
<body style="margin: 0; padding: 20px; background-color: #f5f5f5;">
{html}
</body>
</html>"""
    
        try:
            full_b64 = base64.b64encode(full_html.encode()).decode()
            
            # Check if the base64 string is too large (which could cause browser issues)
            if len(full_b64) > 5000000:  # ~5MB limit
                logger.warning(f"Generated base64 string is very large: {len(full_b64)} bytes")
                st.warning("The generated flowchart is quite large, which might affect download performance")
                
            button_html = f'''
                <a href="data:text/html;base64,{full_b64}" download="{filename}" style="text-decoration: none;">
                    <button style="padding: 8px 16px; background-color: #4361EE; color: white; border: none; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; font-family: sans-serif;">
                        <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="30" height="30" viewBox="0 0 30 30">
                            <path d="M25.428,3.333C25.238,3.121,24.967,3,24.683,3H5.317C5.033,3,4.762,3.121,4.572,3.333c-0.19,0.212-0.28,0.495-0.249,0.777l2.202,19.823c0.044,0.403,0.329,0.74,0.719,0.851l7.48,2.137c0.09,0.026,0.183,0.039,0.275,0.039s0.185-0.013,0.275-0.039l7.48-2.137c0.39-0.111,0.674-0.448,0.719-0.851L25.676,4.11C25.708,3.828,25.618,3.545,25.428,3.333z M20.629,10.43h-8.93l0.212,2.542h8.503l-0.638,7.51L15.003,22l-0.047-0.015l-4.72-1.505L9.978,17.42h2.312l0.101,1.189l2.637,0.581l2.591-0.582l0.275-3.213h-8.09L9.178,8h11.659L20.629,10.43z"></path>
                        </svg>
                         Download HTML
                    </button>
                </a>
            '''
            logger.info("Download link generated successfully")
            return button_html
            
        except Exception as e:
            logger.error(f"Error generating download button: {str(e)}")
            st.error("Error creating download button. Please try again.")
            return ""
            
    except Exception as e:
        logger.error(f"Unexpected error in get_download_link: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("An unexpected error occurred while creating the download link")
        return ""

# Response caching functions
_response_cache = {}

def check_cached_response(key):
    """Check if we have a cached response for this key"""
    if key in _response_cache:
        return _response_cache[key]
    return None

def cache_response(key, data):
    """Cache a response for future use"""
    _response_cache[key] = data
    # Keep cache size manageable
    if len(_response_cache) > 50:
        # Remove oldest items
        oldest_keys = list(_response_cache.keys())[:10]
        for old_key in oldest_keys:
            del _response_cache[old_key]

# Implement parallel processing for faster flowchart generation
def generate_flowchart_with_progress(description, api_key, industry, theme_key, orientation):
    """Generate flowchart with progress indicator and parallelization"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Start API call in background
    status_text.text("Step 1/3: Generating flowchart structure...")
    
    # Use ThreadPoolExecutor for concurrent processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the API call in the background
        future = executor.submit(generate_flowchart_description, description, api_key, industry)
        
        # Monitor progress while API call is running
        start_time = time.time()
        while not future.done():
            # Update progress based on elapsed time (estimate 10 seconds total)
            elapsed = time.time() - start_time
            if elapsed < 10:
                progress = min(0.33, elapsed / 10 * 0.33)  # 33% for step 1
                progress_bar.progress(progress)
            time.sleep(0.1)  # Short sleep to avoid CPU spinning
        
        # Get the flowchart data from the completed future
        try:
            flowchart_data = future.result()
            if not flowchart_data:
                return None
        except Exception as e:
            logger.error(f"Error in background API call: {str(e)}")
            st.error(f"Error generating flowchart structure: {str(e)}")
            return None
    
    # Step 2: Generate HTML (this is typically fast)
    status_text.text("Step 2/3: Creating visualization...")
    progress_bar.progress(0.4)  # 40% after API call
    
    try:
        # Generate the HTML for the flowchart
        flowchart_html = generate_flowchart_html(flowchart_data, theme_key, orientation)
        progress_bar.progress(0.7)  # 70% after HTML generation
    except Exception as e:
        logger.error(f"Error generating HTML: {str(e)}")
        st.error(f"Error creating visualization: {str(e)}")
        return None
    
    # Step 3: Prepare download link
    status_text.text("Step 3/3: Finalizing flowchart...")
    progress_bar.progress(0.9)  # 90% almost done
    
    # Extract chart ID for export options
    chart_id = None
    try:
        chart_id_match = re.search(r'id="(flowchart-[a-z0-9]+)"', flowchart_html)
        if chart_id_match:
            chart_id = chart_id_match.group(1)
    except Exception as e:
        logger.error(f"Error extracting chart ID: {str(e)}")
    
    # Create download link
    try:
        html_button = get_download_link(flowchart_html, "flowchart.html")
    except Exception as e:
        logger.error(f"Error creating download link: {str(e)}")
        html_button = None
    
    # Complete
    progress_bar.progress(1.0)
    status_text.text("Flowchart generated successfully!")
    time.sleep(0.5)  # Short pause to show completion
    status_text.empty()  # Clear the status text
    progress_bar.empty()  # Remove the progress bar
    
    return {
        "flowchart_data": flowchart_data,
        "flowchart_html": flowchart_html,
        "chart_id": chart_id,
        "html_button": html_button
    }


def generate_export_options(chart_id):
    """Generate HTML with client-side export options for the flowchart"""
    # Empty function that returns nothing - all export functionality removed
    return ""

# All conversion functions (convert_to_png, convert_to_pdf, etc.) have been removed

# Streamlit UI
# Replace the plain header with a styled banner
# st.markdown("""
# <div style="text-align: center; margin-bottom: 30px;">
#     <div style="background: linear-gradient(to right, #4361EE, #4CC9F0); padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
#         <h1 style="color: white; margin: 0; font-family: 'Roboto', sans-serif; font-size: 32px;">
#             <i class="fas fa-project-diagram" style="margin-right: 15px;"></i>Ask Flow Chart
#         </h1>
#         <p style="color: white; margin: 8px 0 0 0; font-size: 18px;">AI-Powered Flow Chart Generator</p>
#     </div>
# </div>
# """, unsafe_allow_html=True)


st.title("Ask Flow Chart")

# Tabs for different sections
tab1, tab2 = st.tabs(["Create Flowchart", "About"])

with tab1:
    # Create sidebar for configuration options
    with st.sidebar:
        # Logo for Ask Flow Chart
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="background: linear-gradient(to right, #4361EE, #4CC9F0); padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: white; margin: 0; font-family: 'Roboto', sans-serif; font-size: 24px;">
                    <i class="fas fa-project-diagram" style="margin-right: 10px;"></i>Ask Flow Chart
                </h1>
                <p style="color: white; margin: 5px 0 0 0; font-size: 14px;">AI-Powered Flow Chart Generator</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # API key input
        api_key = st.text_input("Enter your Mistral API key", type="password")

        # Industry selection
        industry = st.selectbox(
                "Select Industry (Optional)",
                ["General", "Technology", "Healthcare", "Finance", "Education", "Marketing", "Manufacturing", "Retail"]
            )
        industry = None if industry == "General" else industry
            
        # Design theme selection
        theme_key = st.selectbox(
                "Design Theme",
                list(DESIGN_THEMES.keys()),
                format_func=lambda x: DESIGN_THEMES[x]["name"]
            )
            
        # Orientation selection
        orientation = st.selectbox(
                "View Orientation",
                ["landscape", "portrait"]
            )

    # Description input in main area
    description = st.text_area(
        "Describe the flow chart you want to create",
        height=200,
        placeholder="Example: Create a flowchart for a customer support process. Start with receiving a customer complaint, then evaluate if it's a known issue. If yes, provide standard solution, if no, escalate to specialist. Finally, follow up with the customer."
    )

# Performance monitoring and advanced settings in sidebar
with st.sidebar:
    # Add a collapsible section for advanced settings
    with st.expander("Performance Settings"):
        use_caching = st.checkbox("Enable Result Caching", value=True, 
                                help="Cache results to improve performance for repeated queries")
        
        use_parallel = st.checkbox("Use Parallel Processing", value=True,
                                 help="Process requests in parallel for faster generation")
        
        optimization_level = st.select_slider(
            "Performance Optimization Level",
            options=["Balanced", "Faster Response", "Better Quality"],
            value="Faster Response",
            help="Adjust the balance between speed and quality"
        )

        # Performance metrics
        st.markdown("### Performance Metrics")
        
        # Create placeholders for performance metrics
        execution_time_placeholder = st.empty()
        api_time_placeholder = st.empty()
        render_time_placeholder = st.empty()
        max_tokens_placeholder = st.empty()
        temperature_placeholder = st.empty()

        if 'last_execution_time' in st.session_state:
            execution_time_placeholder.info(f"⏱️ Total: {st.session_state.last_execution_time:.2f}s")
        else:
            execution_time_placeholder.text("⏱️ Total: Not available")
            
        if 'last_api_time' in st.session_state:
            api_time_placeholder.text(f"🔄 API: {st.session_state.last_api_time:.2f}s")
        else:
            api_time_placeholder.text("🔄 API: Not available")
            
        if 'last_render_time' in st.session_state:
            render_time_placeholder.text(f"🖥️ Render: {st.session_state.last_render_time:.2f}s")
        else:
            render_time_placeholder.text("🖥️ Render: Not available")

# Debug mode toggle in sidebar (only visible in development)
with st.sidebar:
    debug_mode = st.checkbox("Enable Debug Mode", value=False, key="debug_mode")
    if debug_mode:
        # with st.expander("Debug Console"):
        #     st.info("Debug mode is enabled. Additional logging information will be displayed.")
            
        #     # Debug controls
        #     st.write("### Debug Controls")
        #     log_level = st.selectbox(
        #         "Log Level", 
        #         ["DEBUG", "INFO", "WARNING", "ERROR"],
        #         index=1
        #     )
            
        #     # Set logger level based on selection
        #     if log_level == "DEBUG":
        #         logger.setLevel(logging.DEBUG)
        #     elif log_level == "INFO":
        #         logger.setLevel(logging.INFO)
        #     elif log_level == "WARNING":
        #         logger.setLevel(logging.WARNING)
        #     elif log_level == "ERROR":
        #         logger.setLevel(logging.ERROR)
            
            # System information
            st.write("### System Information")
            st.text(f"App Version: 1.0.0")
            # st.text(f"Python: {os.sys.version.split()[0]}")
            # st.text(f"Memory Usage: {round(os.process.memory_info().rss / (1024*1024), 2)} MB")
            
            # Log testing
            # if st.button("Test Logging"):
            #     logger.debug("This is a debug message")
            #     logger.info("This is an info message")
            #     logger.warning("This is a warning message")
            #     logger.error("This is an error message")
            #     st.success("Log test complete. Check your console or logs.")
                
            # Cache information
            st.write("### Cache Status")
            st.text(f"Cache Size: {len(_response_cache)} items")
            if st.button("Clear Cache"):
                _response_cache.clear()
                st.success("Cache cleared successfully")

# Apply performance settings based on optimization level
if optimization_level == "Faster Response":
    max_tokens = 500
    temperature = 0.3
elif optimization_level == "Better Quality":
    max_tokens = 1500
    temperature = 0.7
else:  # Balanced
    max_tokens = 1000
    temperature = 0.5

    # Generate button
if st.button("Generate Flow Chart"):
    # First, validate inputs
    if not api_key:
        st.error("Please enter your Mistral API key in the sidebar")
        logger.warning("Generation attempted without API key")
    elif not description:
        st.error("Please enter a description for your flowchart")
        logger.warning("Generation attempted without description")
    else:
        try:
            # Record start time for execution time tracking
            total_start_time = time.time()
            
            # If using parallel processing, use the progress function
            if use_parallel:
                result = generate_flowchart_with_progress(description, api_key, industry, theme_key, orientation)
                
                if result:
                    # Record total execution time
                    total_execution_time = time.time() - total_start_time
                    st.session_state.last_execution_time = total_execution_time
                    # Set estimated API and render times (for parallel processing we don't have exact measurements)
                    st.session_state.last_api_time = total_execution_time * 0.7  # Estimate
                    st.session_state.last_render_time = total_execution_time * 0.2  # Estimate
                    
                    # Update performance metrics in sidebar
                    execution_time_placeholder.info(f"⏱️ Total: {total_execution_time:.2f}s")
                    api_time_placeholder.text(f"🔄 API: {st.session_state.last_api_time:.2f}s (estimated)")
                    render_time_placeholder.text(f"🖥️ Render: {st.session_state.last_render_time:.2f}s (estimated)")
                    # Display performance settings in the side menu
                    max_tokens_placeholder.text(f"Max Tokens: {max_tokens}")
                    temperature_placeholder.text(f"Temperature: {temperature}")
                    # Display the flowchart
                    st.markdown("<h3>Generated Flow Chart</h3>", unsafe_allow_html=True)
                    
                    # Display the flowchart
                    st.components.v1.html(result['flowchart_html'], height=700)
                    
                    # Add Export Options if available
                    if result['chart_id']:
                        export_options = generate_export_options(result['chart_id'])
                        if export_options:
                            st.components.v1.html(export_options, height=0, scrolling=False)
                    
                    # Display download button
                    if result['html_button']:
                        st.markdown(result['html_button'], unsafe_allow_html=True)
                    
            else:
                # Original sequential approach with spinner
                with st.spinner("Generating flow chart..."):
                    logger.info("Starting flowchart generation process")
                    
                    # Call Mistral API to get the flowchart structure
                    api_start_time = time.time()
                    flowchart_data = generate_flowchart_description(description, api_key, industry)
                    api_time = time.time() - api_start_time
                    st.session_state.last_api_time = api_time
                    logger.info(f"API processing completed in {api_time:.2f} seconds")
            
                    if flowchart_data:
                        try:
                            # Generate and display HTML/CSS flowchart
                            render_start_time = time.time()
                            flowchart_html = generate_flowchart_html(flowchart_data, theme_key, orientation)
                            render_time = time.time() - render_start_time
                            st.session_state.last_render_time = render_time
                            logger.info(f"HTML generation completed in {render_time:.2f} seconds")
                
                            # Record total time
                            total_execution_time = time.time() - total_start_time
                            st.session_state.last_execution_time = total_execution_time
                            
                            # Update performance metrics in sidebar
                            execution_time_placeholder.info(f"⏱️ Total: {total_execution_time:.2f}s")
                            api_time_placeholder.text(f"🔄 API: {api_time:.2f}s")
                            render_time_placeholder.text(f"🖥️ Render: {render_time:.2f}s")
                
                            st.markdown("<h3>Generated Flow Chart</h3>", unsafe_allow_html=True)
                            
                            # Display the flowchart
                            try:
                                st.components.v1.html(flowchart_html, height=700)
                                logger.info("Flowchart displayed successfully")
                            except Exception as e:
                                logger.error(f"Error displaying flowchart: {str(e)}")
                                st.error(f"Error displaying flowchart: {str(e)}")
                                if debug_mode:
                                    st.error(traceback.format_exc())
                            
                            # Add Export Options
                            try:
                                chart_id = re.search(r'id="(flowchart-[a-z0-9]+)"', flowchart_html)
                                if chart_id:
                                    export_options = generate_export_options(chart_id.group(1))
                                    if export_options:
                                        st.components.v1.html(export_options, height=0, scrolling=False)
                                        logger.info("Export options added")
                            except Exception as e:
                                logger.error(f"Error adding export options: {str(e)}")
                                # Non-critical error, don't show to user
                            
                            # HTML Download - basic functionality
                            try:
                                html_button = get_download_link(flowchart_html, "flowchart.html")
                                if html_button:
                                    st.markdown(html_button, unsafe_allow_html=True)
                                    logger.info("Download button added successfully")
                                else:
                                    raise Exception("Failed to generate download button")
                            except Exception as e:
                                logger.error(f"Error creating download button: {str(e)}")
                                st.error("Could not create download button. Please try again or contact support.")
                                if debug_mode:
                                    st.error(traceback.format_exc())
                            
                        except Exception as e:
                            logger.error(f"Error generating flowchart HTML: {str(e)}")
                            logger.error(traceback.format_exc())
                            st.error(f"Error generating flowchart visualization: {str(e)}")
                            if debug_mode:
                                st.error(traceback.format_exc())
                    else:
                        logger.error("Failed to generate flowchart data")
                        st.error("Failed to generate flowchart. Please check your API key and try again with a different description.")
                
        except Exception as e:
            logger.error(f"Unexpected error in main flow: {str(e)}")
            logger.error(traceback.format_exc())
            st.error(f"An unexpected error occurred: {str(e)}")
            if debug_mode:
                st.error(traceback.format_exc())


with tab2:
    st.markdown("""
    ## About This Flow Chart Generator
    
    This modern flow chart generator creates professional-looking flowcharts with different design themes and industry-specific styling. 
    
    ### Features:
    
    - **Multiple Design Themes**: Choose from various professionally designed themes including Modern Minimal, Corporate Professional, Creative Colorful, Tech Blueprint, Healthcare, and Finance & Banking.
    
    - **Industry-Specific Layouts**: Optimize your flowchart for specific industries with appropriate terminology and icons.
    
    - **Font Awesome Icons**: Each node includes relevant icons to enhance visual understanding.
    
    - **Professional Styling**: Includes shadows, gradients, hover effects, and modern color schemes.
    
    - **Downloadable HTML**: Save your flowchart as an HTML file that can be viewed in any browser.
    
    ### How It Works:
    
    1. The app uses the Mistral AI language model to interpret your description and generate a structured flowchart representation
    2. It then applies your chosen design theme with appropriate styling
    3. The final flowchart is rendered using HTML and CSS for a responsive, interactive result
    
    ### Tips for Great Flowcharts:
    
    - Be specific about process steps, decision points, and the flow between them
    - Mention start and end points explicitly
    - For complex processes, break them down into clear sequential steps
    - Consider the audience when choosing design themes
    """)

