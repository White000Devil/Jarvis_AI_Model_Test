"""
Gradio-based Admin Dashboard for JARVIS AI Assistant
"""

import gradio as gr
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys
import os
import yaml # For config tab
from loguru import logger # Explicitly import logger

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.ethical_ai import EthicalAIEngine
from core.reasoning_engine import ReasoningEngine
from core.human_ai_teaming import HumanAITeaming
from core.self_correction import SelfCorrectionEngine
from core.self_learning import SelfLearningEngine # Import SelfLearningEngine
from core.collaboration_hub import CollaborationHub # Import CollaborationHub
from core.deployment_manager import DeploymentManager # Import DeploymentManager
from core.voice_interface import VoiceInterface # Import VoiceInterface
from utils.logger import setup_logging # Import setup_logging if needed for standalone test

# Try to import charting libraries
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    logger.warning("Charting libraries (plotly, pandas) not available. Install: pip install plotly pandas")

def create_admin_dashboard(
    nlp_engine: NLPEngine,
    memory_manager: MemoryManager,
    api_integrations: APIIntegrations,
    vision_engine: VisionEngine,
    ethical_ai_engine: EthicalAIEngine,
    reasoning_engine: ReasoningEngine,
    human_ai_teaming: HumanAITeaming,
    self_correction_engine: SelfCorrectionEngine,
    learning_engine: SelfLearningEngine,
    collaboration_hub: CollaborationHub,
    deployment_manager: DeploymentManager,
    voice_engine: VoiceInterface
):
    """Create Gradio interface for admin dashboard"""
    
    async def get_system_overview():
        """Get comprehensive system overview"""
        try:
            overview = {
                "timestamp": datetime.now().isoformat(),
                "status": "operational",
                "components": {}
            }
            
            # Voice Interface Status
            voice_stats = voice_engine.get_voice_stats()
            overview["components"]["voice"] = {
                "status": "enabled" if voice_stats["voice_enabled"] else "disabled",
                "listening": voice_stats["is_listening"],
                "speaking": voice_stats["is_speaking"],
                "commands": len(voice_stats["registered_commands"])
            }
            
            # Collaboration Hub Status
            collab_stats = collaboration_hub.get_collaboration_stats()
            overview["components"]["collaboration"] = {
                "status": "operational",
                "active_sessions": collab_stats["sessions"]["active"],
                "total_users": collab_stats["users"]["total"],
                "total_workspaces": collab_stats["workspaces"]["total"]
            }
            
            # Deployment Status
            deploy_stats = deployment_manager.get_deployment_stats()
            overview["components"]["deployment"] = {
                "status": "operational",
                "active_deployments": deploy_stats["active_deployments"],
                "docker_available": deploy_stats["docker_enabled"],
                "kubernetes_available": deploy_stats["kubernetes_enabled"]
            }
            
            # Learning Engine Status
            learning_stats = learning_engine.get_learning_stats()
            overview["components"]["learning"] = {
                "status": "operational",
                "total_feedback": learning_stats["feedback_stats"]["total_feedback"],
                "average_rating": learning_stats["feedback_stats"]["average_rating"],
                "scraped_items": learning_stats["scraping_stats"]["total_scraped"]
            }
            
            # Memory System Status
            memory_stats = memory_manager.get_memory_stats()
            overview["components"]["memory"] = {
                "status": "operational",
                "total_items": memory_stats.get("total_items", 0),
                "collections": len([k for k, v in memory_stats.items() if isinstance(v, dict) and "count" in v])
            }
            
            # Vision Engine Status
            vision_stats = vision_engine.get_vision_stats()
            overview["components"]["vision"] = {
                "status": "enabled" if vision_stats["enabled"] else "disabled",
                "models_loaded": vision_stats["models_loaded"],
                "cache_size": vision_stats["cache_size"],
                "recording_active": vision_stats["recording_active"]
            }

            # Phase 5 Components
            ethical_stats = ethical_ai_engine.get_ethical_stats()
            overview["components"]["ethical_ai"] = {
                "status": "enabled" if ethical_stats["enabled"] else "disabled",
                "total_violations": ethical_stats.get("total_violations", 0)
            }

            reasoning_stats = reasoning_engine.get_reasoning_stats()
            overview["components"]["reasoning"] = {
                "status": "enabled" if reasoning_stats["enabled"] else "disabled",
                "planning_depth": reasoning_stats.get("planning_depth")
            }

            teaming_stats = human_ai_teaming.get_teaming_stats()
            overview["components"]["human_ai_teaming"] = {
                "status": "enabled" if teaming_stats["enabled"] else "disabled",
                "adaptive_communication": teaming_stats.get("adaptive_communication_enabled"),
                "clarification_threshold": teaming_stats.get("clarification_threshold")
            }

            self_correction_stats = self_correction_engine.get_correction_stats()
            overview["components"]["self_correction"] = {
                "status": "enabled" if self_correction_stats["enabled"] else "disabled",
                "total_corrections": self_correction_stats.get("total_corrections", 0)
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"❌ System overview failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def create_system_metrics_chart(deploy_stats):
        """Create system metrics visualization"""
        if not CHARTS_AVAILABLE:
            return gr.Markdown("Plotly and Pandas not installed. Cannot display charts.")

        try:
            system_metrics = deploy_stats.get("system_metrics", {})
            
            if "error" in system_metrics:
                return go.Figure().add_annotation(text="Metrics unavailable", x=0.5, y=0.5)
            
            fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]],
                                subplot_titles=("CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)"))
            
            # CPU Usage Gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=system_metrics.get("cpu", {}).get("usage_percent", 0),
                title={'text': "CPU"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ), row=1, col=1)
            
            # Memory Usage Gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=system_metrics.get("memory", {}).get("percent", 0),
                title={'text': "Memory"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ), row=1, col=2)
            
            # Disk Usage Gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=system_metrics.get("disk", {}).get("percent", 0),
                title={'text': "Disk"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkorange"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ), row=1, col=3)
            
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Metrics chart creation failed: {e}")
            return go.Figure().add_annotation(text=f"Error: {e}", x=0.5, y=0.5)
    
    def create_component_status_chart(overview):
        """Create component status visualization"""
        if not CHARTS_AVAILABLE:
            return gr.Markdown("Plotly and Pandas not installed. Cannot display charts.")

        try:
            components = overview.get("components", {})
            
            component_names = []
            statuses = []
            colors = []
            
            for name, info in components.items():
                component_names.append(name.replace('_', ' ').title()) # Format names
                status = info.get("status", "unknown")
                statuses.append(status)
                
                if status == "operational" or status == "enabled":
                    colors.append("green")
                elif status == "disabled" or status == "warning":
                    colors.append("orange")
                else:
                    colors.append("red")
            
            df = pd.DataFrame({'Component': component_names, 'Status': statuses, 'Color': colors})
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df['Component'],
                    y=[1] * len(df), # All bars have same height
                    marker_color=df['Color'],
                    text=df['Status'],
                    textposition='inside'
                )
            ])
            
            fig.update_layout(
                title="Component Status Overview",
                xaxis_title="Components",
                yaxis_title="Status",
                yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                height=400,
                margin=dict(l=10, r=10, t=50, b=10)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Component status chart creation failed: {e}")
            return go.Figure().add_annotation(text=f"Error: {e}", x=0.5, y=0.5)
    
    async def get_recent_activity():
        """Get recent system activity"""
        try:
            activity = []
            
            # Get recent feedback
            learning_stats = learning_engine.get_learning_stats()
            if learning_stats["feedback_stats"]["total_feedback"] > 0:
                activity.append({
                    "timestamp": datetime.now() - timedelta(minutes=5),
                    "component": "Learning",
                    "event": f"Received feedback (avg rating: {learning_stats['feedback_stats']['average_rating']:.2f})",
                    "severity": "info"
                })
            
            # Get collaboration activity
            collab_stats = collaboration_hub.get_collaboration_stats()
            if collab_stats["sessions"]["active"] > 0:
                activity.append({
                    "timestamp": datetime.now() - timedelta(minutes=2),
                    "component": "Collaboration",
                    "event": f"{collab_stats['sessions']['active']} active sessions",
                    "severity": "info"
                })
            
            # Get deployment activity
            deploy_stats = deployment_manager.get_deployment_stats()
            if deploy_stats["active_deployments"] > 0:
                activity.append({
                    "timestamp": datetime.now() - timedelta(minutes=1),
                    "component": "Deployment",
                    "event": f"{deploy_stats['active_deployments']} active deployments",
                    "severity": "info"
                })

            # Get ethical violations
            ethical_stats = ethical_ai_engine.get_ethical_stats()
            if ethical_stats.get("total_violations", 0) > 0:
                activity.append({
                    "timestamp": datetime.now() - timedelta(minutes=10),
                    "component": "Ethical AI",
                    "event": f"Detected {ethical_stats['total_violations']} ethical violations",
                    "severity": "warning"
                })

            # Get self-correction events
            correction_stats = self_correction_engine.get_correction_stats()
            if correction_stats.get("total_corrections", 0) > 0:
                activity.append({
                    "timestamp": datetime.now() - timedelta(minutes=7),
                    "component": "Self-Correction",
                    "event": f"Performed {correction_stats['total_corrections']} self-corrections",
                    "severity": "info"
                })
            
            # Sort by timestamp
            activity.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return activity[:10]  # Return last 10 activities
            
        except Exception as e:
            logger.error(f"❌ Recent activity retrieval failed: {e}")
            return []
    
    def format_system_overview(overview):
        """Format system overview for display"""
        try:
            if "error" in overview:
                return f"❌ **System Overview Error:** {overview['error']}"
            
            components = overview.get("components", {})
            
            overview_text = f"""
# 🤖 JARVIS System Overview

**Status:** {overview.get('status', 'unknown').upper()}  
**Last Updated:** {overview.get('timestamp', 'unknown')}

## Component Status

### 🎤 Voice Interface
- **Status:** {components.get('voice', {}).get('status', 'unknown')}
- **Listening:** {'✅' if components.get('voice', {}).get('listening') else '❌'}
- **Speaking:** {'✅' if components.get('voice', {}).get('speaking') else '❌'}
- **Commands:** {components.get('voice', {}).get('commands', 0)}

### 🤝 Collaboration Hub
- **Status:** {components.get('collaboration', {}).get('status', 'unknown')}
- **Active Sessions:** {components.get('collaboration', {}).get('active_sessions', 0)}
- **Total Users:** {components.get('collaboration', {}).get('total_users', 0)}
- **Workspaces:** {components.get('collaboration', {}).get('total_workspaces', 0)}

### 🚀 Deployment Manager
- **Status:** {components.get('deployment', {}).get('status', 'unknown')}
- **Active Deployments:** {components.get('deployment', {}).get('active_deployments', 0)}
- **Docker Available:** {'✅' if components.get('deployment', {}).get('docker_available') else '❌'}
- **Kubernetes Available:** {'✅' if components.get('deployment', {}).get('kubernetes_available') else '❌'}

### 🧠 Self-Learning Engine
- **Status:** {components.get('learning', {}).get('status', 'unknown')}
- **Total Feedback:** {components.get('learning', {}).get('total_feedback', 0)}
- **Average Rating:** {components.get('learning', {}).get('average_rating', 0):.2f}
- **Scraped Items:** {components.get('learning', {}).get('scraped_items', 0)}

### 💾 Memory Manager
- **Status:** {components.get('memory', {}).get('status', 'unknown')}
- **Total Items:** {components.get('memory', {}).get('total_items', 0)}
- **Collections:** {components.get('memory', {}).get('collections', 0)}

### 👁️ Vision Engine
- **Status:** {components.get('vision', {}).get('status', 'unknown')}
- **Models Loaded:** {'✅' if components.get('vision', {}).get('models_loaded') else '❌'}
- **Cache Size:** {components.get('vision', {}).get('cache_size', 'N/A')}
- **Recording Active:** {'✅' if components.get('vision', {}).get('recording_active') else '❌'}

### ⚖️ Ethical AI Engine
- **Status:** {components.get('ethical_ai', {}).get('status', 'unknown')}
- **Total Violations:** {components.get('ethical_ai', {}).get('total_violations', 0)}

### 💡 Reasoning Engine
- **Status:** {components.get('reasoning', {}).get('status', 'unknown')}
- **Planning Depth:** {components.get('reasoning', {}).get('planning_depth', 'N/A')}

### 🤝 Human-AI Teaming
- **Status:** {components.get('human_ai_teaming', {}).get('status', 'unknown')}
- **Adaptive Communication:** {'✅' if components.get('human_ai_teaming', {}).get('adaptive_communication') else '❌'}
- **Clarification Threshold:** {components.get('human_ai_teaming', {}).get('clarification_threshold', 'N/A')}

### 🛠️ Self-Correction Engine
- **Status:** {components.get('self_correction', {}).get('status', 'unknown')}
- **Total Corrections:** {components.get('self_correction', {}).get('total_corrections', 0)}
"""
            return overview_text
        except Exception as e:
            logger.error(f"❌ Error formatting overview: {e}")
            return f"Error formatting overview: {e}"

    def format_recent_activity(activity_list):
        """Format recent activity for display"""
        if not activity_list:
            return "No recent activity."
        
        formatted_text = "## Recent Activity\n\n"
        for activity in activity_list:
            timestamp_str = activity["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            severity_icon = "🟢" if activity["severity"] == "info" else "🟠" if activity["severity"] == "warning" else "🔴"
            formatted_text += f"- {severity_icon} **{timestamp_str}** [{activity['component']}]: {activity['event']}\n"
        return formatted_text

    async def get_memory_content(collection_name: str, query: str = "", limit: int = 10):
        """Retrieve content from a specific memory collection"""
        try:
            if collection_name == "conversations":
                results = await memory_manager.search_conversations(query, limit=limit)
                return json.dumps(results, indent=2)
            elif collection_name == "general_knowledge":
                all_ids = memory_manager.knowledge_collection.get(limit=limit, include=[])['ids']
                if all_ids:
                    results = memory_manager.knowledge_collection.get(ids=all_ids, include=['documents', 'metadatas'])
                    formatted_results = []
                    for i in range(len(results['ids'])):
                        formatted_results.append({
                            "id": results['ids'][i],
                            "document": results['documents'][i],
                            "metadata": results['metadatas'][i]
                        })
                    return json.dumps(formatted_results, indent=2)
                return "[]"
            elif collection_name == "security_knowledge":
                results = await memory_manager.search_security_knowledge(query, limit=limit)
                return json.dumps(results, indent=2)
            elif collection_name == "ethical_violations":
                all_ids = memory_manager.ethical_violations_collection.get(limit=limit, include=[])['ids']
                if all_ids:
                    results = memory_manager.ethical_violations_collection.get(ids=all_ids, include=['documents', 'metadatas'])
                    formatted_results = []
                    for i in range(len(results['ids'])):
                        formatted_results.append({
                            "id": results['ids'][i],
                            "document": results['documents'][i],
                            "metadata": results['metadatas'][i]
                        })
                    return json.dumps(formatted_results, indent=2)
                return "[]"
            else:
                return "Invalid collection name."
        except Exception as e:
            logger.error(f"❌ Error retrieving memory content for {collection_name}: {e}")
            return f"Error: {e}"

    async def get_log_content(log_type: str, limit_lines: int = 100):
        """Retrieve content from log files"""
        log_path = None
        if log_type == "app_logs":
            log_path = Path("logs") / f"jarvis_{datetime.now().strftime('%Y-%m-%d')}.log"
        elif log_type == "feedback_logs":
            log_path = Path("data/feedback_logs/feedback.jsonl")
        elif log_type == "scraping_logs":
            log_path = Path("data/scraping_logs/scraping.jsonl")
        elif log_type == "ethical_violations_logs":
            log_path = Path("data/ethical_violations/violations.jsonl")
        elif log_type == "self_correction_logs":
            log_path = Path("data/self_correction_log/corrections.jsonl")
        
        if log_path and log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    return "".join(lines[-limit_lines:]) # Return last N lines
            except Exception as e:
                return f"Error reading log file: {e}"
        return f"Log file not found: {log_path}"

    async def update_config_file(config_str: str):
        """Update the config.yaml file"""
        try:
            new_config = yaml.safe_load(config_str)
            with open("config.yaml", "w") as f:
                yaml.safe_dump(new_config, f, indent=2)
            return "Configuration updated successfully! Restart JARVIS for changes to take effect."
        except yaml.YAMLError as e:
            return f"Error parsing YAML: {e}"
        except Exception as e:
            return f"Error saving configuration: {e}"

    def load_current_config():
        """Load current config.yaml content"""
        try:
            with open("config.yaml", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "# config.yaml not found. Using default settings."
        except Exception as e:
            return f"Error loading config.yaml: {e}"

    with gr.Blocks(title="JARVIS AI Admin Dashboard") as admin_dashboard:
        gr.Markdown("# ⚙️ JARVIS AI Admin Dashboard")
        gr.Markdown("Monitor and manage JARVIS AI components.")

        with gr.Tab("Overview"):
            overview_output = gr.Markdown()
            recent_activity_output = gr.Markdown()
            
            with gr.Row():
                system_metrics_chart = gr.Plot()
                component_status_chart = gr.Plot()

            def refresh_overview():
                overview = asyncio.run(get_system_overview())
                activity = asyncio.run(get_recent_activity())
                deploy_stats = deployment_manager.get_deployment_stats() # Get fresh stats for metrics
                return (
                    format_system_overview(overview),
                    format_recent_activity(activity),
                    create_system_metrics_chart(deploy_stats),
                    create_component_status_chart(overview)
                )

            admin_dashboard.load(refresh_overview, outputs=[overview_output, recent_activity_output, system_metrics_chart, component_status_chart], every=5) # Refresh every 5 seconds
            gr.Button("Refresh Overview").click(refresh_overview, outputs=[overview_output, recent_activity_output, system_metrics_chart, component_status_chart])

        with gr.Tab("Memory & Knowledge"):
            gr.Markdown("## Memory & Knowledge Management")
            with gr.Row():
                memory_collection_dropdown = gr.Dropdown(
                    choices=["conversations", "general_knowledge", "security_knowledge", "ethical_violations"],
                    label="Select Memory Collection",
                    value="conversations"
                )
                memory_query_input = gr.Textbox(label="Search Query (for conversations/security knowledge)", placeholder="e.g., 'SQL injection' or 'last interaction'")
                memory_limit_slider = gr.Slider(minimum=1, maximum=100, step=1, value=10, label="Limit Results")
                memory_refresh_button = gr.Button("Refresh Memory Content")
            
            memory_content_output = gr.JSON(label="Memory Content")
            
            memory_refresh_button.click(
                fn=lambda c, q, l: asyncio.run(get_memory_content(c, q, l)),
                inputs=[memory_collection_dropdown, memory_query_input, memory_limit_slider],
                outputs=[memory_content_output]
            )
            
            # Initial load
            admin_dashboard.load(
                fn=lambda: asyncio.run(get_memory_content("conversations")),
                outputs=[memory_content_output]
            )

        with gr.Tab("Logs"):
            gr.Markdown("## System Logs")
            with gr.Row():
                log_type_dropdown = gr.Dropdown(
                    choices=["app_logs", "feedback_logs", "scraping_logs", "ethical_violations_logs", "self_correction_logs"],
                    label="Select Log Type",
                    value="app_logs"
                )
                log_limit_slider = gr.Slider(minimum=10, maximum=1000, step=10, value=100, label="Limit Lines")
                log_refresh_button = gr.Button("Refresh Logs")
            
            log_content_output = gr.Textbox(label="Log Content", lines=20, interactive=False)
            
            log_refresh_button.click(
                fn=lambda t, l: asyncio.run(get_log_content(t, l)),
                inputs=[log_type_dropdown, log_limit_slider],
                outputs=[log_content_output]
            )
            
            # Initial load
            admin_dashboard.load(
                fn=lambda: asyncio.run(get_log_content("app_logs")),
                outputs=[log_content_output]
            )

        with gr.Tab("Configuration"):
            gr.Markdown("## Edit Configuration")
            gr.Markdown("Edit `config.yaml` directly. **Restart JARVIS AI for changes to take effect.**")
            config_editor = gr.Code(value=load_current_config(), language="yaml", lines=30, label="config.yaml")
            save_config_button = gr.Button("Save Configuration", variant="primary")
            config_status_output = gr.Textbox(label="Status", interactive=False)

            save_config_button.click(
                fn=update_config_file,
                inputs=[config_editor],
                outputs=[config_status_output]
            )
            
            # Reload config on tab select
            config_editor.change(fn=load_current_config, outputs=config_editor)

    return admin_dashboard

# This part is for testing the dashboard independently
if __name__ == "__main__":
    # Setup basic logging for the test run
    setup_logging(debug=True)

    # Mock all necessary engines for independent testing
    class MockNLPEngine:
        def __init__(self, config=None): pass
        async def process_query(self, query, context=None): return {"content": "mock nlp", "metadata": {"intent": "mock", "confidence": 0.5, "timestamp": datetime.now().isoformat(), "response_time": 0.1}}
        def get_conversation_summary(self): return {"total_exchanges": 10, "most_common_intent": "general_query"}
    
    class MockMemoryManager:
        def __init__(self, config=None): pass
        async def search_conversations(self, query, limit=10): 
            return [{"user_message": "Hello", "jarvis_response": "Hi there!", "metadata": {"intent": "greeting"}}]
        async def search_security_knowledge(self, query, limit=10): 
            return [{"title": "Mock Vuln", "description": "Mock description"}]
        def get_memory_stats(self): 
            return {"conversations": {"count": 5}, "security_knowledge": {"count": 2}, "ethical_violations": {"count": 1}, "total_items": 8}
        class MockChromaCollection:
            def get(self, ids=None, limit=None, include=None):
                if ids:
                    return {'ids': ids, 'documents': [f"Doc for {i}" for i in ids], 'metadatas': [{"source": "mock"}]}
                return {'ids': [f"id_{i}" for i in range(limit or 1)], 'documents': [], 'metadatas': []}
            def count(self): return 10
        knowledge_collection = MockChromaCollection()
        ethical_violations_collection = MockChromaCollection()
        async def add_ethical_violation(self, user_input: str, jarvis_response: str, violation_type: str, severity: str, explanation: str): pass


    class MockAPIIntegrations:
        def __init__(self, config=None): pass
        async def security_analysis(self, target): return {"status": "mocked"}
        def get_api_stats(self): return {"total_requests": 10, "successful_requests": 8, "failed_requests": 2}
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc_val, exc_tb): pass

    class MockVisionEngine:
        def __init__(self, config=None): pass
        async def analyze_video(self, path): return {"analysis_id": "mock_vid_analysis"}
        def get_vision_stats(self): return {"enabled": True, "models_loaded": True, "cache_size": "100MB", "recording_active": False}

    class MockEthicalAIEngine:
        def __init__(self, memory_manager, config=None): pass
        async def check_response_for_ethics(self, u, r, c): return True, []
        async def apply_ethical_guardrails(self, u, r, v): return r
        def get_ethical_stats(self): return {"enabled": True, "total_violations": 3, "violation_types": {"harmful_content": 2}}

    class MockReasoningEngine:
        def __init__(self, nlp, mem, api, vis, eth, config=None): pass
        async def reason_on_query(self, q, c): return {"reasoning_steps": ["mock step"], "decisions": [], "final_plan": "mock plan", "response": "Mock reasoning response."}
        def get_reasoning_stats(self): return {"enabled": True, "planning_depth": 3, "decision_threshold": 0.6}

    class MockHumanAITeaming:
        def __init__(self, nlp, mem, collab, config=None): pass
        async def clarify_request(self, u, c, ctx): return None
        async def adapt_communication(self, u, r, ctx): return r
        def get_teaming_stats(self): return {"enabled": True, "adaptive_communication_enabled": True, "clarification_threshold": 0.5}

    class MockSelfCorrectionEngine:
        def __init__(self, nlp, mem, eth, config=None): pass
        async def assess_confidence(self, r, c): return 0.8
        async def detect_inconsistency(self, r, h): return 0.9
        async def propose_correction(self, r, e): return r
        async def explain_reasoning(self, u, r, c): return "Mock explanation."
        def get_correction_stats(self): return {"enabled": True, "total_corrections": 1, "confidence_threshold": 0.7}
    
    class MockSelfLearningEngine:
        def __init__(self, memory_manager, config=None): pass
        async def process_user_feedback(self, u, r, rt, ft, i="unknown"): return "mock_feedback_id"
        async def scrape_security_data(self, max_items): return {"total_scraped": 5, "new_knowledge": 3, "sources": {"mock.com": {"items_scraped": 5, "new_items": 3}}}
        async def optimize_learning_parameters(self): return {"status": "optimized"}
        def get_learning_stats(self): return {"feedback_stats": {"total_feedback": 10, "average_rating": 0.7, "positive_feedback": 8, "negative_feedback": 2, "recent_average": 0.8}, "scraping_stats": {"total_scraped": 50, "new_knowledge": 20, "processed_items": 50, "processing_rate": 0.4}}

    class MockCollaborationHub:
        def __init__(self, config=None): self.enabled = True
        async def create_user(self, u, e, r): return "mock_user_id"
        async def get_user(self, u_id): return {"role": "admin"}
        async def create_workspace(self, n, d, c_by): return "mock_ws_id"
        async def create_collaboration_session(self, ws_id, c_by): return "mock_session_id"
        async def send_message(self, s_id, u_id, m_type, content): pass
        def get_collaboration_stats(self): return {"users": {"total": 5}, "workspaces": {"total": 2}, "sessions": {"total": 3, "active": 1}, "total_messages": 50, "active_connections": 1}

    class MockDeploymentManager:
        def __init__(self, config=None): self.enabled = True
        async def create_deployment_config(self, n, e, r=1, i="latest", p=None, ev=None): return {"name": n}
        async def build_docker_image(self, p, t): return True
        async def deploy_docker_container(self, c): return "mock_deploy_id_docker"
        async def deploy_to_kubernetes(self, c): return "mock_deploy_id_k8s"
        async def undeploy(self, d_id): return True
        def get_deployment_stats(self): return {"enabled": True, "docker_enabled": True, "kubernetes_enabled": False, "active_deployments": 2, "system_metrics": {"cpu": {"usage_percent": 45}, "memory": {"percent": 60}, "disk": {"percent": 75}}}

    class MockVoiceInterface:
        def __init__(self, config=None): self.enabled = True
        def register_command_callback(self, c, cb): pass
        async def start_listening(self, continuous=False): pass
        async def _single_voice_input(self, prompt=""): return "mock input"
        async def speak(self, text): pass
        def get_voice_stats(self): return {"voice_enabled": True, "is_listening": False, "is_speaking": False, "registered_commands": ["mock command"]}

    # Instantiate mocks
    mock_config = {
        "NLP_MODEL": "mock", "NLP_MAX_SEQ_LENGTH": 128,
        "CHROMA_DB_PATH": "mock_db", "EMBEDDING_MODEL": "mock",
        "API_KEYS": {},
        "VISION_ENABLED": True, "VISION_MODEL": "mock", "VIDEO_ANALYSIS_CACHE_SIZE_MB": 100,
        "FEEDBACK_LOG_PATH": "data/feedback_logs/feedback.jsonl",
        "SCRAPING_LOG_PATH": "data/scraping_logs/scraping.jsonl",
        "SECURITY_DATA_SOURCES": [], "MAX_SCRAPED_ITEMS_PER_RUN": 10,
        "VOICE_ENABLED": True, "WAKE_WORD": "jarvis", "STT_MODEL": "tiny.en", "TTS_VOICE": "en-US",
        "COLLABORATION_ENABLED": True, "MAX_ACTIVE_SESSIONS": 5,
        "DOCKER_ENABLED": True, "KUBERNETES_ENABLED": False,
        "ETHICAL_AI_ENABLED": True, "ETHICAL_VIOLATION_LOG_PATH": "data/ethical_violations/violations.jsonl", "ETHICAL_GUIDELINES": [],
        "REASONING_ENABLED": True, "PLANNING_DEPTH": 3, "DECISION_THRESHOLD": 0.7,
        "HUMAN_AI_TEAMING_ENABLED": True, "CLARIFICATION_THRESHOLD": 0.4, "ADAPTIVE_COMMUNICATION_ENABLED": True,
        "SELF_CORRECTION_ENABLED": True, "CONFIDENCE_THRESHOLD_FOR_CORRECTION": 0.6, "SELF_CORRECTION_LOG_PATH": "data/self_correction_log/corrections.jsonl"
    }

    mock_nlp = MockNLPEngine(mock_config)
    mock_memory = MockMemoryManager(mock_config)
    mock_api = MockAPIIntegrations(mock_config)
    mock_vision = MockVisionEngine(mock_config)
    mock_ethical = MockEthicalAIEngine(mock_memory, mock_config)
    mock_reasoning = MockReasoningEngine(mock_nlp, mock_memory, mock_api, mock_vision, mock_ethical, mock_config)
    mock_collab_hub = MockCollaborationHub(mock_config)
    mock_teaming = MockHumanAITeaming(mock_nlp, mock_memory, mock_collab_hub, mock_config)
    mock_correction = MockSelfCorrectionEngine(mock_nlp, mock_memory, mock_ethical, mock_config)
    mock_learning = MockSelfLearningEngine(mock_memory, mock_config)
    mock_deploy_manager = MockDeploymentManager(mock_config)
    mock_voice_interface = MockVoiceInterface(mock_config)

    # Create dashboard with mocks
    dashboard = create_admin_dashboard(
        mock_nlp,
        mock_memory,
        mock_api,
        mock_vision,
        mock_ethical,
        mock_reasoning,
        mock_teaming,
        mock_correction,
        mock_learning,
        mock_collab_hub,
        mock_deploy_manager,
        mock_voice_interface
    )
    
    # Launch the dashboard
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True
    )
    
    # Keep the main event loop running for Gradio
    try:
        while True:
            asyncio.run(asyncio.sleep(1))
    except KeyboardInterrupt:
        logger.info("Admin Dashboard stopped.")
