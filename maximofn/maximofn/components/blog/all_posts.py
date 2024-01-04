import reflex as rx
import maximofn.components.blog.posts as posts

def all_posts() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Posts",
        ),
        posts.post_test1(),
    )