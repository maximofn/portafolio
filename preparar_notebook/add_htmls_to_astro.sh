#!/bin/bash

html_file=$1
title=$2
end_url=$3
description=$4
keywords=$5
languaje=$6
image=$7


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
    image_path={image_path}
>

<section class=\"post-body-post\">"

post_index="

<div class=\"post-index\">

"

# Find lines starting with '<hX id="' where X is 1-6 and add them to the 'post_index' variable
echo -e "\tFINDING HEADINGS WITH ID ATTRIBUTES:"
while IFS= read -r line; do
    if grep -Eq '^<h[1-6] id="' <<< "$line"; then
        post_index+="$line"
    fi
done < "$html_file"
post_index+="</div>"
post_index+=" "
post_index+="<div class=\"post-content\">"
post_index+=" "

botom_file="
</div>

</section>

</PostLayout>"

# Change all '{' to '{opening_brace}' into html_file
echo -e "\tCHANGE ALL '{' TO '{opening_brace}' INTO $html_file"
sed -i 's/{/{opening_brace}/g' $html_file

# Change all '<section' to '\<section' into html_file
echo -e "\tCHANGE ALL '<section' TO '\ n<section' INTO $html_file"
sed -i 's/<section/\n<section/g' $html_file

# Change all '¶' to '<img class="link-img" alt="link-svg" src={svg_paths.link_svg_path}/>' into html_file
echo -e "\tCHANGE ALL '¶' TO '<img class="link-img" alt="link-svg" src={svg_paths.link_svg_path}/>' INTO $html_file"
sed -i 's/¶/<img class="link-img" alt="link-svg" src=\{svg_paths.link_svg_path\}\/>/g' $html_file

# Create page
echo -e "\tCREATING PAGE: $end_url.astro"
if [[ $languaje == "EN" ]]; then
    touch ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    touch ../portfolio/src/pages/pt-br/$end_url.astro
else
    touch ../portfolio/src/pages/$end_url.astro
fi

# Add header
echo -e "\tADDING HEADER TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$header_file" > ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$header_file" > ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$header_file" > ../portfolio/src/pages/$end_url.astro
fi

# Add html index
echo -e "\tADDING HTML INDEX TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$post_index" >> ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$post_index" >> ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$post_index" >> ../portfolio/src/pages/$end_url.astro
fi

# Add html content
echo -e "\tADDING HTML CONTENT TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    cat $html_file >> ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    cat $html_file >> ../portfolio/src/pages/pt-br/$end_url.astro
else
    cat $html_file >> ../portfolio/src/pages/$end_url.astro
fi

# Add botom
echo -e "\tADDING BOTOM TO $end_url.astro"
if [[ $languaje == "EN" ]]; then
    echo "$botom_file" >> ../portfolio/src/pages/en/$end_url.astro
elif [[ $languaje == "PT" ]]; then
    echo "$botom_file" >> ../portfolio/src/pages/pt-br/$end_url.astro
else
    echo "$botom_file" >> ../portfolio/src/pages/$end_url.astro
fi