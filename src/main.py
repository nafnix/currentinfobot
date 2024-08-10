from src.core.app import App
from src.handlers import handlers


app = App()

app.include_handlers(handlers)

app.run()
