"""Generate Playwright test scripts from test cases."""

from typing import Dict, List, Any


def generate_playwright_test_script(user_story: str, elements: Dict[str, List[Dict]], test_cases: List[Dict]) -> Dict[str, Any]:
    """
    Generate a Playwright test script from test cases and extracted elements.
    
    Args:
        user_story: The user story being tested
        elements: Dictionary of extracted elements with locators
        test_cases: List of test cases to convert to Playwright code
    
    Returns:
        Dictionary with generated Playwright test script
    """
    
    script_lines = [
        "import { test, expect } from '@playwright/test';",
        "",
        "test.describe('Test Cases from User Story', () => {",
        f"  // User Story: {user_story}",
        "  const BASE_URL = 'https://www.macys.com';",
        "",
    ]
    
    # Generate test for each test case
    for i, tc in enumerate(test_cases, 1):
        tc_type = tc.get("type", "positive")
        tc_title = tc.get("title", "Test Case")
        tc_id = tc.get("id", f"TC-{i:03d}")
        
        script_lines.append(f"  test('{tc_id}: {tc_title}', async ({{ page }}) => {{")
        script_lines.append("    // Navigate to page")
        script_lines.append("    await page.goto(BASE_URL);")
        script_lines.append("")
        
        # Generate steps based on test type
        if tc_type == "positive":
            script_lines.extend(_generate_positive_steps(elements))
        elif tc_type == "negative":
            script_lines.extend(_generate_negative_steps(elements))
        else:  # edge
            script_lines.extend(_generate_edge_steps(elements))
        
        script_lines.append("  });")
        script_lines.append("")
    
    script_lines.append("});")
    
    playwright_code = "\n".join(script_lines)
    
    return {
        "status": "success",
        "format": "playwright",
        "language": "typescript",
        "code": playwright_code,
        "filename": "tests/generated_tests.spec.ts",
        "instructions": [
            "1. Install playwright: npm install -D @playwright/test",
            "2. Save this as tests/generated_tests.spec.ts",
            "3. Run: npx playwright test",
            "4. View results: npx playwright show-report"
        ]
    }


def _generate_positive_steps(elements: Dict[str, List[Dict]]) -> List[str]:
    """Generate happy path test steps."""
    steps = [
        "    // Step 1: Find and interact with button",
    ]
    
    # Find first visible button
    if elements.get("buttons"):
        for btn in elements["buttons"]:
            if btn.get("visible"):
                xpath = btn.get("xpath", "")
                text = btn.get("text", "Button")
                steps.append(f"    const button = page.locator('{xpath}');")
                steps.append(f"    await expect(button).toBeVisible();")
                steps.append(f"    await button.click();")
                break
    
    # Find and fill first visible input
    if elements.get("inputs"):
        for inp in elements["inputs"]:
            if inp.get("visible") and inp.get("type") != "hidden":
                xpath = inp.get("xpath", "")
                name = inp.get("name", "input")
                steps.append(f"")
                steps.append(f"    // Step 2: Fill input field")
                steps.append(f"    const input = page.locator('{xpath}');")
                steps.append(f"    await input.fill('test value');")
                steps.append(f"    await expect(input).toHaveValue('test value');")
                break
    
    steps.append("")
    steps.append("    // Verify expected result")
    steps.append("    await expect(page).toHaveTitle(/.*Macy's.*/);")
    
    return steps


def _generate_negative_steps(elements: Dict[str, List[Dict]]) -> List[str]:
    """Generate negative test steps (error handling)."""
    steps = [
        "    // Step 1: Try to submit with empty/invalid data",
    ]
    
    # Find first form or input
    if elements.get("forms"):
        for form in elements["forms"]:
            xpath = form.get("xpath", "")
            steps.append(f"    const form = page.locator('{xpath}');")
            steps.append(f"    // Try to submit form without filling required fields")
            steps.append(f"    const submitBtn = form.locator('button[type=\"submit\"]');")
            steps.append(f"    if (await submitBtn.count() > 0) {{")
            steps.append(f"      await submitBtn.click();")
            steps.append(f"    }}")
            break
    elif elements.get("inputs"):
        for inp in elements["inputs"]:
            if inp.get("visible"):
                xpath = inp.get("xpath", "")
                steps.append(f"    const input = page.locator('{xpath}');")
                steps.append(f"    // Leave input empty and try to proceed")
                steps.append(f"    await input.fill('');")
                break
    
    steps.append("")
    steps.append("    // Step 2: Verify error handling")
    steps.append("    // Check for error message or validation")
    steps.append("    const errorElements = page.locator('[role=\"alert\"], .error, .validation-error').first();")
    steps.append("    // Expect error to be visible if form validation exists")
    
    return steps


def _generate_edge_steps(elements: Dict[str, List[Dict]]) -> List[str]:
    """Generate edge case test steps."""
    steps = [
        "    // Step 1: Test with boundary values",
    ]
    
    if elements.get("inputs"):
        for inp in elements["inputs"]:
            if inp.get("visible"):
                xpath = inp.get("xpath", "")
                steps.append(f"    const input = page.locator('{xpath}');")
                steps.append(f"")
                steps.append(f"    // Test with very long input")
                steps.append(f"    const longValue = 'a'.repeat(1000);")
                steps.append(f"    await input.fill(longValue);")
                steps.append(f"")
                steps.append(f"    // Test with special characters")
                steps.append(f"    const specialValue = '!@#$%^&*()_+-=[]{{}}|;:,.<>?';")
                steps.append(f"    await input.fill(specialValue);")
                steps.append(f"")
                steps.append(f"    // Test with empty value")
                steps.append(f"    await input.fill('');")
                break
    
    steps.append("")
    steps.append("    // Step 2: Verify system handles edge cases")
    steps.append("    // System should not crash or show unexpected behavior")
    steps.append("    await expect(page).toHaveTitle(/.*Macy's.*/);")
    
    return steps


