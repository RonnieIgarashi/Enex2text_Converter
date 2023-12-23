import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET

OUTDIR = "output_files"
AFTERDIR = "extracted_files"
BEFOREDIR = "input_files"

class Note:
    def __init__(self):
        self.title = ""
        self.contents = ""
        self.updated = None

def sanitize_filename(title):
    # alter unavailable chars to '-'
    invalid_chars = re.compile(r'[\\/:\*\?"<>\|]')

    return re.sub(invalid_chars, '-', title)

def process_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for note_element in root.iter('note'):
        note = Note()

        for child in note_element:
            if child.tag == 'title':
                note.title = sanitize_filename(child.text) + ".txt"
            elif child.tag == 'content':
                note.contents = child.text.strip()
                note.contents = note.contents.replace("<br/>", "\n")
                # remove unnecessary XML tags of head and tail
                note.contents = re.sub(r"<\?xml(.+?)<en-note>", "", note.contents, flags=re.DOTALL)
                note.contents = re.sub(r"</en-note>", "", note.contents, flags=re.DOTALL)
            elif child.tag == 'updated':
                time_string = re.search(r"\d{8}T\d{6}Z", child.text)
                note.updated = time.strptime(time_string.group(), "%Y%m%dT%H%M%SZ")

        note.contents = re.sub(r"</?[a-zA-Z]+/?>", "", note.contents)
        note.title = note.title.replace("/", "-")
        path = os.path.join(OUTDIR, note.title)

        with open(path, "w", encoding='UTF-8') as output_file:
            output_file.write(note.contents + "\n")

        os.utime(path, (time.mktime(note.updated), time.mktime(note.updated)))

def process_directory(dir_path):
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        
        if os.path.isfile(file_path) and file_name.endswith(".enex"):
            process_file(file_path)
            shutil.move(file_path, os.path.join(AFTERDIR, file_name))
        elif os.path.isdir(file_path):
            # Don't execute when target is directory.(not recursive)
            pass
        else:
            print(f"Error: File '{file_path}' not found.")


def main():
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
    
    if not os.path.exists(AFTERDIR):
        os.makedirs(AFTERDIR)
    
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        if not os.path.isfile(input_file):
            print(f"Error: File '{input_file}' not found.")
            sys.exit(1)
        else:
            process_file(input_file)
            print("Finish!")
    elif len(sys.argv) > 2:
        print("can't execute over 2 in a single mode. when you wan't to convert multiple files, put target files in input directory and don't put any arguments.")
        sys.exit(1)
    else:
        process_directory(BEFOREDIR)
        print("Finish!")


if __name__ == "__main__":
    main()
