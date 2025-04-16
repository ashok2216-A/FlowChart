import streamlit as st
import requests
import json
import re
import random
import uuid
import math
import base64

# Set up the Streamlit app
st.set_page_config(page_title="Modern Flow Chart Generator", layout="wide")
st.title("Modern Flow Chart Generator")

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
        "connector": {"color": "#CED4DA", "style": "curved", "thickness": "2px"},
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
        "connector": {"color": "#95A5A6", "style": "straight", "thickness": "2px"},
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
        "connector": {"color": "#A5A6F6", "style": "dashed", "thickness": "3px"},
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
        "connector": {"color": "#4361EE", "style": "gradient", "thickness": "2px"},
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
        "connector": {"color": "#90E0EF", "style": "straight", "thickness": "2px"},
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
        "connector": {"color": "#95D5B2", "style": "straight", "thickness": "2px"},
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
    
    Format your response as JSON with this structure:
    {{
        "nodes": [
            {{"id": "node1", "text": "Start Process", "type": "start", "connections": ["node2"], "icon": "fa-play-circle"}},
            {{"id": "node2", "text": "Process Step", "type": "process", "connections": ["node3"], "icon": "fa-cogs"}},
            {{"id": "node3", "text": "Decision Point?", "type": "decision", "connections": ["node4", "node5"], "icon": "fa-question-circle"}},
            {{"id": "node4", "text": "Yes Path", "type": "process", "connections": ["node6"], "icon": "fa-check-circle"}},
            {{"id": "node5", "text": "No Path", "type": "process", "connections": ["node6"], "icon": "fa-times-circle"}},
            {{"id": "node6", "text": "End Process", "type": "end", "connections": [], "icon": "fa-flag-checkered"}}
        ]
    }}
    """
    
    data = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        
        # Extract the JSON content from the response
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Find JSON in the text
        json_match = re.search(r'```json\s*(\{.*?\})\s*```|(\{[\s\S]*"nodes"[\s\S]*?\})', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1) if json_match.group(1) else json_match.group(2)
            return json.loads(json_str)
        else:
            # Try to find a JSON object directly
            json_match = re.search(r'\{[\s\S]*"nodes"[\s\S]*?\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                st.error("Failed to extract valid JSON from the model response.")
                return None
    except Exception as e:
        st.error(f"Error calling Mistral API: {str(e)}")
        return None

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
        source_point_x = source_center_x
        source_point_y = source_center_y + source_height / 2
    
    if target_node["node"]["type"] == "decision":
        # Adjust the target point for diamond shape
        target_point_x = target_center_x
        target_point_y = target_center_y - target_height / 2
    
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
        return f"background: linear-gradient(90deg, {color}, {color}DD); height: {thickness}; {css}"
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
        return "transform: rotate(45deg); width: 100px; height: 100px;"
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
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow: hidden;
            background-color: transparent;
            border-radius: 12px;
            min-height: 700px;
            position: relative;
            transition: background-color 0.3s ease;
        }}
        
        #{chart_id}.dark-mode {{
            background-color: transparent;
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
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 5px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            gap: 5px;
            align-items: center;
            transition: background-color 0.3s ease;
        }}
        
        #{chart_id}.dark-mode .controls {{
            background: #2d2d2d;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        #{chart_id} .navigation-controls {{
            position: fixed;
            left: 20px;
            bottom: 20px;
            z-index: 1000;
            background: white;
            padding: 5px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2px;
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
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 30px;
            min-height: 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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
            transition: transform 0.2s, box-shadow 0.2s;
            border: 2px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            cursor: move;
            user-select: none;
        }}
        
        #{chart_id} .node.dragging {{
            opacity: 0.8;
            z-index: 1000;
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
        }}
        
        #{chart_id} .node-decision:hover {{
            transform: rotate(45deg) translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
            border-color: {theme["node_styles"]["decision"]["bg"]}DD;
        }}
        
        #{chart_id}.dark-mode .node-decision:hover {{
            box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
        }}
        
        #{chart_id} .node-decision .content {{
            transform: rotate(-45deg);
            width: 140px;
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
        
        #{chart_id} .connector:after {{
            content: '';
            position: absolute;
            right: -6px;
            top: -4px;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 5px 0 5px 8px;
            border-color: transparent transparent transparent {theme["connector"]["color"]};
            z-index: 3;
        }}
        
        #{chart_id} .connector.curved:after {{
            right: -8px;
            top: -5px;
            border-width: 6px 0 6px 10px;
        }}
        
        #{chart_id} .connector.dashed:after {{
            border-style: dashed;
            border-width: 5px 0 5px 8px;
        }}
        
        #{chart_id} .connector.gradient:after {{
            border-color: transparent transparent transparent {theme["connector"]["color"]}DD;
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
        
        # Different styling based on node type
        if node["type"] == "decision":
            nodes_html += f"""
            <div id="{node['id']}" class="node node-{node['type']}" style="left: {x}px; top: {y}px;">
                <div class="content">
                    {icon_html}
                    {node['text']}
                </div>
            </div>
            """
        else:
            nodes_html += f"""
            <div id="{node['id']}" class="node node-{node['type']}" style="left: {x}px; top: {y}px;">
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
                sourcePoint = {{
                    x: sourceCenter.x,
                    y: sourceCenter.y + source.height / 2
                }};
            }} else {{
                // Calculate border intersection for regular nodes
                sourcePoint = calculateBorderIntersection(sourceCenter, targetCenter, source);
            }}
            
            if (isTargetDecision) {{
                targetPoint = {{
                    x: targetCenter.x,
                    y: targetCenter.y - target.height / 2
                }};
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
        
        // Mouse event handlers
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
                }}
            }}
        }});
        
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
                const container = document.getElementById('{chart_id}');
                const containerRect = container.getBoundingClientRect();
                
                // Calculate new position
                let newX = e.clientX - containerRect.left - offsetX;
                let newY = e.clientY - containerRect.top - offsetY;
                
                // Update node position
                currentNode.style.left = `${{newX}}px`;
                currentNode.style.top = `${{newY}}px`;
                
                // Update stored position
                nodePositions.set(currentNode.id, {{
                    x: newX,
                    y: newY,
                    width: currentNode.offsetWidth,
                    height: currentNode.offsetHeight
                }});
                
                // Update connectors in real-time
                updateConnectors();
            }}
        }});
        
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
        }});
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
    """
    
    return html

# Function to generate a download link for the HTML
def get_download_link(html, filename="flowchart.html"):
    b64 = base64.b64encode(html.encode()).decode()
    
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
    
    full_b64 = base64.b64encode(full_html.encode()).decode()
    href = f'<a href="data:text/html;base64,{full_b64}" download="{filename}" target="_blank">Download Flowchart HTML</a>'
    return href

# Streamlit UI
st.header("Modern Flow Chart Generator")

# Tabs for different sections
tab1, tab2 = st.tabs(["Create Flowchart", "About"])

with tab1:
    # API key input
    api_key = st.text_input("Enter your Mistral API key", type="password")

    # Description input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        description = st.text_area(
            "Describe the flow chart you want to create",
            height=120,
            placeholder="Example: Create a flowchart for a customer support process. Start with receiving a customer complaint, then evaluate if it's a known issue. If yes, provide standard solution, if no, escalate to specialist. Finally, follow up with the customer."
        )
    
    with col2:
        industry = st.selectbox(
            "Select Industry (Optional)",
            ["General", "Technology", "Healthcare", "Finance", "Education", "Marketing", "Manufacturing", "Retail"]
        )
        industry = None if industry == "General" else industry
        
        theme_key = st.selectbox(
            "Design Theme",
            list(DESIGN_THEMES.keys()),
            format_func=lambda x: DESIGN_THEMES[x]["name"]
        )
        
        orientation = st.selectbox(
            "View Orientation",
            ["landscape", "portrait"]
        )
        
    

    # Generate button
    if st.button("Generate Flow Chart") and api_key and description:
        with st.spinner("Generating flow chart..."):
            # Call Mistral API to get the flowchart structure
            flowchart_data = generate_flowchart_description(description, api_key, industry)
            
            if flowchart_data:
                # Display the JSON data in an expandable section
                # with st.expander("View Flowchart Data (JSON)"):
                #     st.json(flowchart_data)
                
                # Generate and display HTML/CSS flowchart
                flowchart_html = generate_flowchart_html(flowchart_data, theme_key, orientation)
                
                st.subheader("Generated Flow Chart")
                st.components.v1.html(flowchart_html, height=700)
                
                # Download buttons
                st.markdown(get_download_link(flowchart_html), unsafe_allow_html=True)
                
                # Show theme preview
                with st.expander("Theme Details"):
                    st.write(f"**Theme:** {DESIGN_THEMES[theme_key]['name']}")
                    st.write("**Color Palette:**")
                    cols = st.columns(4)
                    with cols[0]:
                        st.markdown(f"<div style='background-color:{DESIGN_THEMES[theme_key]['node_styles']['start']['bg']};height:30px;width:30px;border-radius:4px;'></div>Start", unsafe_allow_html=True)
                    with cols[1]:
                        st.markdown(f"<div style='background-color:{DESIGN_THEMES[theme_key]['node_styles']['process']['bg']};height:30px;width:30px;border-radius:4px;border:1px solid #ddd'></div>Process", unsafe_allow_html=True)
                    with cols[2]:
                        st.markdown(f"<div style='background-color:{DESIGN_THEMES[theme_key]['node_styles']['decision']['bg']};height:30px;width:30px;border-radius:4px;'></div>Decision", unsafe_allow_html=True)
                    with cols[3]:
                        st.markdown(f"<div style='background-color:{DESIGN_THEMES[theme_key]['node_styles']['end']['bg']};height:30px;width:30px;border-radius:4px;'></div>End", unsafe_allow_html=True)
            else:
                st.error("Failed to generate flowchart. Please check your API key and try again.")

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

