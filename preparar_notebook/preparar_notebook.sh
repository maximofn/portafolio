#!/bin/bash

notebook=$1
user=$(whoami)
documents="Documentos"
if [[ $user == *"@AEROESPACIAL.SENER"* ]]; then
    user=${user//@AEROESPACIAL.SENER/}
    documents="Documents"
    echo $user
fi
posts_dir="/home/$user/Documents/web/portafolio/posts/"
pages_dir="/home/$user/Documents/web/portafolio/paginas"

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
                    echo -e "\nGENERATING HTMLs"
                    python ../../jupyter-to-html/jupyter_to_html.py -f $name.$ext
                    python ../../jupyter-to-html/jupyter_to_html.py -f notebooks_translated/$name"_EN".$ext
                    python ../../jupyter-to-html/jupyter_to_html.py -f notebooks_translated/$name"_PT".$ext
                    echo "HTMLs GENERATED"
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