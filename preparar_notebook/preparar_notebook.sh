#!/bin/bash

notebook=$1

echo "GETING METADATA OF $notebook"
IFS=$'$' read -r title end_url description_es description_en description_pt keywords_es keywords_en keywords_pt image image_width image_height image_extension date < <(python ../preparar_notebook/get_notebook_metadata.py $notebook)

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
echo -e "\tImage width: $image_width"
echo -e "\tImage height: $image_height"
echo -e "\tImage extension: $image_extension"
echo -e "\tDate: $date"
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
                    ../preparar_notebook/add_htmls_to_astro.sh html_files/$name.html "$title" "$end_url" "$description_es" "$keywords_es" "ES" "$image" "$image_width" "$image_height" "$image_extension" "$date"
                    echo -e "\nADDING EN HTML TO ASTRO"
                    ../preparar_notebook/add_htmls_to_astro.sh html_files/$name"_EN".html "$title" "$end_url" "$description_en" "$keywords_en" "EN" "$image" "$image_width" "$image_height" "$image_extension" "$date"
                    echo -e "\nADDING PT HTML TO ASTRO"
                    ../preparar_notebook/add_htmls_to_astro.sh html_files/$name"_PT".html "$title" "$end_url" "$description_pt" "$keywords_pt" "PT" "$image" "$image_width" "$image_height" "$image_extension" "$date"
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