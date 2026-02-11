import unittest
import os
import json
import tempfile
import shutil
import xml.etree.ElementTree as ET
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
parent_root = os.path.dirname(project_root)

sys.path.insert(0, project_root)
sys.path.insert(0, parent_root)

# Config xato bermasligi uchun
os.environ["ENV_FILE_PATH"] = os.path.join(project_root, ".env.borjomi")

# Import
try:
    from services.xml_transformer import XMLTransformer
except ImportError:
    from sales_integration.services.xml_transformer import XMLTransformer


class TestXMLTransformer(unittest.TestCase):

    def setUp(self):
        """Har bir testdan oldin vaqtinchalik papka va fayllar yaratamiz"""
        self.test_dir = tempfile.mkdtemp()

        # 1. Fake Mapping (JSON) yaratamiz
        self.mapping_path = os.path.join(self.test_dir, "mapping.json")
        self.mapping_data = {
            "101": "202",
            "555": "777"
        }
        with open(self.mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.mapping_data, f)

        # Classni shu fake mapping bilan ishga tushiramiz
        self.transformer = XMLTransformer(mapping_file=self.mapping_path)

    def tearDown(self):
        """Test tugagach, vaqtinchalik fayllarni o'chiramiz"""
        shutil.rmtree(self.test_dir)

    def test_load_mappings(self):
        """Mapping fayli to'g'ri yuklandimi?"""
        self.assertEqual(self.transformer.mappings["101"], "202")
        self.assertEqual(len(self.transformer.mappings), 2)
        print("✅ Mapping yuklash testi o'tdi.")

    def test_load_mapping_not_found(self):
        """Mapping fayli yo'q bo'lsa xato bermasligi kerak"""
        transformer = XMLTransformer(mapping_file="yoq_fayl.json")
        self.assertEqual(transformer.mappings, {})
        print("✅ Mapping yo'q bo'lsa (Empty) testi o'tdi.")

    def test_process_outlets_success(self):
        """XML dagi ID lar o'zgaradimi?"""

        # 1. Fake XML yaratamiz
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
        <Root>
            <Outlet AREA_ID="101" Name="Shop A" />
            <Outlet AREA_ID="999" Name="Shop B" />
            <Outlet AREA_ID="555" Name="Shop C" />
        </Root>"""

        xml_path = os.path.join(self.test_dir, "outlets.xml")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        # 2. Transformatsiya qilamiz
        result = self.transformer.process_outlets(xml_path)

        # 3. Tekshiramiz
        self.assertTrue(result)  # True qaytishi kerak (o'zgarish bo'ldi)

        # XML ni qayta o'qib, ichini tekshiramiz
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 101 -> 202 ga o'zgarishi kerak
        outlet_a = root.find(".//Outlet[@Name='Shop A']")
        self.assertEqual(outlet_a.get('AREA_ID'), "202")

        # 555 -> 777 ga o'zgarishi kerak
        outlet_c = root.find(".//Outlet[@Name='Shop C']")
        self.assertEqual(outlet_c.get('AREA_ID'), "777")

        # 999 o'zgarmasligi kerak (chunki mappingda yo'q)
        outlet_b = root.find(".//Outlet[@Name='Shop B']")
        self.assertEqual(outlet_b.get('AREA_ID'), "999")

        print("✅ XML Transformatsiya (Success) testi o'tdi.")

    def test_process_no_changes(self):
        """O'zgaradigan hech narsa bo'lmasa"""
        xml_content = '<Root><Outlet AREA_ID="888" /></Root>'
        xml_path = os.path.join(self.test_dir, "no_change.xml")
        with open(xml_path, 'w') as f:
            f.write(xml_content)

        result = self.transformer.process_outlets(xml_path)

        # False qaytishi kerak, chunki o'zgarish bo'lmadi
        self.assertFalse(result)
        print("✅ XML O'zgarishsiz (No changes) testi o'tdi.")

    def test_process_invalid_xml(self):
        """Buzilgan XML fayl kelsa"""
        xml_path = os.path.join(self.test_dir, "broken.xml")
        with open(xml_path, 'w') as f:
            f.write("<Root><Tag>Yopilmagan teg")  # Xato format

        result = self.transformer.process_outlets(xml_path)

        # Dastur qulamasligi kerak, shunchaki False qaytarishi kerak
        self.assertFalse(result)
        print("✅ Buzilgan XML (Invalid) testi o'tdi.")


if __name__ == '__main__':
    unittest.main()