import json
import os
from google.adk import Agent
from tools.crawl_tool import crawl_page_sync
from tools.ui_extractor import extract_ui_elements
from tools.ui_graph_builder import build_ui_graph, build_complete_ui_flow


def parse_user_story(story: str) -> dict:
    """Parse user story to extract actor, action, and goal."""
    import re
    
    story = story.strip()
    
    actor = re.search(r'[Aa]s\s+(?:an?|a)\s+(.+?)[,.]', story)
    action = re.search(r'[Ii]\s+want\s+(?:to\s+)?(.+?)[,.]', story)
    goal = re.search(r'[Ss]o\s+that\s+(.+?)\.', story)
    
    return {
        "actor": actor.group(1).strip() if actor else "user",
        "action": action.group(1).strip() if action else story[:50],
        "goal": goal.group(1).strip() if goal else "purpose not specified"
    }


def crawl_website(url: str) -> dict:
    """Tool: Crawl website and get content."""
    return crawl_page_sync(url)


def extract_ui(html_content: str, markdown_content: str = "") -> dict:
    """Tool: Extract UI elements from page content."""
    elements = extract_ui_elements(html_content, markdown_content)
    return {
        "extracted_elements": elements,
        "element_count": sum(len(v) if isinstance(v, list) else 0 for v in elements.values())
    }


def build_graph(elements_data: str) -> dict:
    """Tool: Build UI action graph from elements."""
    try:
        elements = json.loads(elements_data) if isinstance(elements_data, str) else elements_data
    except:
        elements = elements_data
    
    graph = build_ui_graph(elements.get("extracted_elements", elements))
    return {
        "ui_graph": graph,
        "page_type": graph.get("page_type")
    }


def generate_test_cases_from_ui(user_story: str, ui_graph: dict, ui_elements: dict) -> dict:
    """Generate test cases based on user story and UI context."""
    parsed = parse_user_story(user_story)
    page_type = ui_graph.get("page_type", "content_page")
    flows = build_complete_ui_flow(page_type, ui_elements.get("extracted_elements", {}))
    
    test_cases = []
    priority_map = {"search": "high", "login": "critical", "checkout": "critical", "add": "high"}
    
    # Positive test cases
    for i, flow in enumerate(flows[:3], 1):
        test_cases.append({
            "id": f"TC-P{i:03d}",
            "type": "Positive",
            "title": f"Verify user can {flow['step']}",
            "priority": "High",
            "description": f"As {parsed['actor']}, verify ability to {flow['step']} when accessing {page_type}",
            "preconditions": [
                "User is on the page",
                f"Required element '{flow['element']}' is visible"
            ],
            "steps": [
                f"Locate {flow['element']} on the page",
                f"Perform {flow['step']} action",
                "Verify success feedback"
            ],
            "expected_result": f"User successfully {flow['step']}"
        })
    
    # Negative test cases
    negative_scenarios = [
        {"step": "submit_empty_form", "element": "submit_button", "reason": "Empty form submission"},
        {"step": "enter_invalid_input", "element": "input_field", "reason": "Invalid data input"},
        {"step": "missing_required_field", "element": "form", "reason": "Missing required field"}
    ]
    
    for i, scenario in enumerate(negative_scenarios, 1):
        test_cases.append({
            "id": f"TC-N{i:03d}",
            "type": "Negative",
            "title": f"Verify error handling for {scenario['reason']}",
            "priority": "Medium",
            "description": f"Verify system handles {scenario['reason']} gracefully",
            "preconditions": [
                "User is on the page",
                f"User attempts to {scenario['step']}"
            ],
            "steps": [
                f"Attempt {scenario['step']}",
                "Observe system response",
                "Verify error message is displayed"
            ],
            "expected_result": f"Error message shown, user not allowed to proceed"
        })
    
    # Edge cases
    edge_scenarios = [
        {"case": "long_input", "description": "Enter very long input in text field"},
        {"case": "special_characters", "description": "Enter special characters in input"},
        {"case": "rapid_clicks", "description": "Rapid clicking on button"}
    ]
    
    for i, scenario in enumerate(edge_scenarios, 1):
        test_cases.append({
            "id": f"TC-E{i:03d}",
            "type": "Edge",
            "title": f"Verify behavior with {scenario['case']}",
            "priority": "Low",
            "description": f"Test system behavior when {scenario['description']}",
            "preconditions": [
                "User is on the page",
                f"Scenario: {scenario['description']}"
            ],
            "steps": [
                f"Perform: {scenario['description']}",
                "Monitor application behavior",
                "Check for crashes or unexpected behavior"
            ],
            "expected_result": f"System handles {scenario['case']} gracefully"
        })
    
    return {
        "total_test_cases": len(test_cases),
        "by_type": {
            "positive": len([tc for tc in test_cases if tc["type"] == "Positive"]),
            "negative": len([tc for tc in test_cases if tc["type"] == "Negative"]),
            "edge": len([tc for tc in test_cases if tc["type"] == "Edge"])
        },
        "test_cases": test_cases
    }


def format_test_cases_markdown(test_cases_json: str) -> dict:
    """Format test cases as markdown report."""
    try:
        data = json.loads(test_cases_json) if isinstance(test_cases_json, str) else test_cases_json
    except:
        data = test_cases_json
    
    test_cases = data.get("test_cases", [])
    summary = data.get("by_type", {})
    
    markdown = "# Test Cases Report\n\n"
    markdown += f"**Total Test Cases:** {len(test_cases)}\n"
    markdown += f"**Positive:** {summary.get('positive', 0)} | "
    markdown += f"**Negative:** {summary.get('negative', 0)} | "
    markdown += f"**Edge:** {summary.get('edge', 0)}\n\n"
    
    markdown += "## Test Cases\n\n"
    
    for tc in test_cases:
        type_emoji = {"Positive": "✅", "Negative": "❌", "Edge": "⚠️"}.get(tc["type"], "📝")
        markdown += f"### {type_emoji} {tc['id']}: {tc['title']}\n"
        markdown += f"- **Type:** {tc['type']}\n"
        markdown += f"- **Priority:** {tc['priority']}\n"
        markdown += f"- **Description:** {tc['description']}\n"
        markdown += f"- **Preconditions:**\n"
        for pre in tc.get("preconditions", []):
            markdown += f"  - {pre}\n"
        markdown += f"- **Steps:**\n"
        for j, step in enumerate(tc.get("steps", []), 1):
            markdown += f"  {j}. {step}\n"
        markdown += f"- **Expected Result:** {tc['expected_result']}\n\n"
    
    return {
        "markdown": markdown,
        "test_case_count": len(test_cases)
    }


# Create ADK Agent with tools
root_agent = Agent(
    name="website_testcase_generator",
    description="Generates comprehensive test cases from user stories using website UI crawling and analysis",
    tools=[
        crawl_website,
        extract_ui,
        build_graph
    ]
)
