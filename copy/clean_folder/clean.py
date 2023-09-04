import re
import shutil
import sys
from pathlib import Path

def noti():
    global video, images, audio, documents, archives, others, folders, extensions, others_extensions, dict_exstentions
    video = list()
    images = list()
    audio = list()
    documents = list()
    archives = list()
    others = list()
    folders = list()
    extensions = set()
    others_extensions = set()

    #  Словник розширеннь
    dict_exstentions = {
        "video": ('.avi', '.mp4', '.mov', '.mkv'),
        "images": ('.jpeg', '.png', '.jpg', '.svg'),
        "documents": ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
        "audio": ('.mp3', '.ogg', '.wav', '.arm'),
        "archives": ('.zip', '.gz', '.tar'),
    }

def create_trans_dict():
    UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m",
                   "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

    global TRANS                                # створюємо словник  TRANS з маленькими та великими літерами
    TRANS = {}
    for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
        TRANS[ord(key)] = value
        TRANS[ord(key.upper())] = value.upper()


def dir_manager(folder, flag='del'):    # Створюємо або видаляємо технічні папки
    perech_dir = ('archives', 'video', 'audio', 'documents', 'images', 'others')
    if flag == 'create':
        for item in perech_dir:
            folder_create = folder / item
            folder_create.mkdir(exist_ok=True)
    else:
        for item in perech_dir:
            folder_create = folder / item
            if not any(folder_create.iterdir()):
                folder_create.rmdir()


def normalize(name):
    """ транслітерує з кирилиці на англійський алфавіт, неліквід транслітерує на "_"
        розширення не змінюється
        Повертає им'я папки чи файла   """
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"

def rename_file(file, target_folder):
    target_folder.mkdir(exist_ok=True)
    file.replace(target_folder/normalize(file.name))
    print(f' {file}  перенесено {target_folder} ')

def repack_archive(archive):
    """" Розпаковка архіва у папку з іменем архіва."""
     # archive  - путь і ім'я файлу з розширенням

    archive_name = archive.name         # чисте ім'я файлу з розширенням

                                      # чисте ім'я файлу без розширення
    new_name_dir = normalize(archive_name.replace(".zip", '').replace('.gz','').replace('.tar',''))

    archive_folder = Arg_folder / "archives" / new_name_dir
#    print(f'1 archive: {archive}  Путь розпаковки: {archive_folder} ')

    archive_folder.mkdir(exist_ok=True)
    try:
        shutil.unpack_archive(str(archive.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    archive.unlink()
    print(f' archive: {archive}  Розпаковано: {archive_folder}  видалено')

def run_file(file):
    for type_file, ext_file in dict_exstentions.items():
        if type_file == "video" and file.suffix in ext_file:       #   video
            extensions.add(file.suffix)
            video.append(file)
            rename_file(file, Arg_folder / "video")
            return

        if type_file == "images" and file.suffix in ext_file:  # якщо images
            extensions.add(file.suffix)
            images.append(file)
            rename_file(file, Arg_folder / "images" )
            return

        if type_file == "documents" and file.suffix in ext_file:  # якщо documents
            extensions.add(file.suffix)
            documents.append(file)
            rename_file(file, Arg_folder / "documents")
            return

        if type_file == "audio" and file.suffix in ext_file:  # якщо audio
            extensions.add(file.suffix)
            audio.append(file)
            rename_file(file, Arg_folder / "audio" )
            return

        if type_file == "archives" and file.suffix in ext_file:    #  archives
            extensions.add(file.suffix)
            archives.append(file)
            repack_archive(file)
            return

    others_extensions.add(file.suffix)          # невідомий файл
    others.append(file)
    rename_file(file, Arg_folder / "others")


def run_dir(item):
    if item == Arg_folder / item.name:
        if item.name in ('archives', 'video', 'audio', 'documents', 'images', 'others'):
            return
        else:
            if not any(item.iterdir()):  # Видаляємо директорію, якщо  порожня
                item.rmdir()
                return

            folders.append(item)
            scan(item)                          # Сканує внутрішню папку item

    else:
        if not any(item.iterdir()):  # Видаляємо директорію, якщо  порожня
            item.rmdir()
            print(f' пуста папка : {item}  {item.name} видалено ')
            return

        folders.append(item)
        scan(item)                      # Сканує внутрішню папку item


def scan(root_folder):
    """" Сканує папку     """
    for item in root_folder.iterdir():
        if item.is_file():
            run_file(item)

        if item.is_dir():
            run_dir(item)


def main():
    noti()                  # створюємо списки
    path = sys.argv[1]
    print(f"Start in {path}")

    create_trans_dict()  # створюємо перекладач

    path = path.strip('/').split('/')[-1]  # Шлях  /user/Desktop/Мотлох  перетворюємо на Мотлох
    global Arg_folder
    Arg_folder = Path(path)
    arg = Arg_folder
    dir_manager(arg, 'create')  # Створюємо технічні папки

    for i in range(20):  # повтотрюємо для видалення пустих вкладених папок
        scan(arg)

    dir_manager(arg)        # видаляємо пусті технічні папки

    print(f"video файли: {video}\n")
    print(f"images файли: {images}\n")
    print(f"audio файли: {audio}\n")
    print(f"documents файли: {documents}\n")
    print(f"archives файли: {archives}\n")
    print(f"others файли: {others}\n")

    print(f"extensions: {extensions}\n")
    print(f"others_extensions: {others_extensions}\n")


if __name__ == '__main__':
    main()





