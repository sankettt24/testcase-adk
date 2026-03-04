import json
from typing import Dict, List


def build_ui_graph(elements: Dict) -> Dict:
    """Build UI action graph from extracted elements."""
    
    # Infer page type from elements
    page_type = infer_page_type(elements)
    
    # Build action graph based on page type
    graph = {
        "page_type": page_type,
        "available_actions": [],
        "user_flows": [],
        "interaction_patterns": []
    }
    
    # Add actions based on detected elements
    if elements["inputs"]:
        graph["available_actions"].append("fill_input_field")
        graph["interaction_patterns"].append({
            "type": "form_interaction",
            "inputs": [inp.get("name", "unknown") for inp in elements["inputs"][:3]]
        })
    
    if elements["buttons"]:
        graph["available_actions"].extend(["click_button", "submit_form"])
        graph["interaction_patterns"].append({
            "type": "button_click",
            "buttons": elements["buttons"][:5]
        })
    
    if elements["dropdowns"]:
        graph["available_actions"].append("select_dropdown_option")
        graph["interaction_patterns"].append({
            "type": "dropdown_selection",
            "dropdowns": elements["dropdowns"][:3]
        })
    
    if elements["links"]:
        graph["available_actions"].append("navigate_link")
        graph["interaction_patterns"].append({
            "type": "navigation",
            "links": [link.get("text", "")[:30] for link in elements["links"][:5]]
        })
    
    # Add page-specific flows
    summary = elements.get("summary", {})
    
    if summary.get("has_search"):
        graph["user_flows"].append("search_product")
        graph["user_flows"].append("view_search_results")
    
    if summary.get("has_cart"):
        graph["user_flows"].extend(["add_to_cart", "view_cart", "checkout"])
    
    if summary.get("has_login"):
        graph["user_flows"].append("login_or_register")
    
    # Default flows for any page
    if not graph["user_flows"]:
        graph["user_flows"] = ["view_page", "interact_with_elements", "navigate_away"]
    
    return graph


def infer_page_type(elements: Dict) -> str:
    """Infer page type from available elements."""
    summary = elements.get("summary", {})
    
    if summary.get("has_search"):
        return "search_page"
    elif summary.get("has_cart"):
        return "product_page"
    elif summary.get("has_login"):
        return "login_page"
    elif len(elements.get("links", [])) > 20:
        return "navigation_hub"
    elif len(elements.get("forms", [])) > 0:
        return "form_page"
    else:
        return "content_page"


def build_complete_ui_flow(page_type: str, elements: Dict) -> Dict:
    """Build complete user interaction flow for the page."""
    flows = {
        "homepage": [
            {"step": "view_homepage", "element": "page"},
            {"step": "search_product", "element": "search_input"},
            {"step": "view_results", "element": "results_list"},
            {"step": "open_product", "element": "product_link"}
        ],
        "search_page": [
            {"step": "enter_search_query", "element": "search_input"},
            {"step": "submit_search", "element": "search_button"},
            {"step": "view_results", "element": "results_container"},
            {"step": "filter_results", "element": "filter_dropdown"},
            {"step": "sort_results", "element": "sort_dropdown"}
        ],
        "product_page": [
            {"step": "view_product_details", "element": "product_info"},
            {"step": "select_size", "element": "size_dropdown"},
            {"step": "select_color", "element": "color_dropdown"},
            {"step": "view_price", "element": "price_display"},
            {"step": "add_to_cart", "element": "add_button"},
            {"step": "view_reviews", "element": "reviews_section"}
        ],
        "cart_page": [
            {"step": "view_cart_items", "element": "cart_list"},
            {"step": "update_quantity", "element": "quantity_input"},
            {"step": "remove_item", "element": "remove_button"},
            {"step": "apply_coupon", "element": "coupon_input"},
            {"step": "proceed_checkout", "element": "checkout_button"}
        ],
        "login_page": [
            {"step": "enter_email", "element": "email_input"},
            {"step": "enter_password", "element": "password_input"},
            {"step": "submit_login", "element": "login_button"},
            {"step": "forgot_password", "element": "forgot_password_link"}
        ]
    }
    
    return flows.get(page_type, flows["homepage"])
