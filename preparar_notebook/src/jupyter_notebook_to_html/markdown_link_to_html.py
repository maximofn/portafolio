import re

def markdown_to_html_external_link(markdown_link: str) -> str:
    """
    Converts an external Markdown link to an HTML link.

    Args:
        markdown_link: The Markdown link string (e.g., "[Link text](https://example.com)").

    Returns:
        The HTML link string (e.g., "<a href="https://example.com">Link text</a>").
    """
    match = re.match(r"\[(.*?)\]\((https?://.*?)\)", markdown_link)
    if match:
        link_text = match.group(1)
        link_url = match.group(2)
        return f'<a href="{link_url}">{link_text}</a>'
    return markdown_link # Return original if not a valid external link

def markdown_to_html_internal_link(markdown_link: str, language: str = "ES") -> str:
    """
    Converts an internal Markdown link to an HTML link.

    Args:
        markdown_link: The Markdown link string (e.g., "[Link text](/path/to/page)").

    Returns:
        The HTML link string (e.g., "<a href="/path/to/page">Link text</a>").
    """
    match = re.match(r"\[(.*?)\]\((/.*?)\)", markdown_link)
    if match:
        link_text = match.group(1)
        link_url = match.group(2)
        if language == "EN":
            link_url = f"/en{link_url}"
        elif language == "PT":
            link_url = f"/pt{link_url}"
        return f'<a href="{link_url}">{link_text}</a>'
    return markdown_link # Return original if not a valid internal link
