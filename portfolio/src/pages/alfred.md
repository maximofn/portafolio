---
layout: '../layouts/MarkdownLayout.astro'

huggingface_svg_path: 'icons/hf-logo-pirate.svg'
github_svg_path: 'icons/github-brands-solid.svg'
linkedin_svg_path: 'icons/linkedin-brands-solid.svg'
x_svg_path: 'icons/square-x-twitter-brands-solid.svg'
kaggle_svg_path: 'icons/kaggle-brands-solid.svg'
facebook_svg_path: 'icons/facebook-brands-solid.svg'
instagram_svg_path: 'icons/instagram-brands-solid.svg'
tiktok_svg_path: 'icons/tiktok-brands-solid.svg'
twitch_svg_path: 'icons/twitch-brands-solid.svg'
youtube_svg_path: 'icons/youtube-brands-solid.svg'
curriculum_svg_path: 'icons/cv-solid.svg'
spain_flag_svg_path: 'icons/spain-flag.svg'
united_states_flag_svg_path: 'icons/united-states-flag.svg'
brazil_flag_svg_path: 'icons/brazil-flag-optimized.svg'

maximofn_photo_path: 'images/maximo-0014_resized_291x436.webp'
# maximofn_photo_path: = 'https://avatars.githubusercontent.com/u/53622795?v=4'

huggingface_link: 'https://huggingface.co/Maximofn'
github_link: 'http://github.com/maximofn'
linkedin_link: 'http://linkedin.com/in/MaximoFN/'
x_link: 'https://x.com/Maximo_fn'
kaggle_link: 'http://kaggle.com/maximofn'
facebook_link: 'https://www.facebook.com/profile.php?id=100085177670661'
instagram_link: 'https://www.instagram.com/maximo__fn/'
tiktok_link: 'https://www.tiktok.com/@maximo__fn'
twitch_link: 'https://www.twitch.tv/maximofn/'
youtube_link: 'https://www.youtube.com/channel/UCdQwg2JU_fWRsHn3yIlf3tw'
curriculum_link: 'https://github.com/maximofn/maximofn/raw/main/Curriculum%20Vitae.pdf'
portfolio_link: 'https://www.twitch.tv/maximofn/portafolio'

color_50: ='#f2f7fb'
color_100: '#e7f0f8'
color_200: '#d3e2f2'
color_300: '#b9cfe8'
color_400: '#9cb6dd'
color_500: '#839dd1'
color_600: '#6a7fc1'
color_700: '#6374ae'
color_800: '#4a5989'
color_900: '#414e6e'
color_950: '#262c40'

background_color: '#131720'
color_white: '#fafafa'
color_grid_dark: 'rgba(79, 79, 79, 0.2)'
color_grid_light: '#4f4f4f2e'

title: "MaximoFN"
languaje: 'es'
description: 'Página de MaximoFN. Página para aprender sobre IA en español'
keywords: 'IA, Inteligencia Artificial, Python, Español'
author: 'MaximoFN'
theme_color: '#131720'
url: 'https://maximofn.com'
icon: "/icons/MFN-512x512.webp"
---

# Alfred

Personal terminal assistant for all operating systems and languages

![usage](https://raw.githubusercontent.com/maximofn/alfred/main/gifs/alfredx4.gif)

## Install

Install system requeriments

``` bash
sudo apt update
sudo apt install -y python3 python3-pip git
```

### Install by installer

From here, if you have a debian based system you can use the [alfred.deb](https://github.com/maximofn/alfred/blob/v1.3/alfredv1_3.deb) installer.

### Install from source

Install python requeriments

``` bash
pip install halo
pip install --upgrade openai
```

Create source folder

``` bash
sudo rm -r /usr/src/alfred
cd /usr/src
git clone -b branch_v1.3 https://github.com/maximofn/alfred.git
cd /usr/src/alfred
sudo find . -depth -not -name '*.py' -delete
```

Create symbolic link to /usr/bin/alfred

``` bash
echo 'alias alfred="/usr/src/alfred/alfred.py"' >> ~/.bashrc
```

Restart bash

``` bash
source ~/.bashrc
```

## Openai API KEY

Loggin to <a href="https://platform.openai.com/overview" target="_blank">open ai</a> and get your open ai api key

![open ai api key](https://raw.githubusercontent.com/maximofn/alfred/main/gifs/openaix2.gif)

## Usage

You can ask to alfred specific questions by typing `alfred` followed by your question

![usage](https://raw.githubusercontent.com/maximofn/alfred/main/gifs/alfredx4.gif)

Or write `alfred` and keep asking him questions. To finish type `exit`

![usage](https://raw.githubusercontent.com/maximofn/alfred/main/gifs/alfredBuclex4.gif)

## Support

If you like it consider giving the repository a star ⭐, but if you really like it consider buying me a coffee ☕.

[![BuyMeACoffee](https://img.shields.io/badge/Buy_Me_A_Coffee-Support_my_work-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white&labelColor=101010)](https://www.buymeacoffee.com/maximofn)