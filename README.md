# 🧪 ADK Test Case Generator

An advanced AI-powered test case generation system using **Google Agent Development Kit (ADK)** with **Gemini 2.0-Flash**.

Supports **two powerful modes**:
- 📖 **Story Mode**: Generate test cases from user stories  
- 🌐 **Website Mode**: Crawl websites, extract UI elements, and generate context-aware test cases

---

## 🎯 Key Features

✅ **Dual Mode Generation**
- Story-based test case generation (BDD/Gherkin format)
- Website crawling with AI-powered UI analysis
- Intelligent action graph building from HTML

✅ **Comprehensive Test Coverage**
- Positive test cases (happy paths)
- Negative test cases (error handling, validation)  
- Edge cases (boundary conditions, security testing)

✅ **Smart UI Analysis**
- Automatic page type detection (search, product, login, cart, etc.)
- Element extraction (buttons, inputs, dropdowns, links, forms)
- User flow mapping per page type

✅ **Professional Output**
- Markdown report generation ready for test management tools
- Test case download functionality
- Structured test format with IDs, priorities, and detailed steps

---

## 📁 Project Structure

```
testcase-adk/
├── testcase_agent/              # ADK Agent
│   ├── agent.py                # Agent with 6 integrated tools
│   ├── __init__.py
│   └── .env                     # Your Google API key
├── tools/                       # Reusable tool library
│   ├── crawl_tool.py           # Website crawling (Crawl4AI)
│   ├── ui_extractor.py         # UI element extraction
│   ├── ui_graph_builder.py     # Action flow building
│   └── __init__.py
├── main.py                      # CLI interface
├── requirements.txt
├── README.md
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- pip
- Google API Key (free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey))

### Setup

```bash
# Clone repository
git clone https://github.com/sankettt24/testcase-adk.git
cd testcase-adk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GOOGLE_API_KEY=your_api_key_here" > testcase_agent/.env
```

---

## 🚀 Quick Start

### Option 1: ADK Web Interface (Recommended)
```bash
adk web
```
Then select `testcase_agent` from the dropdown and interact naturally:

**Story Mode:**
```
As a customer, I want to search for products so that I can find what I need
```

**Website Mode:**
```
Please crawl https://example.com and generate test cases for:
As a customer, I want to add products to my cart
```

### Option 2: CLI Interactive Mode
```bash
python main.py
```

Choose:
1. **Story-based** - Paste a user story
2. **Website-based** - Enter a URL
3. Exit

### Option 3: ADK CLI
```bash
adk run testcase_agent
```

---

## 📋 How It Works

### 📖 Story Mode
**Input:** User story in BDD format

```
As a customer, I want to search for products so that I can find what I need
```

**Agent Actions:**
1. Parses story → Actor: "customer", Action: "search for products", Goal: "find what I need"
2. Generates test cases (positive, negative, edge)
3. Formats as markdown report

**Output:** 9+ test cases
```
✅ TC-P001: Verify search with valid keyword
❌ TC-N001: Verify error handling with empty input
⚠️ TC-E001: Verify behavior with special characters
```

### 🌐 Website Mode
**Input:** Website URL + optional user story

```
URL: https://example.com
User Story: As a customer, I want to add items to my cart
```

**Agent Actions:**
1. Crawls website (Crawl4AI)
2. Extracts UI elements (buttons, forms, inputs, links)
3. Builds action graph (page type, flows, interactions)
4. Generates context-specific test cases
5. Formats as markdown

**Output:** 9+ context-aware test cases
```
Page Type: Product Page
Available Actions: select_size, select_color, add_to_cart
User Flows: [add_to_cart, view_cart, checkout]

Generated Test Cases:
✅ TC-P001: Verify user can select product size and add to cart
❌ TC-N001: Verify error handling when adding out-of-stock item
⚠️ TC-E001: Verify behavior with maximum quantity
```

---

## 🔧 Built-in Tools

The ADK agent has 6 intelligent tools:

| Tool | Mode | Purpose |
|------|------|---------|
| `parse_user_story` | Story | Extract actor, action, goal from story |
| `generate_test_cases` | Story | Create test cases (positive, negative, edge) |
| `format_test_cases_as_markdown` | Story | Format test cases as markdown report |
| `crawl_website` | Website | Fetch and parse website content |
| `extract_ui_elements_tool` | Website | Identify buttons, forms, inputs, links |
| `build_ui_action_graph` | Website | Build user interaction flows |

**The agent intelligently decides which tools to use!**

---

## 💬 Usage Examples

### Example 1: Story-Based Test Generation

**Input:**
```
As a student, I want to search for courses, so that I can find classes of interest
```

**Agent Process:**
```
1. Parsing story...
   Actor: student
   Action: search for courses
   Goal: find classes of interest

2. Generating test cases...
3. Formatting report...
```

**Output:**
```markdown
# Test Cases Report

**Total Test Cases:** 9

## TC-P001: Valid Search
- Type: Positive
- Priority: High
- Description: Verify search with valid course keyword
- Preconditions: Student is on search page
- Steps:
  1. Enter "Computer Science" in search
  2. Click Search button
  3. Verify results displayed
