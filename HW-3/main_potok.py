import argparse
from pathlib import Path
from shutil import copyfile
from threading import Thread
import logging

"""
--source [-s]
--output [-o] default folder = sort
"""


parser = argparse.ArgumentParser(description="Sorting files in a directory")
parser.add_argument("--source", "-s", help="Source directory", required=True)
parser.add_argument("--output", "-o", help="Output directory", default="files_by_type")

print(parser.parse_args())
args = vars(parser.parse_args())
print(args)

source = Path(args.get("source"))
output = Path(args.get("output"))

directories = []


def process_folder(path: Path) -> None:
    for el in path.iterdir():
        if el.is_dir():
            directories.append(el)  # додаємо до списку шлях до вкладеної директороії
            process_folder(el)      # перевіряємо даний елемент на наявність вкладених директорій


def copy_file(path: Path) -> None:
    for el in path.iterdir():
        if el.is_file():
            ext = el.suffix[1:]     # отримуємо розширення файлу
            ext_dir = output / ext  # зберігаємо шлях до директорії з розширенням конкретного файлу

            try:
                ext_dir.mkdir(exist_ok=True, parents=True)   # створюємо директорію, якщо вона не існує
                copyfile(el, ext_dir / el.name)     # копіюємо файл
            except OSError as e:
                logging.error(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

    directories.append(source)
    process_folder(source)
    logging.info(f"{directories}")

    threads = []
    for directory in directories:
        th = Thread(target=copy_file, args=(directory,))
        th.start()
        threads.append(th)

    [th.join() for th in threads]
    logging.info(f"Done! Can be delete the \"{source}\"")
