import pytest
import torch
from model.image_model import ImageModel

@pytest.fixture
def model():
    m = ImageModel()
    return m

def test_similarity(model):
    img = torch.tensor([1.0, 0.0])
    txt = torch.tensor([[1.0, 0.0]])

    score = model.similarity(img, txt)

    assert isinstance(score, float)
    assert score == pytest.approx(1.0)

def test_search_clip_sorting(model):
    image_embeddings = {
        "a.jpg": torch.tensor([1.0, 0.0]),
        "b.jpg": torch.tensor([0.0, 1.0])
    }

    def fake_text_embedding(prompt):
        return torch.tensor([[1.0, 0.0]])

    model.get_text_embedding = fake_text_embedding

    results = model.search_clip("test", image_embeddings)

    assert results[0][0] == "a.jpg"
    assert results[0][1] >= results[1][1]

def test_extract_nouns(model):
    caption = "A dog and a car in the city"
    nouns = model.extract_nouns(caption)

    assert "dog" in nouns
    assert "car" in nouns

def test_determine_category_from_tags(model):
    tags = ["dog", "tree"]

    cat, sub = model.determine_category_from_tags(tags)

    assert cat in model.MAIN_CATEGORIES or cat == "other"
    assert isinstance(sub, str)