"""Test Case Generation Agent using Google ADK with Web Crawling."""

import json
import sys
import os
from pathlib import Path
from google.adk.agents import Agent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.crawl_tool import crawl_page_sync
from tools.ui_extractor import extract_ui_elements
from tools.ui_graph_builder import build_ui_graph, build_complete_ui_flow


# Tool 1: Parse User Story
def parse_user_story(story: str) -> dict:
    if not story or not story.strip():
        return {
            "status": "error",
            "error_message": "User story text cannot be empty.",
        }

    story = story.strip()
    result = {
        "status": "success",
        "original_story": story,
        "actor": "Unknown",
        "action": "Unknown",
        "goal": "Unknown",
        "notes": "Components extracted. Use generate_test_cases to produce test cases.",
    }

    lower = story.lower()

    if "as a" in lower or "as an" in lower:
        try:
            start = lower.find("as a")
            if start == -1:
                start = lower.find("as an")
                actor_prefix_len = 6
            else:
                actor_prefix_len = 5

            actor_start = start + actor_prefix_len
            want_idx = lower.find("i want", actor_start)
            if want_idx != -1:
                result["actor"] = story[actor_start:want_idx].strip().rstrip(",")

            action_start = want_idx + 7
            so_that_idx = lower.find("so that", action_start)
            if so_that_idx != -1:
                result["action"] = story[action_start:so_that_idx].strip().rstrip(",")
                result["goal"] = story[so_that_idx + 8:].strip().rstrip(".")
            else:
                result["action"] = story[action_start:].strip().rstrip(".")

        except Exception:
            result["notes"] = (
                "Could not fully parse story structure. "
                "Proceeding with full text for test case generation."
            )
    else:
        result["notes"] = (
            "Story does not follow the 'As a ... I want ... so that ...' format. "
            "Proceeding with full text for test case generation."
        )

    return result


# Tool 2: Generate Test Cases
def generate_test_cases(story: str, test_types: str = "positive,negative,edge") -> dict:
    if not story or not story.strip():
        return {
            "status": "error",
            "error_message": "User story text cannot be empty.",
        }

    requested_types = [t.strip().lower() for t in test_types.split(",")]
    valid_types = {"positive", "negative", "edge"}
    invalid = set(requested_types) - valid_types
    
    if invalid:
        return {
            "status": "error",
            "error_message": (
                f"Invalid test types: {invalid}. "
                f"Allowed values are: {valid_types}"
            ),
        }

    test_cases = []
    counter = 1

    type_templates = {
        "positive": {
            "suffix": "Happy Path",
            "priority": "high",
            "description": "Valid inputs and expected successful outcome",
        },
        "negative": {
            "suffix": "Error Handling",
            "priority": "high",
            "description": "Invalid inputs or failure conditions",
        },
        "edge": {
            "suffix": "Edge Case",
            "priority": "medium",
            "description": "Boundary conditions and unusual but valid scenarios",
        },
    }

    # Extract key info from story for better test cases
    story_lower = story.lower()
    
    for t in requested_types:
        tmpl = type_templates[t]
        
        # Generate context-specific test cases
        if t == "positive":
            test_cases.append({
                "id": f"TC-{counter:03d}",
                "title": f"[{tmpl['suffix']}] User successfully performs desired action with valid inputs",
                "type": t,
                "description": tmpl["description"],
                "preconditions": "User is authenticated and on the relevant page with valid permissions",
                "steps": [
                    "1. Locate and open the feature/module mentioned in the story",
                    "2. Provide valid input data as described in the story",
                    "3. Execute the desired action",
                    "4. Verify system processes the request",
                    "5. Confirm the expected outcome is achieved",
                ],
                "expected_result": "Action completes successfully; system provides confirmation; data is correctly processed and returned",
                "priority": tmpl["priority"],
            })
        elif t == "negative":
            test_cases.append({
                "id": f"TC-{counter:03d}",
                "title": f"[{tmpl['suffix']}] System properly handles error conditions and invalid inputs",
                "type": t,
                "description": tmpl["description"],
                "preconditions": "User is on the relevant page",
                "steps": [
                    "1. Attempt to perform action with invalid/missing inputs",
                    "2. Try with null, empty, or malformed data",
                    "3. Attempt with unauthorized access if applicable",
                    "4. Trigger error conditions (timeout, system unavailable, etc.)",
                    "5. Observe system response",
                ],
                "expected_result": "System displays appropriate error message; request is rejected safely; no data corruption occurs; user is guided to correct input",
                "priority": tmpl["priority"],
            })
        else:  # edge case
            test_cases.append({
                "id": f"TC-{counter:03d}",
                "title": f"[{tmpl['suffix']}] System handles boundary conditions and unusual valid scenarios",
                "type": t,
                "description": tmpl["description"],
                "preconditions": "User is on the relevant page with valid permissions",
                "steps": [
                    "1. Test with minimum allowed values/inputs",
                    "2. Test with maximum allowed values/inputs",
                    "3. Test with special characters and edge values",
                    "4. Test with concurrent requests if applicable",
                    "5. Test with very long or very short inputs",
                ],
                "expected_result": "System processes edge cases correctly; maintains data integrity; responds within acceptable time limits; handles limits gracefully",
                "priority": tmpl["priority"],
            })
        counter += 1

    return {
        "status": "success",
        "story": story,
        "total_test_cases": len(test_cases),
        "test_cases": test_cases,
    }


