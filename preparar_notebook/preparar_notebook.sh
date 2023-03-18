#!/bin/bash

notebook=$1
posts_dir="/home/wallabot/Documentos/web/portafolio/posts/"

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
                if [[ $actual_dir/$dir == $posts_dir ]]; then
                    cd $posts_dir
                    read -p "Quieres traducirlo? (si/no): " traducir
                    while [[ $traducir != "si" && $traducir != "no" && $traducir != "SI" && $traducir != "NO" && $traducir != "Si" && $traducir != "No" && $traducir != "sI" && $traducir != "nO" ]]; do
                        read -p "Quieres traducirlo? (si/no): " traducir
                    done
                    if [[ $traducir == "si" ]]; then
                        echo "TRANSLATING $name.$ext"
                        source ~/miniconda3/bin/activate translator
                        python ../../jupyter-translator/jupyter_translator.py -f $name.$ext -t EN PT
                        source ~/miniconda3/bin/deactivate
                        echo "TRANSLATION DONE"
                    fi
                    echo -e "\nGENERATING HTMLs"
                    python ../../jupyter-to-html/jupyter_to_html.py -f $name.$ext
                    python ../../jupyter-to-html/jupyter_to_html.py -f notebooks_translated/$name"_EN".$ext
                    python ../../jupyter-to-html/jupyter_to_html.py -f notebooks_translated/$name"_PT".$ext
                    echo "HTMLs GENERATED"
                else
                    echo "The file is not in the posts directory"
                    echo "Actual directory: $actual_dir/$dir"
                    echo "Posts directory: $posts_dir"
                fi
            else
                echo "The file is not readable"
            fi
        else
            echo "The file is not a regular file"
        fi
    else
        echo "The file does not exist"
    fi
else
    echo "The file is not a notebook"
fi