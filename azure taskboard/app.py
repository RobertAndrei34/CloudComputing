import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient

from models import db, Task

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

blob_service = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

queue_client = QueueClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name=os.getenv("QUEUE_NAME", "taskqueue")
)

CONTAINER_NAME = os.getenv("BLOB_CONTAINER", "attachments")


@app.before_request
def create_tables():
    db.create_all()


@app.route("/")
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("index.html", tasks=tasks)


@app.route("/tasks/create", methods=["POST"])
def create_task():
    title = request.form["title"]
    description = request.form.get("description")
    file = request.files.get("attachment")

    attachment_url = None

    if file and file.filename:
        container_client = blob_service.get_container_client(CONTAINER_NAME)

        try:
            container_client.create_container()
        except Exception:
            pass

        blob_name = f"{uuid.uuid4()}-{file.filename}"
        blob_client = container_client.get_blob_client(blob_name)

        blob_client.upload_blob(file, overwrite=True)
        attachment_url = blob_client.url

    task = Task(
        title=title,
        description=description,
        attachment_url=attachment_url
    )

    db.session.add(task)
    db.session.commit()

    queue_client.send_message(str(task.id))

    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>")
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("task.html", task=task)


if __name__ == "__main__":
    app.run(debug=True)