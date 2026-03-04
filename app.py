import json
import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import traceback

load_dotenv()

# Import original tools
from testcase_agent.agent import (
    parse_user_story,
    generate_test_cases,
    format_test_cases_as_markdown
)

# Import new tools for URL-based generation
from agents.testcase_agent import (
    crawl_website,
    extract_ui,
    build_graph,
    generate_test_cases_from_ui,
    format_test_cases_markdown
)

app = Flask(__name__)
CORS(app)


# ===== ORIGINAL STORY-BASED ENDPOINTS =====

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def serve_home():
    """Serve the main HTML interface (will have dual-mode support)."""
    return render_template_string(get_html_template())


@app.route('/api/parse-story', methods=['POST'])
def parse_story():
    """Parse user story - Original endpoint."""
    try:
        data = request.get_json()
        user_story = data.get('user_story', '').strip()
        
        if not user_story:
            return jsonify({'error': 'User story is required'}), 400
        
        parsed = parse_user_story(user_story)
        return jsonify(parsed)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/generate-testcases', methods=['POST'])
def generate_testcases():
    """Generate test cases from user story - Original endpoint."""
    try:
        data = request.get_json()
        user_story = data.get('user_story', '').strip()
        test_types = data.get('test_types', 'positive,negative,edge')
        
        if not user_story:
            return jsonify({'error': 'User story is required'}), 400
        
        # Parse story
        parsed = parse_user_story(user_story)
        
        # Generate test cases
        test_cases = generate_test_cases(user_story, test_types)
        
        # Format as markdown
        formatted = format_test_cases_as_markdown(json.dumps(test_cases))
        
        return jsonify({
            'parsed': parsed,
            'test_cases': test_cases,
            'markdown': formatted.get('markdown', '')
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


# ===== NEW URL-BASED CRAWLING ENDPOINTS =====

@app.route('/api/crawl-website', methods=['POST'])
def crawl_website_endpoint():
    """Crawl a website and extract content."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = crawl_website(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/extract-ui-elements', methods=['POST'])
def extract_ui_elements():
    """Extract UI elements from HTML content."""
    try:
        data = request.get_json()
        html_content = data.get('html', '')
        markdown_content = data.get('markdown', '')
        
        if not html_content:
            return jsonify({'error': 'HTML content is required'}), 400
        
        result = extract_ui(html_content, markdown_content)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/build-ui-graph', methods=['POST'])
def build_ui_graph_endpoint():
    """Build UI action graph from extracted elements."""
    try:
        data = request.get_json()
        elements_data = data.get('elements', {})
        
        result = build_graph(elements_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/generate-testcases-from-url', methods=['POST'])
def generate_testcases_from_url():
    """Full workflow: Crawl URL -> Extract UI -> Build Graph -> Generate Test Cases."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        user_story = data.get('user_story', '').strip()
        
        if not url:
            return jsonify({'error': 'Website URL is required'}), 400
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Step 1: Crawl website
        crawl_result = crawl_website(url)
        if not crawl_result.get('success'):
            return jsonify({'error': f'Failed to crawl website: {crawl_result.get("error")}'}), 400
        
        # Step 2: Extract UI elements
        html_content = crawl_result.get('html', '')
        markdown_content = crawl_result.get('markdown', '')
        elements_result = extract_ui(html_content, markdown_content)
        elements_data = elements_result.get('extracted_elements', {})
        
        # Step 3: Build UI graph
        graph_result = build_graph(elements_data)
        ui_graph = graph_result.get('ui_graph', {})
        
        # Step 4: Generate test cases
        if user_story:
            test_cases_result = generate_test_cases_from_ui(user_story, ui_graph, elements_data)
        else:
            # Generate generic test cases
            test_cases_result = generate_test_cases_from_ui(
                f"As a user, I want to interact with {url}",
                ui_graph,
                elements_data
            )
        
        # Step 5: Format as markdown
        markdown_result = format_test_cases_markdown(test_cases_result)
        
        return jsonify({
            'success': True,
            'url': url,
            'crawl_data': {
                'markdown_preview': markdown_content[:500] + '...' if len(markdown_content) > 500 else markdown_content,
                'html_size': len(html_content)
            },
            'elements': elements_data,
            'ui_graph': ui_graph,
            'test_cases': test_cases_result,
            'markdown': markdown_result.get('markdown', '')
        })
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


def get_html_template():
    """HTML template with dual-mode support (Story-based and URL-based)."""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Case Generator - ADK Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        .mode-selector {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .mode-btn {
            padding: 12px 30px;
            border: 2px solid white;
            background: transparent;
            color: white;
            cursor: pointer;
            border-radius: 25px;
            font-size: 1em;
            transition: all 0.3s;
        }

        .mode-btn.active {
            background: white;
            color: #667eea;
            font-weight: bold;
        }

        .mode-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .content {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .card h2 {
            margin-bottom: 20px;
            color: #667eea;
            font-size: 1.5em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        .form-group textarea,
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            font-family: inherit;
            resize: none;
        }

        .form-group textarea:focus,
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .checkbox-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 0;
            font-weight: normal;
            cursor: pointer;
        }

        .checkbox-group input[type="checkbox"] {
            width: auto;
            padding: 0;
            cursor: pointer;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            transition: transform 0.2s;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .results {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .results h2 {
            margin-bottom: 20px;
            color: #667eea;
        }

        .results-scroll {
            max-height: 600px;
            overflow-y: auto;
            padding-right: 10px;
        }

        .results-scroll::-webkit-scrollbar {
            width: 8px;
        }

        .results-scroll::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 5px;
        }

        .results-scroll::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 5px;
        }

        .test-case {
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }

        .test-case.positive {
            border-left-color: #4caf50;
        }

        .test-case.negative {
            border-left-color: #f44336;
        }

        .test-case.edge {
            border-left-color: #ff9800;
        }

        .test-case h4 {
            margin-bottom: 8px;
            color: #333;
        }

        .test-case .meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }

        .test-case .meta span {
            margin-right: 15px;
        }

        .type-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 10px;
        }

        .type-badge.positive {
            background: #4caf50;
            color: white;
        }

        .type-badge.negative {
            background: #f44336;
            color: white;
        }

        .type-badge.edge {
            background: #ff9800;
            color: white;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .message {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .message.error {
            background: #ffebee;
            color: #c62828;
            border-left: 4px solid #f44336;
        }

        .message.success {
            background: #e8f5e9;
            color: #2e7d32;
            border-left: 4px solid #4caf50;
        }

        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            color: #1565c0;
        }

        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .btn-secondary {
            background: #e0e0e0;
            color: #333;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            flex: 1;
            font-weight: bold;
            transition: background 0.2s;
        }

        .btn-secondary:hover {
            background: #bdbdbd;
        }

        .hidden {
            display: none !important;
        }

        .mode-content {
            display: none;
        }

        .mode-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Test Case Generator</h1>
            <p>Generate comprehensive test cases using ADK Agent</p>
        </div>

        <div class="mode-selector">
            <button class="mode-btn active" onclick="switchMode('story')">📖 Story Mode</button>
            <button class="mode-btn" onclick="switchMode('url')">🌐 Website Mode</button>
        </div>

        <div class="content">
            <!-- STORY MODE INPUT -->
            <div id="story-mode" class="mode-content active">
                <div class="card">
                    <h2>📖 Story-Based Test Case Generation</h2>
                    
                    <div class="form-group">
                        <label for="user_story">User Story</label>
                        <textarea id="user_story" placeholder="Enter user story&#10;Example: As a customer, I want to search for products so that I can find what I need" rows="8"></textarea>
                    </div>

                    <div class="form-group">
                        <label>Test Types to Generate</label>
                        <div class="checkbox-group">
                            <label><input type="checkbox" name="test_type" value="positive" checked> ✅ Positive</label>
                            <label><input type="checkbox" name="test_type" value="negative" checked> ❌ Negative</label>
                            <label><input type="checkbox" name="test_type" value="edge" checked> ⚠️ Edge</label>
                        </div>
                    </div>

                    <button class="btn-primary" onclick="generateFromStory()">Generate Test Cases</button>
                </div>
            </div>

            <!-- URL MODE INPUT -->
            <div id="url-mode" class="mode-content hidden">
                <div class="card">
                    <h2>🌐 Website-Based Test Case Generation</h2>
                    
                    <div class="info-box">
                        <strong>💡 How it works:</strong> Provide a website URL and an optional user story. The agent will crawl the site, extract UI elements, and generate context-aware test cases.
                    </div>

                    <div class="form-group">
                        <label for="website_url">Website URL *</label>
                        <input type="url" id="website_url" placeholder="https://example.com" />
                    </div>

                    <div class="form-group">
                        <label for="url_user_story">User Story (Optional)</label>
                        <textarea id="url_user_story" placeholder="Example: As a customer, I want to add a product to my cart" rows="5"></textarea>
                    </div>

                    <button class="btn-primary" onclick="generateFromURL()">Crawl & Generate Test Cases</button>
                </div>
            </div>

            <!-- RESULTS SECTION -->
            <div class="results">
                <h2>Test Cases</h2>
                <div id="message-container"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating test cases...</p>
                </div>

                <div class="results-scroll" id="results" style="display: none;">
                    <div id="parsed-info" style="display: none;" class="info-box">
                        <strong>Parsed Story Components:</strong>
                        <p><strong>Actor:</strong> <span id="actor"></span></p>
                        <p><strong>Action:</strong> <span id="action"></span></p>
                        <p><strong>Goal:</strong> <span id="goal"></span></p>
                    </div>
                    <div id="test-cases-container"></div>
                </div>

                <div class="button-group" id="download-btn" style="display: none;">
                    <button class="btn-secondary" onclick="downloadResults()">⬇️ Download Markdown</button>
                    <button class="btn-secondary" onclick="clearResults()">🔄 Clear</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE_URL = window.location.origin;
        let currentResults = null;

        function switchMode(mode) {
            document.querySelectorAll('.mode-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.mode-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(mode + '-mode').classList.add('active');
            document.querySelector(`[onclick="switchMode('${mode}')"]`).classList.add('active');
            clearResults();
        }

        async function generateFromStory() {
            const story = document.getElementById('user_story').value.trim();
            if (!story) {
                showMessage('Please enter a user story', 'error');
                return;
            }

            const types = Array.from(document.querySelectorAll('input[name="test_type"]:checked'))
                .map(el => el.value)
                .join(',');

            if (!types) {
                showMessage('Please select at least one test type', 'error');
                return;
            }

            showLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/api/generate-testcases`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_story: story, test_types: types })
                });

                const data = await response.json();
                if (!response.ok) {
                    showMessage(data.error || 'Error generating test cases', 'error');
                    return;
                }

                currentResults = data;
                displayResults(data);
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }

        async function generateFromURL() {
            const url = document.getElementById('website_url').value.trim();
            if (!url) {
                showMessage('Please enter a website URL', 'error');
                return;
            }

            const userStory = document.getElementById('url_user_story').value.trim();

            showLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/api/generate-testcases-from-url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, user_story: userStory })
                });

                const data = await response.json();
                if (!response.ok) {
                    showMessage(data.error || 'Error generating test cases', 'error');
                    return;
                }

                currentResults = data;
                displayResults(data);
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }

        function displayResults(data) {
            const container = document.getElementById('test-cases-container');
            const results = document.getElementById('results');
            const messages = document.getElementById('message-container');
            
            messages.innerHTML = '';
            
            if (data.parsed) {
                const parsed = data.parsed;
                document.getElementById('actor').textContent = parsed.actor || 'Unknown';
                document.getElementById('action').textContent = parsed.action || 'Unknown';
                document.getElementById('goal').textContent = parsed.goal || 'Unknown';
                document.getElementById('parsed-info').style.display = 'block';
            }

            let testCases = [];
            if (data.test_cases && data.test_cases.test_cases) {
                testCases = data.test_cases.test_cases;
            } else if (data.test_cases && Array.isArray(data.test_cases)) {
                testCases = data.test_cases;
            }

            if (testCases.length === 0) {
                messages.innerHTML = '<div class="message error">No test cases found</div>';
                return;
            }

            container.innerHTML = testCases.map(tc => `
                <div class="test-case ${tc.type || 'positive'}">
                    <h4>${tc.id || 'N/A'}: ${tc.title || 'No title'}</h4>
                    <div class="meta">
                        <span class="type-badge ${tc.type || 'positive'}">${(tc.type || 'Unknown').toUpperCase()}</span>
                        <span>Priority: <strong>${tc.priority || 'N/A'}</strong></span>
                    </div>
                    <p><strong>Description:</strong> ${tc.description || 'N/A'}</p>
                    <p><strong>Preconditions:</strong></p>
                    <ul style="margin-left: 20px; margin-bottom: 10px;">
                        ${Array.isArray(tc.preconditions) ? 
                            tc.preconditions.map(pre => `<li>${pre}</li>`).join('') : 
                            `<li>${tc.preconditions || 'N/A'}</li>`}
                    </ul>
                    <p><strong>Steps:</strong></p>
                    <ol style="margin-left: 20px; margin-bottom: 10px;">
                        ${Array.isArray(tc.steps) ? 
                            tc.steps.map(step => `<li>${step}</li>`).join('') : 
                            `<li>${tc.steps || 'N/A'}</li>`}
                    </ol>
                    <p><strong>Expected Result:</strong> ${tc.expected_result || 'N/A'}</p>
                </div>
            `).join('');

            results.style.display = 'block';
            document.getElementById('download-btn').style.display = 'flex';
            showMessage(`Generated ${testCases.length} test cases`, 'success');
        }

        function downloadResults() {
            if (!currentResults) return;

            let markdown = currentResults.markdown || '';
            if (!markdown && currentResults.test_cases) {
                markdown = generateMarkdown(currentResults);
            }

            const blob = new Blob([markdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `test-cases-${new Date().toISOString().split('T')[0]}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function generateMarkdown(data) {
            let md = '# Test Cases Report\n\n';
            
            let testCases = [];
            if (data.test_cases && data.test_cases.test_cases) {
                testCases = data.test_cases.test_cases;
            } else if (data.test_cases && Array.isArray(data.test_cases)) {
                testCases = data.test_cases;
            }

            md += `**Total: ${testCases.length} test cases**\n\n`;

            testCases.forEach(tc => {
                const icon = {'positive': '✅', 'negative': '❌', 'edge': '⚠️'}[tc.type] || '📝';
                md += `## ${icon} ${tc.id}: ${tc.title}\n`;
                md += `- **Type:** ${tc.type}\n`;
                md += `- **Priority:** ${tc.priority}\n`;
                md += `- **Description:** ${tc.description}\n`;
                md += `- **Preconditions:** ${Array.isArray(tc.preconditions) ? tc.preconditions.join('; ') : tc.preconditions}\n`;
                md += `- **Steps:**\n`;
                (Array.isArray(tc.steps) ? tc.steps : [tc.steps]).forEach((step, i) => {
                    md += `  ${i + 1}. ${step}\n`;
                });
                md += `- **Expected Result:** ${tc.expected_result}\n\n`;
            });

            return md;
        }

        function clearResults() {
            document.getElementById('results').style.display = 'none';
            document.getElementById('download-btn').style.display = 'none';
            document.getElementById('test-cases-container').innerHTML = '';
            document.getElementById('message-container').innerHTML = '';
            currentResults = null;
        }

        function showMessage(message, type) {
            const container = document.getElementById('message-container');
            container.innerHTML = `<div class="message ${type}">${message}</div>`;
        }

        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }
    </script>
</body>
</html>
'''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
