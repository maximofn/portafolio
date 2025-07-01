from markdown_to_html.generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns

def markdown_to_html_convert(list_of_contents):
    for item in list_of_contents:
        if "markdown" in item:
            markdown_content = item["markdown"]
            list_of_specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
            print(list_of_specific_markdowns)
        elif "input_code" in item:
            code_content = item["input_code"]
            print(code_content)
        elif "output_code" in item:
            code_content = item["output_code"]
            print(code_content)

    return markdown_content
