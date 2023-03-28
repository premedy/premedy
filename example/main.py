from premedy.premedy import Premedy
from goblet import Goblet, goblet_entrypoint

app = Goblet(function_name="premedy", backend="cloudrun")
Premedy(
    app,
    topic="<topic>",
    project="<project>",
    path="./remediations",
)
goblet_entrypoint(app)
