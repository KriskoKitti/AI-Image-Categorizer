import pytest
from viewmodel.image_viewmodel import ImageViewModel

class DummyOrganizer:
    def __init__(self):
        self.data = []

    def add_image(self, path):
        return path, {}

    def delete_image(self, path):
        pass

    def get_subfolders(self, path):
        return [{"name": "sub"}]

    def load_images(self, path):
        return ["img1.jpg", "img2.jpg"]

    def update_image(self, path, data):
        pass


@pytest.fixture
def vm(monkeypatch):
    vm = ImageViewModel()
    vm.organizer = DummyOrganizer()
    return vm

def test_update_image_invalid_name(vm):
    with pytest.raises(ValueError):
        vm.update_image_data("img.jpg", "", None, [])

def test_update_image_invalid_chars(vm):
    with pytest.raises(ValueError):
        vm.update_image_data("img.jpg", "bad/name", None, [])

def test_update_image_invalid_date(vm):
    with pytest.raises(ValueError):
        vm.update_image_data("img.jpg", "good", "2024-99-99", [])

def test_navigation(vm):
    vm.select_folder("sub")
    assert isinstance(vm.images, list)

def test_image_navigation(vm):
    vm.images = ["a.jpg", "b.jpg"]
    vm.current_image = "a.jpg"

    vm.next_image()
    assert vm.current_image == "b.jpg"

    vm.prev_image()
    assert vm.current_image == "a.jpg"