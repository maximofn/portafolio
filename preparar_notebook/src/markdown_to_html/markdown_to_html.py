from generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns

def markdown_to_html_convert(list_of_contents):
    for item in list_of_contents:
        markdown_content = item["markdown"]
        list_of_specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        print(list_of_specific_markdowns)

    return markdown_content
