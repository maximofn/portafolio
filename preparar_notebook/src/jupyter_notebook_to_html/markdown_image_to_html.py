import re

def markdown_image_to_html(markdown_text: str) -> str:
    """
    Converts markdown image syntax to HTML img tags in a given string.

    Args:
        markdown_text: A string that may contain markdown image syntax.
                       Example: "Some text ![alt text](image_url.png) and more text."

    Returns:
        A string with all valid markdown images converted to HTML img tags.
        If a markdown image syntax is malformed (e.g. missing URL), it's left unchanged.
    """
    
    def extract_balanced_url(text, start_pos):
        """
        Extract URL with balanced parentheses starting from start_pos (which should point to '(').
        Returns the URL content (without the outer parentheses) and the position after the closing ')'.
        Returns None, start_pos if no balanced URL is found.
        """
        if start_pos >= len(text) or text[start_pos] != '(':
            return None, start_pos
        
        paren_count = 0
        i = start_pos
        
        while i < len(text):
            if text[i] == '(':
                paren_count += 1
            elif text[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    # Found balanced closing parenthesis
                    url = text[start_pos + 1:i]  # Extract content between parentheses
                    return url, i + 1
            i += 1
        
        # No balanced closing parenthesis found
        return None, start_pos
    
    def extract_alt_text(text, start_pos):
        """
        Extract alt text with potential nested brackets starting from start_pos (after '![').
        Returns the alt text and the position after the closing ']'.
        Returns None, start_pos if no valid alt text is found.
        """
        if start_pos >= len(text):
            return None, start_pos
        
        bracket_count = 0
        i = start_pos
        
        while i < len(text):
            if text[i] == '[':
                bracket_count += 1
            elif text[i] == ']':
                if bracket_count == 0:
                    # Found the closing bracket for alt text
                    alt_text = text[start_pos:i]
                    return alt_text, i + 1
                else:
                    bracket_count -= 1
            i += 1
        
        # No closing bracket found
        return None, start_pos
    
    result = markdown_text
    offset = 0
    
    # Find all ![...] patterns first
    i = 0
    while i < len(markdown_text):
        if i < len(markdown_text) - 1 and markdown_text[i:i+2] == '![':
            # Extract alt text with balanced brackets
            alt_text, alt_end_pos = extract_alt_text(markdown_text, i + 2)
            
            if alt_text is not None and alt_end_pos < len(markdown_text) and markdown_text[alt_end_pos] == '(':
                # We have ![alt_text](, now extract the URL
                url, url_end_pos = extract_balanced_url(markdown_text, alt_end_pos)
                
                if url is not None:
                    # Valid image syntax found
                    if url:  # Non-empty URL
                        # Build the replacement
                        original_text = markdown_text[i:url_end_pos]
                        replacement = f'<img src="{url}" alt="{alt_text}">'
                        
                        # Apply replacement with offset adjustment
                        result_start = i + offset
                        result_end = result_start + len(original_text)
                        result = result[:result_start] + replacement + result[result_end:]
                        
                        # Update offset for subsequent replacements
                        offset += len(replacement) - len(original_text)
                        
                        # Move past this match
                        i = url_end_pos
                        continue
                    # If URL is empty, leave the original text unchanged
        
        i += 1
    
    return result

if __name__ == '__main__':
    # Example Usage (for direct testing if run as a script)
    test_cases = [
        "![alt text](image.png)",
        "This is a test: ![alt text](http://example.com/image.jpg) and some more text.",
        "![](empty_alt.gif)",
        "![missing url]()",
        "Malformed: ![alt text(no_closing_url.png",
        "No image here.",
        "Multiple: ![alt1](url1.png) and ![alt2](url2.jpg) in one line.",
        "![alt with spaces](path/to/my image.jpeg)"
    ]

    for i, md in enumerate(test_cases):
        html = markdown_image_to_html(md)
        print(f"Test Case {i+1}:")
        print(f"  Markdown: {md}")
        print(f"  HTML    : {html}\n")

    # Test with a more complex string
    complex_md = "Hello ![logo](logo.png), welcome to the site. Here is another image: ![](another.jpg) and a malformed one ![oops()."
    print("Complex Test Case:")
    print(f"  Markdown: {complex_md}")
    print(f"  HTML    : {markdown_image_to_html(complex_md)}\n")
