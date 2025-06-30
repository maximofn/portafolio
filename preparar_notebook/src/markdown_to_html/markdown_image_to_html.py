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
    # Regex to find markdown images: ![alt text](url)
    # - !\[ captures the starting "!["
    # - (.*?) captures the alt text (non-greedy) inside the square brackets. This is group 1.
    # - \] captures the closing "]"
    # - \( captures the opening "(" for the URL
    # - (.*?) captures the URL (non-greedy) inside the parentheses. This is group 2.
    # - \) captures the closing ")"
    image_regex = r"!\[(.*?)\]\((.*?)\)"

    def replace_match(match):
        alt_text = match.group(1)
        url = match.group(2)

        # If URL is empty, it's considered malformed for conversion to a valid <img> tag,
        # so return the original matched string.
        if not url:
            return match.group(0)

        return f'<img src="{url}" alt="{alt_text}">'

    # re.sub will find all non-overlapping matches of image_regex in markdown_text
    # and replace them according to the output of the replace_match function.
    html_output = re.sub(image_regex, replace_match, markdown_text)

    return html_output

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
