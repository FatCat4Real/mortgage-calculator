import reflex as rx

class SimpleState(rx.State):
    count: int = 0

def index():
    return rx.vstack(
        rx.heading("Simple Test App", size="5"),
        rx.text(f"Count: {SimpleState.count}"),
        rx.button("Increment", on_click=SimpleState.set_count(SimpleState.count + 1)),
    )

app = rx.App()
app.add_page(index)