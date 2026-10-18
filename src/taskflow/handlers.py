from taskflow.tasks import task


@task("example")
def example_handler():
    return "success"
