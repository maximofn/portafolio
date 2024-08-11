#!/bin/bash

# Enter post title: Python
# Enter post end url: python
# Enter post spanish description: Introducción a Python
# Enter post english description: Python introduction
# Enter post portugesse description: Uma introducion a Python
# Enter post spanish keywords: python, introducción
# Enter post english keywords: python, introduction
# Enter post portugesse keywords: python, introducion
# Enter post image path: images/alfred.webp

notebook=$1

# read -p "Enter post title: " title
# read -p "Enter post end url: " end_url
# read -p "Enter post spanish description: " description_es
# read -p "Enter post english description: " description_en
# read -p "Enter post portugesse description: " description_pt
# read -p "Enter post spanish keywords: " keywords_es
# read -p "Enter post english keywords: " keywords_en
# read -p "Enter post portugesse keywords: " keywords_pt
# read -p "Enter post image path: " image
title="Python"
end_url="python"
description_es="Introducción a Python"
description_en="Python introduction"
description_pt="Uma introducion a Python"
keywords_es="python, introducción"
keywords_en="python, introduction"
keywords_pt="python, introducion"
image="images/alfred.webp"

echo -e "\nConfiguration of the post:"
echo -e "\tTitle: $title"
echo -e "\tEnd URL: $end_url"
echo -e "\tSpanish Description: $description_es"
echo -e "\tEnglish Description: $description_en"
echo -e "\tPortugesse Description: $description_pt"
echo -e "\tSpanish Keywords: $keywords_es"
echo -e "\tEnglish Keywords: $keywords_en"
echo -e "\tPortugesse Keywords: $keywords_pt"
echo -e "\tImage Path: $image"
read -p "Is it correct? (yes/no)" correct
correct=$(echo $correct | tr '[:upper:]' '[:lower:]') # Change the answer to lowercase
while [[ $correct != "yes" && $correct != "no" ]]; do
    read -p "Is it correct? (yes/no): " correct
    correct=$(echo $correct | tr '[:upper:]' '[:lower:]') # Change the answer to lowercase
done
if [[ $correct == "no" ]]; then
    exit 1
fi

user=$(whoami)
documents="Documentos"
if [[ $user == *"@AEROESPACIAL.SENER"* ]]; then
    user=${user//@AEROESPACIAL.SENER/}
    documents="Documents"
    echo $user
fi
posts_dir="/home/$user/$documents/web/portafolio/posts/"
pages_dir="/home/$user/$documents/web/portafolio/paginas"

# If the notebook is not specified explain how to use the script and exit
if [[ $notebook == "" ]]; then
    echo "Usage: preparar_notebook.sh <notebook>"
    exit 1
fi

# Get directory name and extension of the notebook
dir=$(dirname "$notebook")
ext=${notebook##*.} # "txt"
name=$(basename "$notebook" .$ext)
actual_dir=$(pwd)

# Change path '.' to ''
if [[ $dir == "." ]]; then
    dir=""
fi

if [[ $ext == "ipynb" ]]; then
    if [[ -e $notebook ]]; then
        if [[ -f $notebook ]]; then
            if [[ -r $notebook ]]; then
                if [[ $actual_dir/$dir == $posts_dir || $actual_dir/$dir == $pages_dir ]]; then
                    if [[ $actual_dir/$dir == $posts_dir ]]; then
                        cd $posts_dir
                    fi
                    if [[ $actual_dir/$dir == $pages_dir ]]; then
                        cd $pages_dir
                    fi
                    read -p "Do you whant to translate it? (yes/no): " traducir
                    traducir=$(echo $traducir | tr '[:upper:]' '[:lower:]') # Change the answer to lowercase
                    while [[ $traducir != "yes" && $traducir != "no" ]]; do
                        read -p "Do you whant to translate it? (yes/no): " traducir
                        traducir=$(echo $traducir | tr '[:upper:]' '[:lower:]') # Change the answer to lowercase
                    done
                    if [[ $traducir == "yes" ]]; then
                        echo "TRANSLATING $name.$ext"
                        source ~/miniconda3/bin/activate translator
                        python ../../jupyter-translator/jupyter_translator.py -f $name.$ext -t EN PT
                        conda deactivate
                        echo "TRANSLATION DONE"
                    fi

                    # replace "execution_count": "None", by "execution_count": 99, in notebooks translated
                    echo -e "\nREPLACING execution_count None BY 99"
                    sed -i 's/"execution_count": "None"/"execution_count": 99/g' notebooks_translated/$name"_EN".$ext
                    sed -i 's/"execution_count": "None"/"execution_count": 99/g' notebooks_translated/$name"_PT".$ext

                    echo -e "\nGENERATING HTMLs"
                    echo -e "\n\tGENERATING SPANISH HTML"
                    jupyter nbconvert --to html --template posts_template $name.$ext
                    echo -e "\n\tGENERATING ENGLISH HTML"
                    jupyter nbconvert --to html --template posts_template notebooks_translated/$name"_EN".$ext
                    echo -e "\n\tGENERATING PORTUGUESSE HTML"
                    jupyter nbconvert --to html --template posts_template notebooks_translated/$name"_PT".$ext
                    echo "HTMLs GENERATED"

                    echo -e "\nMOVING HTMLs TO THE RIGHT DIRECTORY"
                    mv $name.html html_files/
                    mv notebooks_translated/$name"_EN".html html_files/
                    mv notebooks_translated/$name"_PT".html html_files/

                    echo -e "\nADDING ES HTML TO ASTRO"
                    ../preparar_notebook/add_htmls_to_astro.sh html_files/$name.html "$title" "$end_url" "$description_es" "$keywords_es" "ES" "$image"
                    echo -e "\nADDING EN HTML TO ASTRO"
                    ../preparar_notebook/add_htmls_to_astro.sh html_files/$name"_EN".html "$title" "$end_url" "$description_en" "$keywords_en" "EN" "$image"
                    echo -e "\nADDING PT HTML TO ASTRO"
                    ../preparar_notebook/add_htmls_to_astro.sh html_files/$name"_PT".html "$title" "$end_url" "$description_pt" "$keywords_pt" "PT" "$image"
                else
                    echo "You aren't into the posts directory"
                    echo "Actual directory: $actual_dir/$dir"
                    echo "Posts directory:  $posts_dir"
                    echo "Pages directory:  $pages_dir"
                    exit 1
                fi
            else
                echo "The file is not readable"
                exit 1
            fi
        else
            echo "The file is not a regular file"
            exit 1
        fi
    else
        echo "The file does not exist"
        exit 1
    fi
else
    echo "The file is not a notebook"
    exit 1
fi