import os
import json
import shutil
from pathlib import Path
from model.image_model import ImageModel  
import numpy as np

class ImageOrganizer:
    def __init__(self, assets_dir=None, json_path=None):
        self.model = ImageModel()

        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.assets_dir = assets_dir or os.path.join(base_dir, "assets")
        self.json_path = json_path or os.path.join(self.assets_dir, "images.json")

        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def add_image(self, image_path):
        result = self.model.analyze_image(image_path)
        main_cat = result["main_category"]
        sub_cat = result["subcategory"]
        tags = result["tags"]
        caption = result["caption"]
        image_date = result["created_at"]

        target_dir = os.path.join(self.assets_dir, main_cat, sub_cat)
        os.makedirs(target_dir, exist_ok=True)

        filename = os.path.basename(image_path)
        target_path = os.path.join(target_dir, filename)

        counter = 1
        while os.path.exists(target_path):
            name, ext = os.path.splitext(filename)
            target_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
            counter += 1

        shutil.copy(image_path, target_path)

        embedding = self.model.get_image_embedding(target_path)

        embedding_path = os.path.join(self.assets_dir, "embeddings")
        os.makedirs(embedding_path, exist_ok=True)

        emb_file = os.path.join(embedding_path, os.path.basename(target_path) + ".npy")
        np.save(emb_file, embedding)


        self.data.append({
            "filename": target_path,
            "main_category": main_cat,
            "subcategory": sub_cat,
            "tags": tags,
            "caption": caption,
            "embedding_file": emb_file,
            "created_at": image_date
        })

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

        return target_path, result

    def update_image(self, image_path, new_data: dict):
        for item in self.data:
            if item["filename"] == image_path:
                item.update(new_data)

                # embedding path fix
                item["embedding_file"] = new_data["filename"] + ".npy"
                break

        self._save_json()

    def delete_image(self, image_path):
        self.data = [
            item for item in self.data
            if item["filename"] != image_path
        ]

        self._save_json()

    def move_image(self, image_path, new_main, new_sub):
        for item in self.data:
            if item["filename"] == image_path:

                filename = os.path.basename(image_path)

                new_dir = os.path.join(self.assets_dir, new_main, new_sub)
                os.makedirs(new_dir, exist_ok=True)

                new_path = os.path.join(new_dir, filename)

                shutil.move(image_path, new_path)

                # JSON update
                item["filename"] = new_path
                item["main_category"] = new_main
                item["subcategory"] = new_sub

                break

        self._save_json()

    def _save_json(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)