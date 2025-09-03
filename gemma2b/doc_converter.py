# This script converts all old .doc files in a specified folder to .docx format using the Windows COM interface for Microsoft Word.
import os
import re
from glob import glob
import win32com.client as win32
from win32com.client import constants

def convert_doc_to_docx(folder_path, dest_folder):
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = False

    doc_files = glob(os.path.join(folder_path, "*.doc"))
    print("docs loaded:", len(doc_files))
    for doc_path in doc_files:
        try:
            doc = word.Documents.Open(doc_path)
            doc.Activate()

            base_name = os.path.basename(doc_path)
            # Create new filename
            new_filename = re.sub(r'\.doc$', '.docx', base_name, flags=re.IGNORECASE)
            new_path = os.path.join(dest_folder, new_filename)
            # Save as DOCX
            doc.SaveAs(new_path, FileFormat=constants.wdFormatXMLDocument)
            doc.Close(False)
            print(f"✅ Converted: {os.path.basename(doc_path)} → {os.path.basename(new_path)}")

        except Exception as e:
            print(f"❌ Failed to convert {doc_path}: {e}")

    word.Quit()

convert_doc_to_docx("c:/personal/_gemma/customdocs/raw/dogs_breeds_doc/",
                    "c:/personal/_gemma/customdocs/raw/dogs_breeds_docx/")