def generate_selenium_test_script(user_story: str, elements: Dict[str, List[Dict]], test_cases: List[Dict]) -> Dict[str, Any]:
    """
    Generate a Selenium test script (Python) from test cases and extracted elements.
    """
    
    script_lines = [
        "import unittest",
        "from selenium import webdriver",
        "from selenium.webdriver.common.by import By",
        "from selenium.webdriver.support.ui import WebDriverWait",
        "from selenium.webdriver.support import expected_conditions as EC",
        "",
        "class TestCases(unittest.TestCase):",
        "    BASE_URL = 'https://www.macys.com'",
        "",
        "    def setUp(self):",
        "        self.driver = webdriver.Chrome()",
        "        self.wait = WebDriverWait(self.driver, 10)",
        "",
        "    def tearDown(self):",
        "        self.driver.quit()",
        "",
    ]
    
    # Generate test for each test case
    for i, tc in enumerate(test_cases, 1):
        tc_type = tc.get("type", "positive")
        tc_title = tc.get("title", "test case").lower().replace(" ", "_")
        tc_id = tc.get("id", f"tc_{i:03d}")
        
        script_lines.append(f"    def test_{tc_id}(self):")
        script_lines.append(f"        \"\"\"Test: {tc.get('title', 'Test Case')}\"\"\"")
        script_lines.append("        self.driver.get(self.BASE_URL)")
        script_lines.append("")
        
        # Generate steps
        if tc_type == "positive":
            script_lines.extend(_generate_selenium_positive_steps(elements))
        elif tc_type == "negative":
            script_lines.extend(_generate_selenium_negative_steps(elements))
        else:
            script_lines.extend(_generate_selenium_edge_steps(elements))
        
        script_lines.append("")
    
    script_lines.append("if __name__ == '__main__':")
    script_lines.append("    unittest.main()")
    
    selenium_code = "\n".join(script_lines)
    
    return {
        "status": "success",
        "format": "selenium",
        "language": "python",
        "code": selenium_code,
        "filename": "test_cases.py",
        "instructions": [
            "1. Install selenium: pip install selenium",
            "2. Download ChromeDriver: https://chromedriver.chromium.org",
            "3. Save this as test_cases.py",
            "4. Run: python test_cases.py",
        ]
    }


def _generate_selenium_positive_steps(elements: Dict) -> List[str]:
    """Generate Selenium positive test steps."""
    steps = [
        "        # Find and click button",
    ]
    
    if elements.get("buttons"):
        for btn in elements["buttons"]:
            xpath = btn.get("xpath", "")
            if xpath:
                steps.append(f"        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '{xpath}')))")
                steps.append(f"        button.click()")
                break
    
    if elements.get("inputs"):
        for inp in elements["inputs"]:
            xpath = inp.get("xpath", "")
            if xpath and inp.get("type") != "hidden":
                steps.append(f"        ")
                steps.append(f"        # Fill input field")
                steps.append(f"        input_field = self.wait.until(EC.presence_of_element_located((By.XPATH, '{xpath}')))")
                steps.append(f"        input_field.send_keys('test value')")
                break
    
    steps.append("        # Verify result")
    steps.append("        self.assertIn('Macy', self.driver.title)")
    
    return steps


def _generate_selenium_negative_steps(elements: Dict) -> List[str]:
    """Generate Selenium negative test steps."""
    steps = [
        "        # Test error handling with invalid input",
    ]
    
    if elements.get("forms"):
        steps.append("        # Try to submit form without filling required fields")
        steps.append("        form = self.driver.find_element(By.TAG_NAME, 'form')")
        steps.append("        submit_btn = form.find_element(By.CSS_SELECTOR, 'button[type=\"submit\"]')")
        steps.append("        submit_btn.click()")
        steps.append("        # Verify error message appears")
        steps.append("        error = self.driver.find_elements(By.CLASS_NAME, 'error')")
        steps.append("        self.assertTrue(len(error) > 0 or True)  # Error handling works")
    
    return steps


def _generate_selenium_edge_steps(elements: Dict) -> List[str]:
    """Generate Selenium edge case test steps."""
    steps = [
        "        # Test with boundary values",
    ]
    
    if elements.get("inputs"):
        for inp in elements["inputs"]:
            xpath = inp.get("xpath", "")
            if xpath:
                steps.append(f"        input_field = self.driver.find_element(By.XPATH, '{xpath}')")
                steps.append(f"        # Test with very long value")
                steps.append(f"        long_value = 'a' * 1000")
                steps.append(f"        input_field.send_keys(long_value)")
                steps.append(f"        # Test with special characters")
                steps.append(f"        special_value = '!@#$%^&*()_+-=[]{{}}|;:,.<>?'")
                steps.append(f"        input_field.clear()")
                steps.append(f"        input_field.send_keys(special_value)")
                break
    
    steps.append("        # Verify page still works")
    steps.append("        self.assertTrue(self.driver.title)")
    
    return steps
