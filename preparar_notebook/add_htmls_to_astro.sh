#!/bin/bash

html_file=$1
title=$2
end_url=$3
description=$4
keywords=$5
languaje=$6
image=$7
image_width=$8
image_height=$9
image_extension=${10}
date=${11}

# Date time variable
date_time=$date+"T00:00:00Z"




# -------------------------------- Create astro file --------------------------------
echo -e "\tCREATING PAGE: $end_url.astro"
if [[ $languaje == "EN" ]]; then
    touch ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    touch ../portfolio/src/pages/pt-br/$end_url.astro
else
    touch ../portfolio/src/pages/$end_url.astro
fi
# --------------------------------------------------------------------------------------------



# -------------------------------- Header of the astro file --------------------------------
# Header file
header_file="---
import PostLayout from '@layouts/PostLayout.astro';

const { metadata_page } = await import('@portfolio/consts.json');
const { colors } = await import('@portfolio/consts.json');
const { svg_paths } = await import('@portfolio/consts.json');

const page_title = '$title';
const end_url = '$end_url';
const description = '$description';
const keywords = '$keywords';
const languaje = '$languaje';
const image_path = '$image';
const opening_brace = '{';
const closing_brace = '}';
---

<PostLayout 
    title={page_title}
    languaje={languaje}
    description={description}
    keywords={keywords}
    author={metadata_page.author}
    theme_color={colors.background_color}
    end_url={end_url}
    image_path={image_path}image_width="$image_width"
    image_height="$image_height"
    image_extension="$image_extension"
    article_date="$date_time"
>

  <section class=\"post-body-post\">"

# Add header
echo -e "\tADDING HEADER TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$header_file" > ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$header_file" > ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$header_file" > ../portfolio/src/pages/$end_url.astro
fi
# --------------------------------------------------------------------------------------------




# -------------------------------- Index with the headings of the html file -------------------
# Open div post-index
post_index="

    <div class=\"post-index\">
"

# Find lines starting with '<hX id="' where X is 1-6 and add them to the 'post_index' variable
echo -e "\tFINDING HEADINGS WITH ID ATTRIBUTES:"
while IFS= read -r line; do
    if grep -Eq '^<h[2-6] id="' <<< "$line"; then
        # This is an example of line: <h2 id="2.-%C2%BFQu%C3%A9-es-Pandas?">2. ¿Qué es Pandas?<a class="anchor-link" href="#2.-%C2%BFQu%C3%A9-es-Pandas?">¶</a></h2>

        # Get the anchor element
        anchor=$(echo "$line" | sed -E 's/.*(<a[^>]*>.*<\/a>).*/\1/')   # In an example achor is: <a class=anchor-link href=#2.-%C2%BFQu%C3%A9-es-Pandas?>¶</a>

        # Get the heading element
        anchor_position=$(echo "$line" | awk '{print index($0, "<a")}') # In an example anchor_position is: 57
        heading_element="${line:0:$anchor_position-1}"                  # In an example heading_element is: <h2 id=2.-%C2%BFQu%C3%A9-es-Pandas?>2. ¿Qué es Pandas?<a
        # if heading_element ends with "<a" then remove it
        if [[ "${heading_element: -2}" == "<a" ]]; then
            heading_element="${heading_element:0:-2}"                   # In an example heading_element is: <h2 id=2.-%C2%BFQu%C3%A9-es-Pandas?>2. ¿Qué es Pandas?
        # if heading_element ends with "<" then remove it
        elif [[ "${heading_element: -1}" == "<" ]]; then
            heading_element="${heading_element:0:-1}"                   # In an example heading_element is: <h2 id=2.-%C2%BFQu%C3%A9-es-Pandas?>2. ¿Qué es Pandas
        fi
        heading_element+="${line: -5}"                                  # In an example heading_element is: <h2 id=2.-%C2%BFQu%C3%A9-es-Pandas?>2. ¿Qué es Pandas?</h2>

        # Remove id attribute from heading element
        first_closing_tag=$(echo "$heading_element" | awk '{print index($0, ">")}') # In an example first_closing_tag is: 36
        cleaned_heading_element="${heading_element:0:3}"                    # In an example cleaned_heading_element is: <h2
        cleaned_heading_element+=">"                                        # In an example cleaned_heading_element is: <h2>
        cleaned_heading_element+="${heading_element:$first_closing_tag}"    # In an example cleaned_heading_element is: <h2>2. ¿Qué es Pandas?</h2>

        # Create modified line
        modified_line="      ${anchor:0:-5}"              # In an example modified_line is: <a class=anchor-link href=#2.-%C2%BFQu%C3%A9-es-Pandas?>
        modified_line+="$cleaned_heading_element"   # In an example modified_line is: <a class=anchor-link href=#2.-%C2%BFQu%C3%A9-es-Pandas?><h2>2. ¿Qué es Pandas?</h2>
        modified_line+="</a>"                       # In an example modified_line is: <a class=anchor-link href=#2.-%C2%BFQu%C3%A9-es-Pandas?><h2>2. ¿Qué es Pandas?</h2></a>

        # Add modified line to post_index
        post_index+="$modified_line
"
    fi
done < "$html_file"

# Close div post-index
post_index+="    </div>

"

# Add html index
echo -e "\tADDING HTML INDEX TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$post_index" >> ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$post_index" >> ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$post_index" >> ../portfolio/src/pages/$end_url.astro
fi
# --------------------------------------------------------------------------------------------



# -------------------------------- Content of the astro file --------------------------------
post_content+="    <div class=\"post-content\">"

# Change all '{' to '{opening_brace}' into html_file
echo -e "\tCHANGE ALL '{' TO '{opening_brace}' INTO $html_file"
sed -i 's/{/{opening_brace}/g' $html_file

# Change all '<section' to '\<section' into html_file
echo -e "\tCHANGE ALL '<section' TO '\ n<section' INTO $html_file"
sed -i 's/<section/\n<section/g' $html_file

# Change all '¶' to '<img class="link-img" alt="link-svg" src={svg_paths.link_svg_path}/>' into html_file
echo -e "\tCHANGE ALL '¶' TO '<img class="link-img" alt="link-svg" src={svg_paths.link_svg_path}/>' INTO $html_file"
sed -i 's/¶/<img class="link-img" alt="link-svg" src=\{svg_paths.link_svg_path\}\/>/g' $html_file

# Add six spaces at start of each line in html_file
# echo -e "\tADD SIX SPACES AT START OF EACH LINE IN $html_file"
# sed -i 's/^/      /' $html_file

# Add html content
echo -e "\tADDING HTML CONTENT TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$post_content" >> ../portfolio/src/pages/en/$end_url.astro
    cat $html_file >> ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$post_content" >> ../portfolio/src/pages/pt-br/$end_url.astro
    cat $html_file >> ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$post_content" >> ../portfolio/src/pages/$end_url.astro
    cat $html_file >> ../portfolio/src/pages/$end_url.astro
fi
# --------------------------------------------------------------------------------------------



# -------------------------------- Botom of the astro file --------------------------------
botom_file="
    </div>

  </section>

</PostLayout>"

# Add botom
echo -e "\tADDING BOTOM TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$botom_file" >> ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$botom_file" >> ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$botom_file" >> ../portfolio/src/pages/$end_url.astro
fi
# --------------------------------------------------------------------------------------------
