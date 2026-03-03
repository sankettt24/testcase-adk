# 🧪 Testcase Generation Agent (ADK)

An AI-powered QA Engineer agent built with **Google ADK** that reads a user story and generates comprehensive, structured test cases — covering **positive**, **negative**, and **edge case** scenarios.

---

## 📁 Project Structure

```
testcase/
├── testcase_agent/
│   ├── __init__.py       # ADK package entry point
│   └── agent.py          # Agent logic + tools
├── .env                  # Your Gemini API key (fill this in)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## ⚙️ Setup

### 1. Prerequisites
- Python 3.9+
- pip

### 2. Create a Virtual Environment (recommended)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Your API Key
Open `.env` and replace `your_api_key_here` with your actual key:
```
GOOGLE_API_KEY=AIzaSy...your_key_here...
```
👉 Get a free key at: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## 🚀 Running the Agent

Open a terminal in this folder (`testcase/`) and run one of:

### Option A — Web UI (Recommended)
```bash
adk web
```
Then open **http://localhost:8000** in your browser, select `testcase_agent` from the dropdown, and start chatting.

### Option B — CLI
```bash
adk run testcase_agent
```
Type or paste your user story when prompted.

---

## 💬 How to Use

Simply paste a user story in the chat. Examples:

**Standard format:**
```
As a registered user, I want to log in with my email and password so that I can access my account.
```

**BDD format:**
```
Given I am on the login page,
When I enter valid credentials and click Login,
Then I should be redirected to my dashboard.
```

**Plain description:**
```
Users should be able to reset their password via a link sent to their email.
```

The agent will:
1. ✅ Parse your user story (actor, action, goal)
2. ✅ Generate test cases (positive, negative, edge cases)
3. ✅ Return a clean Markdown report with all test cases

---

## 🛠️ Agent Tools

| Tool | Description |
|------|-------------|
| `parse_user_story` | Extracts Actor, Action, and Goal from the story text |
| `generate_test_cases` | Creates scaffold test cases by type |
| `format_test_cases_as_markdown` | Outputs a clean Markdown test case report |

---

## 📋 Sample Output

```
# 🧪 Test Cases Report

> **User Story:** As a user, I want to log in...

**Total Test Cases:** 3

## Summary
| ID    | Title                           | Type     | Priority |
|-------|---------------------------------|----------|----------|
| TC-001| [Happy Path] Valid login        | positive | high     |
| TC-002| [Error] Wrong password          | negative | high     |
| TC-003| [Edge] SQL injection in email   | edge     | medium   |
...
```

---

## � Example Test Cases

### User Story
```
As a student,
I want to open and view detailed information of a course from the search results,
so that I can decide whether the class matches my interests
```

### Generated Test Cases

#### ✅ TC-001: [Happy Path] View Course Details
- **Type:** Positive
- **Priority:** High
- **Preconditions:** Student is logged in and has performed a course search that yielded results.
- **Test Steps:**
  1. Perform a course search that returns at least one course.
  2. Click on a course title or a "View Details" button associated with a course in the search results.
  3. Verify that a new page or modal window opens displaying the course details.
  4. Verify that the course details displayed include: Course Name, Course Code, Description, Instructor, Schedule, Credits, and Prerequisites (if any).
- **Expected Result:** The course details page/modal opens, displaying all relevant information about the course. The student can view all details without errors.

#### ❌ TC-002: [Error Handling] Course Details Not Displayed
- **Type:** Negative
- **Priority:** High
- **Preconditions:** Student is logged in and has performed a course search that yielded results.
- **Test Steps:**
  1. Perform a course search.
  2. Click on a course title or a "View Details" button associated with a course in the search results.
  3. Simulate a server error or network interruption while loading the course details.
- **Expected Result:** An error message is displayed to the student (e.g., "Failed to load course details. Please try again later."). The application does not crash or freeze.

#### ⚠️ TC-003: [Edge Case] Handling Large Course Descriptions
- **Type:** Edge Case
- **Priority:** Medium
- **Preconditions:** Student is logged in and has performed a course search that yielded results.
- **Test Steps:**
  1. Create a course with a very long description (e.g., several paragraphs or exceeding a reasonable character limit).
  2. Perform a course search that includes this course in the results.
  3. Click on the course to view its details.
- **Expected Result:** The course details page/modal opens, and the entire course description is displayed without truncation or formatting issues. The page loads within an acceptable timeframe. The layout of the page isn't broken by the long description.

---

### User Story 2
```
Title: Save Courses to Favorites

As a student,
I want to save courses to my favorites list,
so that I can quickly access classes I'm interested in later.

