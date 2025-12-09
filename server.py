"""
Flask API Server for Exercise System
Serves exercises with proper resource handling
"""
from flask import Flask, jsonify, send_from_directory, abort, request
from werkzeug.utils import safe_join
import os
import mimetypes

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.abspath('serverstr')  # Absolute path for security
GLOBAL_RES_DIR = os.path.abspath('res')   # Global resources directory

# Security: Ensure directories exist
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(GLOBAL_RES_DIR, exist_ok=True)


def validate_path(base, *parts):
    """
    Safely join paths and validate they're within base directory
    Prevents directory traversal attacks
    """
    try:
        full_path = safe_join(base, *parts)
        if full_path and os.path.commonpath([base, full_path]) == base:
            return full_path
    except (ValueError, TypeError):
        pass
    return None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Exercise API is running"
    })


@app.route('/api/exercises/<bucket>/<exercise_code>', methods=['GET'])
def get_exercise(bucket, exercise_code):
    """
    Get exercise with all its metadata
    
    Returns:
        {
            "markdown": "content of index.md",
            "has_tests": true/false,
            "has_solution": true/false,
            "resource_base_url": "http://localhost:5000/api/exercises/{bucket}/{code}/res",
            "files": ["tests.toml", "solution.py", ...]
        }
    """
    # Build and validate directory path
    dir_path = validate_path(BASE_DIR, bucket, exercise_code)
    
    if not dir_path or not os.path.isdir(dir_path):
        return jsonify({
            "error": "Exercise not found",
            "bucket": bucket,
            "exercise_code": exercise_code
        }), 404
    
    # Check for index.md
    index_path = os.path.join(dir_path, "index.md")
    if not os.path.isfile(index_path):
        return jsonify({
            "error": "Exercise index.md not found",
            "bucket": bucket,
            "exercise_code": exercise_code
        }), 404
    
    # Read markdown content
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        return jsonify({
            "error": f"Failed to read index.md: {str(e)}"
        }), 500
    
    # Get list of available files
    try:
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    except Exception:
        files = []
    
    # Check for specific files
    has_tests = "tests.toml" in files
    has_solution = "solution.py" in files
    has_local_res = os.path.isdir(os.path.join(dir_path, "res"))
    
    # Build resource base URL
    resource_base_url = request.url_root.rstrip('/') + f"/api/exercises/{bucket}/{exercise_code}/res"
    
    # Process markdown to fix resource paths
    processed_markdown = _process_markdown_resources(
        markdown_content,
        resource_base_url,
        has_local_res
    )
    
    return jsonify({
        "markdown": processed_markdown,
        "has_tests": has_tests,
        "has_solution": has_solution,
        "has_local_resources": has_local_res,
        "resource_base_url": resource_base_url,
        "files": files
    })


@app.route('/api/exercises/<bucket>/<exercise_code>/<filename>', methods=['GET'])
def get_exercise_file(bucket, exercise_code, filename):
    """
    Get a specific file from an exercise (e.g., tests.toml, solution.py)
    """
    # Validate paths
    dir_path = validate_path(BASE_DIR, bucket, exercise_code)
    if not dir_path:
        abort(404)
    
    file_path = validate_path(dir_path, filename)
    if not file_path or not os.path.isfile(file_path):
        abort(404)
    
    # Get mimetype
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    return send_from_directory(dir_path, filename, mimetype=mimetype)


@app.route('/api/exercises/<bucket>/<exercise_code>/res/<path:filename>', methods=['GET'])
def get_exercise_resource(bucket, exercise_code, filename):
    """
    Get a resource file from exercise's local res/ directory
    Priority: local res/ > global res/
    """
    # Try local res/ directory first
    dir_path = validate_path(BASE_DIR, bucket, exercise_code)
    if dir_path:
        local_res_path = validate_path(dir_path, "res", filename)
        if local_res_path and os.path.isfile(local_res_path):
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            return send_from_directory(os.path.join(dir_path, "res"), filename, mimetype=mimetype)
    
    # Fall back to global res/ directory
    global_res_path = validate_path(GLOBAL_RES_DIR, filename)
    if global_res_path and os.path.isfile(global_res_path):
        mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        return send_from_directory(GLOBAL_RES_DIR, filename, mimetype=mimetype)
    
    abort(404)


@app.route('/api/res/<path:filename>', methods=['GET'])
def get_global_resource(filename):
    """
    Get a resource from global res/ directory
    For backward compatibility
    """
    file_path = validate_path(GLOBAL_RES_DIR, filename)
    
    if not file_path or not os.path.isfile(file_path):
        abort(404)
    
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    return send_from_directory(GLOBAL_RES_DIR, filename, mimetype=mimetype)


@app.route('/api/exercises', methods=['GET'])
def list_exercises():
    """
    List all available exercises organized by bucket
    
    Returns:
        {
            "buckets": {
                "default": ["001", "002", ...],
                "custom": ["001", ...]
            }
        }
    """
    buckets = {}
    
    try:
        for bucket_name in os.listdir(BASE_DIR):
            bucket_path = os.path.join(BASE_DIR, bucket_name)
            if os.path.isdir(bucket_path):
                exercises = [
                    name for name in os.listdir(bucket_path)
                    if os.path.isdir(os.path.join(bucket_path, name)) and
                    os.path.isfile(os.path.join(bucket_path, name, "index.md"))
                ]
                if exercises:
                    buckets[bucket_name] = sorted(exercises)
    except Exception as e:
        return jsonify({"error": f"Failed to list exercises: {str(e)}"}), 500
    
    return jsonify({"buckets": buckets})


def _process_markdown_resources(markdown_content, resource_base_url, has_local_res):
    """
    Process markdown to fix resource paths
    
    Converts:
        - res/image.png -> {resource_base_url}/image.png
        - ![alt](res/image.png) -> ![alt]({resource_base_url}/image.png)
    """
    import re
    
    # Fix markdown image syntax: ![alt](res/...)
    markdown_content = re.sub(
        r'!\[([^\]]*)\]\(res/([^)]+)\)',
        rf'![\1]({resource_base_url}/\2)',
        markdown_content
    )
    
    # Fix HTML img tags: <img src="res/...">
    markdown_content = re.sub(
        r'<img\s+([^>]*\s+)?src=["\']res/([^"\']+)["\']',
        rf'<img \1src="{resource_base_url}/\2"',
        markdown_content
    )
    
    # Fix plain res/ references in text (less common)
    markdown_content = re.sub(
        r'\bres/(\S+)',
        rf'{resource_base_url}/\1',
        markdown_content
    )
    
    return markdown_content


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Resource not found",
        "message": str(error)
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == "__main__":
    print("=" * 60)
    print("Exercise API Server Starting")
    print("=" * 60)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Global Resources: {GLOBAL_RES_DIR}")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health")
    print("  GET  /api/exercises")
    print("  GET  /api/exercises/<bucket>/<code>")
    print("  GET  /api/exercises/<bucket>/<code>/<file>")
    print("  GET  /api/exercises/<bucket>/<code>/res/<file>")
    print("  GET  /api/res/<file>")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)