import os
import pytest
import numpy as np
from model.image_organizer import ImageOrganizer

class DummyModel:
    def analyze_image(self, path):
        return {
            "main_category": "animal",
            "subcategory": "dog",
            "tags": ["dog"],
            "caption": "a dog",
            "embedding": np.array([1, 2, 3]),
            "created_at": "2024-01-01"
        }

    def get_image_embedding(self, path):
        return np.array([1, 2, 3])


@pytest.fixture
def organizer(tmp_path):
    org = ImageOrganizer(
        assets_dir=tmp_path,
        json_path=tmp_path / "images.json"
    )
    org.model = DummyModel()
    return org

def test_add_image(organizer, tmp_path):
    test_img = tmp_path / "test.jpg"
    test_img.write_text("fake")

    target_path, result = organizer.add_image(str(test_img))

    assert os.path.exists(target_path)
    assert len(organizer.data) == 1

def test_delete_image(organizer, tmp_path):
    test_img = tmp_path / "test.jpg"
    test_img.write_text("fake")

    path, _ = organizer.add_image(str(test_img))

    organizer.delete_image(path)

    assert not os.path.exists(path)
    assert len(organizer.data) == 0

def test_move_image(organizer, tmp_path):
    test_img = tmp_path / "test.jpg"
    test_img.write_text("fake")

    path, _ = organizer.add_image(str(test_img))

    organizer.move_image(path, "new_cat", "new_sub")

    assert organizer.data[0]["main_category"] == "new_cat"