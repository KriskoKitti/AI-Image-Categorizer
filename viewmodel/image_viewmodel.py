from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.event import EventDispatcher
from model.image_model import ImageModel
from model.image_organizer import ImageOrganizer
import os
import json
from nltk.corpus import wordnet as wn
import torch
import numpy as np


class ImageViewModel(EventDispatcher):

    folders = ListProperty([])
    images = ListProperty([])
    current_image = StringProperty("")
    index = NumericProperty(0)
    search_results = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = ImageModel()
        self.organizer = ImageOrganizer()
        self.base_path = self.get_assets_path()
        self.current_path = self.base_path
        self.load_folders(self.base_path)

    # ---------------- TAGS ----------------
    def process_image(self, image_path):
        return self.model.analyze_image(image_path)

    # ---------------- SAVE ----------------

    def save_image(self, image_path):
        return self.organizer.add_image(image_path)
    
    # ---------------- PATH ----------------

    def get_assets_path(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "assets")

    # ---------------- FOLDERS ----------------

    def load_folders(self, path):
        self.current_path = path
        self.folders = self.model.get_subfolders(path)

    def select_folder(self, folder_name):
        next_path = os.path.join(self.current_path, folder_name)
    
        subfolders = self.model.get_subfolders(next_path)
        images = self.model.load_images(next_path)
    
        if subfolders:
            self.load_folders(next_path)
    
        elif images:
            self.images = images
            self.index = 0
            self.current_image = images[0]
    
        else:
            self.folders = []

    def go_back_folder(self):
        if self.current_path != self.base_path:
            self.current_path = os.path.dirname(self.current_path)
            self.load_folders(self.current_path)

    # ---------------- IMAGES ----------------

    def load_directory(self, directory):
        self.images = self.model.load_images(directory)
        self.index = 0

        if self.images:
            self.current_image = self.images[0]
        else:
            self.current_image = ""

    def next_image(self):
        if self.index < len(self.images) - 1:
            self.index += 1
            self.current_image = self.images[self.index]

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.current_image = self.images[self.index]

    def extract_nouns(self, caption):
        doc = self.model.nlp(caption)
        return [
            token.lemma_.lower()
            for token in doc
            if token.pos_ in ("NOUN", "PROPN")
        ]
    
    # def search_images(self, prompt: str):

    #     json_path = os.path.join(self.get_assets_path(), "images.json")

    #     if not os.path.exists(json_path):
    #         return []

    #     with open(json_path, "r", encoding="utf-8") as f:
    #         data = json.load(f)

    #     # -------- PROMPT PROCESSING --------

    #     prompt_tags = self.extract_nouns(prompt)

    #     # lemma + synonym expansion
    #     expanded_tags = set(prompt_tags)

    #     for tag in prompt_tags:
    #         for syn in wn.synsets(tag, pos=wn.NOUN):
    #             for lemma in syn.lemmas():
    #                 expanded_tags.add(lemma.name().lower())

    #     # -------- IMAGE MATCHING --------

    #     scored_results = []

    #     for entry in data:
    #         image_tags = [t.lower() for t in entry.get("tags", [])]

    #         # intersection
    #         matches = expanded_tags.intersection(image_tags)

    #         if matches:
    #             score = len(matches) / len(image_tags)

    #             scored_results.append({
    #                 "filename": entry["filename"],
    #                 "score": score
    #             })

    #     # -------- SORT BY RELEVANCE --------

    #     scored_results.sort(key=lambda x: x["score"], reverse=True)

    #     results = [item["filename"] for item in scored_results]

    #     self.search_results = results
    #     return results
    
    def search_images(self, prompt: str, threshold: float = 0.2):

        json_path = os.path.join(self.get_assets_path(), "images.json")

        if not os.path.exists(json_path):
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # TEXT EMBEDDING
        text_vec = self.model.get_text_embedding(prompt)  # already normalized

        results = []

        for entry in data:
            emb_path = entry.get("embedding_file")

            if not emb_path or not os.path.exists(emb_path):
                continue

            # load numpy embedding
            image_vec = torch.from_numpy(np.load(emb_path)).float().to(self.model.device)

            # normalize (IMPORTANT even if you think it's normalized)
            image_vec = image_vec / image_vec.norm(dim=-1, keepdim=True)

            score = torch.matmul(text_vec, image_vec).item()

            if score >= threshold:
                results.append({
                    "filename": entry["filename"],
                    "score": score
                })

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        results = [r for r in results if r["score"] >= threshold]

        final = [r["filename"] for r in results]
        self.search_results = final

        return final

