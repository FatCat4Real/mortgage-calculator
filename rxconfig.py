import reflex as rx

class Config(rx.Config):
    app_name = "mortgage_calculator"
    db_url = "sqlite:///reflex.db"
    env = rx.Env.DEV

config = Config()