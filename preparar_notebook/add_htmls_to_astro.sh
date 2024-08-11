#!/bin/bash

html_file=$1
title=$2
end_url=$3
description=$4
keywords=$5
languaje=$6
image=$7
echo "Notebook: $notebook"
echo "Title: $title"
echo "End URL: $end_url"
echo "Description: $description"
echo "Keywords: $keywords"
dir=$(dirname "$html_file")
ext=${html_file##*.} # "txt"
name=$(basename "$html_file" .$ext)

header_file="---
import PostLayout from '../layouts/PostLayout.astro';

const { metadata_page } = await import('../../consts.json');
const { colors } = await import('../../consts.json');

const page_title = '$title';
const end_url = '$end_url';
const description = '$description';
const keywords = '$keywords';
const languaje = '$languaje';
const image_path = '$image';
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
>"

botom_file="</PostLayout>"

# Create page
touch ../portfolio/src/pages/$name.astro

# Add header
echo "$header_file" > ../portfolio/src/pages/$name.astro

# Add html
cat $html_file >> ../portfolio/src/pages/$name.astro

# Add botom
echo "$botom_file" >> ../portfolio/src/pages/$name.astro