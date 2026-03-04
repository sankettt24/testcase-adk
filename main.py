#!/usr/bin/env python3
"""
Test Case Generation Agent - ADK integrated CLI + Web Interface

Run with: python main.py
"""

import json
from testcase_agent.agent import root_agent


def generate_from_story(user_story: str, test_types: str = "positive,negative,edge"):
    """Generate test cases from a user story."""
    prompt = f"""
    User Story: {user_story}
    
    Generate test cases for: {test_types}
    """
    
    response = root_agent.generate(prompt)
    return response


def generate_from_url(url: str, user_story: str = ""):
    """Generate test cases by crawling a website."""
    prompt = f"""
    Website URL: {url}
    {f'User Story: {user_story}' if user_story else ''}
    
    Please:
    1. Crawl the website
    2. Extract UI elements
    3. Build UI action graph
    4. Generate comprehensive test cases (positive, negative, edge cases)
    """
    
    response = root_agent.generate(prompt)
    return response


def interactive_mode():
    """Run interactive test case generation."""
    print("\n" + "="*60)
    print("🧪 ADK Test Case Generator")
    print("="*60)
    print("\nChoose mode:")
    print("1. Story-based generation")
    print("2. Website-based generation")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        story = input("\nEnter user story: ").strip()
        if story:
            print("\n⏳ Generating test cases from story...")
            result = generate_from_story(story)
            print("\n" + "="*60)
            print(result)
            print("="*60)
    
    elif choice == "2":
        url = input("\nEnter website URL: ").strip()
        story = input("Enter user story (optional): ").strip()
        
        if url:
            print(f"\n⏳ Crawling {url} and generating test cases...")
            result = generate_from_url(url, story)
            print("\n" + "="*60)
            print(result)
            print("="*60)
    
    elif choice != "3":
        print("Invalid choice!")
    
    if choice in ["1", "2"]:
        again = input("\nGenerate another? (y/n): ").strip().lower()
        if again == "y":
            interactive_mode()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       ADK Test Case Generation Agent                    ║
    ║       Powered by Gemini 2.0-Flash                       ║
    ║                                                          ║
    ║  Features:                                              ║
    ║  ✓ Story-based test generation (BDD format)             ║
    ║  ✓ Website crawling & UI analysis (Crawl4AI)            ║
    ║  ✓ Intelligent action graph building                    ║
    ║  ✓ Comprehensive test coverage                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