Acceptance Criteria:
- The student can click a "Save to Favorites" (or bookmark) option on a course.
- The selected course is added to the student's favorites list.
- The system confirms that the course was successfully saved.
- The student can view the saved course in the favorites section.
- The student can remove a course from favorites when no longer interested.
```

#### ✅ TC-001: [Happy Path] Save Course to Favorites
- **Type:** Positive
- **Priority:** High
- **Preconditions:** Student is logged in and viewing a course details page or a course listing.
- **Test Steps:**
  1. Navigate to a course details page or a course listing.
  2. Click the "Save to Favorites" button (or bookmark icon) for a specific course.
  3. Verify that a confirmation message is displayed (e.g., "Course saved to favorites").
  4. Navigate to the student's favorites list.
  5. Verify that the saved course is present in the favorites list, with all relevant details (course name, code, instructor, etc.).
- **Expected Result:** The course is successfully added to the student's favorites list, a confirmation message is displayed, and the course appears in the favorites section.

#### ❌ TC-002: [Error Handling] Unable to Save Course to Favorites
- **Type:** Negative
- **Priority:** High
- **Preconditions:** Student is logged in and viewing a course details page or a course listing.
- **Test Steps:**
  1. Navigate to a course details page or a course listing.
  2. Click the "Save to Favorites" button for a specific course.
  3. Simulate a server error or network interruption during the save operation.
- **Expected Result:** An appropriate error message is displayed to the student (e.g., "Unable to save course to favorites. Please try again later."). The course is not added to the favorites list.

#### ⚠️ TC-003: [Edge Case] Maximum Number of Courses in Favorites
- **Type:** Edge Case
- **Priority:** Medium
- **Preconditions:** Student is logged in. The system has a defined limit on the number of courses that can be saved to favorites.
- **Test Steps:**
  1. Save courses to the favorites list until the limit is reached.
  2. Attempt to save another course to favorites.
- **Expected Result:** A message is displayed to the student indicating that the maximum number of courses in favorites has been reached, and the course is not saved. The student may also be prompted to remove a course from favorites before adding a new one.

---
### User Story 3
```
Title: Search Products by Keyword

As a customer,
I want to search for products using keywords,
so that I can quickly find items I want to purchase.
```

#### ✅ TC-001: Positive Search - Valid keyword returns products
- **Type:** Positive
- **Priority:** High
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter "laptop" in the search bar.
  2. Click the search button.
- **Expected Result:** A list of laptops is displayed. Each product listed should have the word "laptop" in its title or description.

#### ✅ TC-002: Positive Search - Multiple keywords return relevant products
- **Type:** Positive
- **Priority:** High
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter "red cotton shirt" in the search bar.
  2. Click the search button.
- **Expected Result:** A list of red cotton shirts is displayed. Each product listed should have the words "red," "cotton," and "shirt" in its title or description.

#### ✅ TC-003: Positive Search - Keyword with mixed case returns products
- **Type:** Positive
- **Priority:** High
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter "lApTOp" in the search bar.
  2. Click the search button.
- **Expected Result:** A list of laptops is displayed, same as TC-001. The search should be case-insensitive.

#### ❌ TC-004: Negative Search - Invalid keyword returns no products
- **Type:** Negative
- **Priority:** High
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter "xyz123invalidproduct" in the search bar.
  2. Click the search button.
- **Expected Result:** A message is displayed indicating that no products were found matching the search criteria.

#### ❌ TC-005: Negative Search - Empty keyword returns error or all products
- **Type:** Negative
- **Priority:** High
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Leave the search bar empty.
  2. Click the search button.
- **Expected Result:** Either a message is displayed indicating that a keyword is required, or all products are displayed.

#### ❌ TC-006: Negative Search - Special characters handling
- **Type:** Negative
- **Priority:** High
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter "!@#$%" in the search bar.
  2. Click the search button.
- **Expected Result:** A message is displayed indicating that no products were found, or the special characters are stripped and the search continues.

#### ⚠️ TC-007: Edge Case - Very long keyword
- **Type:** Edge Case
- **Priority:** Medium
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter a keyword that exceeds the maximum allowed length (e.g., 255 characters).
  2. Click the search button.
- **Expected Result:** The system either truncates the keyword to the maximum allowed length and performs the search, or displays an error message indicating the keyword is too long.

#### ⚠️ TC-008: Edge Case - Keyword with HTML tags
- **Type:** Edge Case
- **Priority:** Medium
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter a keyword containing HTML tags, such as `<script>alert('test')</script>`.
  2. Click the search button.
- **Expected Result:** The system either strips the HTML tags, escapes them to prevent security vulnerabilities, or displays an error message.

#### ⚠️ TC-009: Edge Case - SQL injection attempts
- **Type:** Edge Case
- **Priority:** Medium
- **Preconditions:** User is on the product search page.
- **Test Steps:**
  1. Enter a keyword containing SQL injection attempts, such as `laptop' OR '1'='1`.
  2. Click the search button.
- **Expected Result:** The system neutralizes the SQL injection attempt and either returns results as if the injection was not present, or displays an error message.

---
## �🔧 Customization

- **Change the model**: Edit `model="gemini-2.0-flash"` in `agent.py` (e.g., `gemini-1.5-pro`)
- **Add more tools**: Define new functions and add them to the `tools=[...]` list in `agent.py`
- **Modify the system prompt**: Edit the `instruction="""..."""` block in `agent.py`
