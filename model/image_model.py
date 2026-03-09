import os
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import spacy
import torch
import nltk
from nltk.corpus import wordnet as wn


class ImageModel:
    MAIN_CATEGORIES = {
        "animal",
        "vehicle",
        "person",
        "plant",
        "food",
        "building",
        "furniture"
    }
    
    def __init__(self):
        self.processor = BlipProcessor.from_pretrained(
            "models/blip",
            local_files_only=True
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            "models/blip",
            local_files_only=True
        )
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        self.nlp = spacy.load("en_core_web_sm")

     # ---------------- CAPTION + TAG ----------------

    def generate_caption(self, image_path):
        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        output = self.model.generate(**inputs)

        caption = self.processor.decode(
            output[0],
            skip_special_tokens=True
        )

        return caption

    def extract_nouns(self, caption):
        doc = self.nlp(caption)
        return [
            token.lemma_.lower()
            for token in doc
            if token.pos_ in ("NOUN", "PROPN")
        ]

    # ---------------- WORDNET CATEGORY ----------------

    def categorize_tag(self, tag):
        tag = tag.lower()
        
        synsets = wn.synsets(tag, pos=wn.NOUN)

        if not synsets:
            return "other"

        for synset in synsets:
            queue = [synset]
            visited = set()
            while queue:
                s = queue.pop(0)
                if s in visited:
                    continue
                visited.add(s)
    
                name = s.name().split('.')[0].lower()
                if name in self.MAIN_CATEGORIES:
                    return name
    
                queue.extend(s.hypernyms())

        return "other"

    def determine_category_from_tags(self, tags):
        for tag in tags:
            main_cat = self.categorize_tag(tag)
            if main_cat != "other":
                return main_cat, tag

        return "other", "unknown"

    # ---------------- ANALYZE ----------------

    def analyze_image(self, image_path):
        caption = self.generate_caption(image_path)
        tags = self.extract_nouns(caption)

        main_category, subcategory = self.determine_category_from_tags(tags)

        return {
            "caption": caption,
            "tags": tags,
            "main_category": main_category,
            "subcategory": subcategory
        }

    # ---------------- IMAGE / FOLDER LOADING ----------------

    def get_folders_with_thumbnails(self, base_path):
        """
        Visszaadja az assets mappa almappáit
        mindegyikhez a thumbnail (első kép) útvonalát
        """
        result = []

        if not os.path.exists(base_path):
            return result

        folders = [
            f for f in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, f))
            and not f.startswith(".")
            and not f.endswith("checkpoints")
            and f != "__pycache__"
        ]

        for folder in folders:
            folder_path = os.path.join(base_path, folder)

            images = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]

            thumb_path = os.path.join(folder_path, images[0]) if images else ""

            result.append({
                "name": folder,
                "thumb": thumb_path
            })

        return result

    def get_subfolders(self, path):
        if not os.path.exists(path):
            return []
    
        return [
            {"name": f}
            for f in os.listdir(path)
            if os.path.isdir(os.path.join(path, f))
            and not f.startswith(".")
            and f != "__pycache__"
        ]

    def load_images(self, directory):
        if not os.path.exists(directory):
            return []

        return [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]

