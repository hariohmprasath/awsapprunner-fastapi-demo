import json
import os
import pytest
from reportlab.pdfgen import canvas
from fastapi.testclient import TestClient
from app import app, UploadFile
from typing import List

# Setup test client
client = TestClient(app)


@pytest.fixture
def server():
    with TestClient(app) as client:
        yield client


def test_upload_files(server):
    # Prepare a test file
    filename = "file1.pdf"
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "This is a sample PDF file.")
    c.save()

    test_files = [
        ("files", ("file1.pdf", open(filename, "rb"), "application/pdf")),
    ]

    # Send the request
    response = server.post("/upload", files=test_files)

    # Assert the response
    assert response.status_code == 200
    print(response)
    assert isinstance(json.loads(response.text), list)


    # Close the test files
    for _, (_, file, _) in test_files:
        file.close()
    
    # Remove the test file
    os.remove(filename)