# Tool 3: Format Test Cases as Markdown
def format_test_cases_as_markdown(test_cases_json: str) -> dict:
    if not test_cases_json or not test_cases_json.strip():
        return {
            "status": "error",
            "error_message": "test_cases_json cannot be empty.",
        }

    try:
        data = json.loads(test_cases_json)
        if isinstance(data, dict):
            test_cases = data.get("test_cases", [])
            story = data.get("story", "")
        elif isinstance(data, list):
            test_cases = data
            story = ""
        else:
            return {
                "status": "error",
                "error_message": "Invalid JSON format. Expected a list or object with 'test_cases' key.",
            }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_message": f"Failed to parse JSON: {str(e)}",
        }

    if not test_cases:
        return {
            "status": "error",
            "error_message": "No test cases found in the provided JSON.",
        }

    lines = []
    lines.append("# Test Cases Report")
    lines.append("")
    if story:
        lines.append(f"> **User Story:** {story}")
        lines.append("")

    lines.append(f"**Total Test Cases:** {len(test_cases)}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| ID | Title | Type | Priority |")
    lines.append("|----|-------|------|----------|")
    for tc in test_cases:
        tc_id = tc.get("id", "N/A")
        title = tc.get("title", "N/A")
        tc_type = tc.get("type", "N/A")
        priority = tc.get("priority", "N/A")
        lines.append(f"| {tc_id} | {title} | {tc_type} | {priority} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Test Cases")
    lines.append("")

    type_icons = {"positive": "✅", "negative": "❌", "edge": "⚠️"}

    for tc in test_cases:
        tc_id = tc.get("id", "N/A")
        title = tc.get("title", "N/A")
        tc_type = tc.get("type", "N/A")
        icon = type_icons.get(tc_type, "🔹")
        priority = tc.get("priority", "N/A")
        preconditions = tc.get("preconditions", "N/A")
        steps = tc.get("steps", [])
        expected = tc.get("expected_result", "N/A")

        lines.append(f"### {icon} {tc_id}: {title}")
        lines.append("")
        lines.append(f"- **Type:** `{tc_type}`")
        lines.append(f"- **Priority:** `{priority}`")
        lines.append(f"- **Preconditions:** {preconditions}")
        lines.append("")
        lines.append("**Test Steps:**")
        lines.append("")
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")
        lines.append(f"**Expected Result:** {expected}")
        lines.append("")
        lines.append("---")
        lines.append("")

    markdown_output = "\n".join(lines)

    return {
        "status": "success",
        "markdown": markdown_output,
        "total_test_cases": len(test_cases),
    }


# Tool 4: Crawl Website
def crawl_website(url: str) -> dict:
    """Crawl a website and extract content using Crawl4AI."""
    result = crawl_page_sync(url)
    return {
        "success": result.get("success"),
        "url": url,
        "preview": result.get("markdown", "")[:1000] if result.get("success") else None,
        "has_html": bool(result.get("html")),
        "error": result.get("error")
    }


# Tool 5: Extract UI Elements
def extract_ui_elements_tool(html_content: str) -> dict:
    """Extract UI elements from HTML content."""
    if not html_content:
        return {"error": "HTML content is empty", "elements": {}}
    
    elements = extract_ui_elements(html_content)
    return {
        "buttons": elements.get("buttons", [])[:5],
        "inputs": elements.get("inputs", [])[:3],
        "dropdowns": elements.get("dropdowns", [])[:3],
        "links": elements.get("links", [])[:5],
        "forms": elements.get("forms", []),
        "summary": elements.get("summary", {})
    }


# Tool 6: Build UI Action Graph
def build_ui_action_graph(html_content: str) -> dict:
    """Build UI action graph from HTML content."""
    if not html_content:
        return {"error": "HTML content is empty", "graph": {}}
    
    elements = extract_ui_elements(html_content)
    graph = build_ui_graph(elements)
    page_type = graph.get("page_type")
    flows = build_complete_ui_flow(page_type, elements)
    
    return {
        "page_type": page_type,
        "available_actions": graph.get("available_actions", []),
        "user_flows": graph.get("user_flows", []),
        "example_flows": [flow["step"] for flow in flows[:3]]
    }


root_agent = Agent(
    name="testcase_generation_agent",
    model="gemini-2.0-flash",
    description="An AI QA engineer agent that generates test cases from user stories or websites.",
    instruction="""You are an expert QA Engineer. You can generate comprehensive test cases in two ways:

**Mode 1: Story-Based (Recommended for given user stories)**
1. Use parse_user_story to extract actor, action, and goal
2. Use generate_test_cases to create test cases (positive, negative, edge)
3. Use format_test_cases_as_markdown to format the output

**Mode 2: Website-Based (For URLs)**
1. Use crawl_website to fetch page content
2. Use extract_ui_elements_tool to identify interactive elements
3. Use build_ui_action_graph to understand user flows
4. Generate test cases based on the UI structure and interactions

**Test Case Requirements:**
For each type (positive, negative, edge), create 3 detailed test cases:
- **Positive**: Valid inputs, happy path, expected success
- **Negative**: Error handling, invalid inputs, missing fields, unauthorized access
- **Edge**: Boundary conditions, special characters, extreme values, security concerns

Always provide:
- Test ID (TC-P001, TC-N001, TC-E001, etc.)
- Title describing what is tested
- Type, Priority, Description
- Preconditions (setup requirements)
- Numbered steps (1, 2, 3...)
- Expected results

Make test cases specific to the story or website context, not generic.""",
    tools=[
        parse_user_story,
        generate_test_cases,
        format_test_cases_as_markdown,
        crawl_website,
        extract_ui_elements_tool,
        build_ui_action_graph
    ],
)

