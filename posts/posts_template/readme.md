Copy this folder to `~/miniconda3/share/jupyter/nbconvert/templates/posts_template/`, then export to HTML using the following command:

```bash
jupyter nbconvert --to html --template posts_template <jupyter_notebook>
```