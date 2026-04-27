from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.event import EventDispatcher
from model.image_model import ImageModel
from model.image_organizer import ImageOrganizer
import os
import json
from nltk.corpus import wordnet as wn
import torch
import numpy as np
import re
from datetime import datetime

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
    
    def update_image_data(self, image_path, filename, date, tags):

        # --- VALIDÁLÁS ---
        if not filename:
            raise ValueError("Fájlnév nem lehet üres")

        if re.search(r'[<>:"/\\|?*]', filename):
            raise ValueError("Érvénytelen karakter a fájlnévben")

        # dátum
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except:
                raise ValueError("Dátum formátum: YYYY-MM-DD")

        # tagek tisztítása
        clean_tags = list(set(tag.strip().lower() for tag in tags if tag.strip()))

        # --- FÁJL ÁTNEVEZÉS ---
        dir_path = os.path.dirname(image_path)
        ext = os.path.splitext(image_path)[1]
        new_path = os.path.join(dir_path, filename + ext)

        if new_path != image_path:
            os.rename(image_path, new_path)

            # embedding fájl átnevezése is!
            old_emb = image_path + ".npy"
            new_emb = new_path + ".npy"

            if os.path.exists(old_emb):
                os.rename(old_emb, new_emb)


        # --- MODEL UPDATE ---
        self.organizer.update_image(
            image_path,
            {
                "filename": new_path,
                "tags": clean_tags,
                "created_at": date
            }
        )

        return image_path
    
    # ---------------- PATH ----------------

    def get_assets_path(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base_dir, "assets")

    # ---------------- FOLDERS ----------------

    def load_folders(self, path):
        self.current_path = path
        self.folders = self.model.get_subfolders(path)

    def select_folder(self, folder_name):
        new_path = os.path.join(self.current_path, folder_name)
        self.current_path = new_path

        subfolders = self.model.get_subfolders(new_path)
        images = self.model.load_images(new_path)

        self.folders = subfolders
        self.images = images

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
    
    def search_images(self, prompt: str, threshold: float = 0.20):

        json_path = os.path.join(self.get_assets_path(), "images.json")

        if not os.path.exists(json_path):
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        text_vec = self.model.get_text_embedding(prompt) 

        results = []

        for entry in data:
            emb_path = entry.get("embedding_file")

            if not emb_path or not os.path.exists(emb_path):
                continue

            image_vec = torch.from_numpy(np.load(emb_path)).float().to(self.model.device)

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
    
    def get_metadata(self, path):
        for item in self.organizer.data:
            if item["filename"] == path:
                return item
        return None
    
    def get_caption(self, path):
        data = self.get_metadata(path)
        return data["caption"] if data else ""

    def get_tags(self, path):
        data = self.get_metadata(path)
        return data["tags"] if data else []

    def get_upload_date(self, path):
        data = self.get_metadata(path)
        return data["created_at"] if data else []
    
    def get_main_category(self, path):
        data = self.get_metadata(path)
        return data["main_category"] if data else []
    
    def get_subcategory(self, path):
        data = self.get_metadata(path)
        return data["subcategory"] if data else []

