import os
import json
import xml.etree.ElementTree as ET
from core.logger import logger
from core.config import settings


class XMLTransformer:
    """
    XML fayllarni biznes qoidalar asosida o'zgartiruvchi servis.
    Hozirda faqat AREA_ID larni almashtirish uchun moslashtirilgan.
    """

    def __init__(self, mapping_file: str = "data/area_mappings.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> dict:
        """JSON fayldan ID lar lug'atini yuklaydi."""
        if not os.path.exists(self.mapping_file):
            logger.warning(f"Mapping fayli topilmadi: {self.mapping_file}")
            return {}

        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Mapping yuklandi: {len(data)} ta qoida.")
                return data
        except Exception as e:
            logger.error(f"Mapping faylini o'qishda xato: {e}")
            return {}

    def process_outlets(self, file_path: str) -> bool:
        """
        Outlets.xml faylidagi AREA_ID larni almashtiradi.
        Matnni replace qilish o'rniga, XML daraxti (Tree) bilan ishlaydi (Xavfsiz usul).
        """
        if not self.mappings:
            return False

        try:
            logger.info(f"Outlets.xml tahlil qilinmoqda: {file_path}")

            # XML ni o'qish
            tree = ET.parse(file_path)
            root = tree.getroot()

            changes_count = 0

            # Har bir Outlet tegini qidiramiz (yoki kerakli tegni)
            # Agar XML strukturasi murakkab bo'lsa, './/Outlet' yoki shunga o'xshash yo'l kerak
            # Borjomi faylida aniq teg ko'rsatilmagan, umumiy replace qilingan.
            # Lekin Senior sifatida biz barcha elementlarning atributlarini tekshiramiz:

            for elem in root.iter():
                current_id = elem.get('AREA_ID')
                if current_id and current_id in self.mappings:
                    new_id = self.mappings[current_id]
                    elem.set('AREA_ID', new_id)
                    changes_count += 1

            if changes_count > 0:
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
                logger.info(f"✅ {changes_count} ta AREA_ID muvaffaqiyatli almashtirildi.")
                return True
            else:
                logger.info("ℹ️ O'zgartirish kerak bo'lgan AREA_ID lar topilmadi.")
                return False

        except ET.ParseError:
            logger.error("XML faylni o'qishda xatolik (buzilgan format).")
            return False
        except Exception as e:
            logger.error(f"XML transformatsiyasida xato: {e}")
            return False


# Singleton
xml_transformer = XMLTransformer()