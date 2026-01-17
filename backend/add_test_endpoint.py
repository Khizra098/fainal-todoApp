"""Test script to add a simple test endpoint to main.py temporarily"""
import os
import sys

# Read the current main.py
main_py_path = "src/main.py"
with open(main_py_path, 'r') as f:
    content = f.read()

# Check if test endpoint already exists
if "/test-endpoint" not in content:
    # Add a simple test endpoint at the end before the if __name__ == "__main__":
    lines = content.split('\n')

    # Find where to insert the test endpoint (before the if __name__ == "__main__":)
    insert_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('if __name__ == "__main__":'):
            insert_idx = i
            break

    if insert_idx != -1:
        # Insert a simple test endpoint before the if statement
        test_endpoint = [
            "",
            "@app.get(\"/test-endpoint\")",
            "def test_endpoint():",
            "    return {\"message\": \"Test endpoint working\"}",
            ""
        ]

        # Insert the new lines
        for i, new_line in enumerate(test_endpoint):
            lines.insert(insert_idx + i, new_line)

        # Write back to file
        with open(main_py_path, 'w') as f:
            f.write('\n'.join(lines))

        print("Added test endpoint to main.py")
    else:
        print("Could not find insertion point in main.py")
else:
    print("Test endpoint already exists")