- Expected Result: List of CS courses appears

## TC-N001: Empty Search
- Type: Negative
- Priority: High
- Description: Verify error handling with empty input
- Preconditions: Student is on search page
- Steps:
  1. Leave search empty
  2. Click Search button
  3. Observe system response
- Expected Result: Error message displayed

## TC-E001: Special Characters
- Type: Edge
- Priority: Medium
- Description: Verify behavior with special characters
- Preconditions: Student is on search page
- Steps:
  1. Enter "@#$%" in search
  2. Click Search button
- Expected Result: Either no results or special chars stripped
```

### Example 2: Website-Based Test Generation

**Input:**
```
URL: https://example.com/shop
User Story: As a customer, I want to add products to my cart
```

**Agent Process:**
```
1. Crawling website...
2. Extracting UI elements:
   - Buttons: [Add to Cart, Buy Now, Continue Shopping]
   - Forms: [Search, Filter]
   - Inputs: [Quantity]
   - Dropdowns: [Size, Color]

3. Building action graph:
   Page Type: Product Page
   Available Actions: select_size, select_color, add_to_cart
   User Flows: add_to_cart → view_cart → checkout

4. Generating context-specific test cases...
5. Formatting report...
```

**Output:**
```markdown
# Test Cases Report
URL: https://example.com/shop
Page Type: Product Page

## TC-P001: Add Product to Cart
- Type: Positive
- Priority: High
- Description: Verify user can add product with size and color selection
- Preconditions: User on product page, product in stock
- Steps:
  1. Select size from dropdown
  2. Select color from dropdown
  3. Click Add to Cart button
  4. Verify cart count increases
- Expected Result: Product added to cart, success message displayed

## TC-N001: Add Out-of-Stock Product
- Type: Negative
- Priority: High
- Description: Verify error handling for out-of-stock items
- Preconditions: User on product page, product is out of stock
- Steps:
  1. Observe Add to Cart button (should be disabled)
  2. Attempt to add product
- Expected Result: Error message, product not added

## TC-E001: Maximum Quantity
- Type: Edge
- Priority: Medium
- Description: Verify behavior at quantity boundaries
- Preconditions: User on product page
- Steps:
  1. Set quantity to maximum allowed
  2. Attempt to increase beyond maximum
  3. Click Add to Cart
- Expected Result: Quantity capped at maximum, success message
```

---

## 📊 Page Type Detection

The system automatically detects page type and generates relevant flows:

| Page Type | Detected By | Generated Flows | Test Focus |
|-----------|------------|-----------------|-----------|
| **Search Page** | Search input | Enter query, submit, filter, sort, view results | Form submission, filtering, display |
| **Product Page** | Product info + Add button | Select attributes, add to cart, view reviews | Selection, inventory, cart actions |
| **Cart Page** | Cart/basket element | View items, update quantity, apply coupon, checkout | Quantity changes, pricing, navigation |
| **Login Page** | Login form | Enter credentials, reset password, remember me | Authentication, validation, recovery |
| **Navigation Hub** | Many links (>20) | Navigate to sections, explore categories | Link accessibility, navigation flows |

---

## 🐳 Docker Deployment

### Local Development
```bash
docker-compose up
```

### Production Deployment
```bash
docker build -t testcase-adk .
docker run -p 5000:8000 -e GOOGLE_API_KEY=<key> testcase-adk
```

---

## ⚙️ Customization

### Change the Model
Edit `testcase_agent/agent.py`:
```python
root_agent = Agent(
    model="gemini-2.0-flash",  # Change to: gemini-1.5-pro, etc.
    ...
)
```

### Add Custom Tools
1. Create tool function in `tools/` directory
2. Register in `testcase_agent/agent.py` tools list:
```python
root_agent = Agent(
    ...
    tools=[
        parse_user_story,
        generate_test_cases,
        format_test_cases_as_markdown,
        crawl_website,
        extract_ui_elements_tool,
        build_ui_action_graph,
        your_new_tool  # Add here
    ]
)
```

### Modify Instructions
Edit the `instruction=""` prompt in `testcase_agent/agent.py` to customize agent behavior.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Check `.env` file exists in `testcase_agent/` |
| `ModuleNotFoundError: crawl4ai` | Run `pip install crawl4ai` |
| Website crawl timeout | Website might be slow; increase timeout in `crawl_tool.py` |
| No UI elements extracted | Website might use JavaScript; enable JS rendering |
| Test cases are generic | Provide more specific user story details |

---

## 📈 Performance

- **Max crawl size:** 10 MB
- **Max test cases:** 100+ per generation
- **Crawl timeout:** 30 seconds
- **API timeout:** 60 seconds

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🔗 Resources

- [Google ADK Documentation](https://github.com/google/google-adk)
- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Gemini API Guide](https://ai.google.dev)
- [Google AI Studio](https://aistudio.google.com)

---

## ❓ Support

- **Issues:** [GitHub Issues](https://github.com/sankettt24/testcase-adk/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sankettt24/testcase-adk/discussions)
- **Email:** support@example.com

---

**Made with ❤️ using Google ADK + Gemini 2.0-Flash**
