from ftplib import FTP
import os
import json
import time
import threading


class CopyFilesFTP:
    def __init__(self, path: str):
        # Парсим конфиг файл
        self.path = path
        self.config = json.load(open(self.path, 'r'))
        self.host = self.config['host']
        self.port = self.config['port'] if self.config['port'] else 21
        self.username = self.config['username']
        self.password = self.config['password']
        self.files = self.config['files']
        # Создаем подключение
        self.ftp_connection = self._connect_and_login()

    def _connect_and_login(self):
        ftp_obj = FTP(host=self.host, timeout=10)
        ftp_obj.connect(port=self.port)
        ftp_obj.login(self.username, self.password)
        return ftp_obj

    def upload_method(self, multi_thread: bool):
        # Если значение multi_thread - True загружаем файлы используя многопоточность
        for file_path in self.files:
            if multi_thread:
                t = threading.Thread(target=self.upload_files, args=(file_path, ))
                t.start()
                time.sleep(1)
            else:
                self.upload_files(file_path)

    @staticmethod
    def is_file_text_extension(file_path: str):
        # Определяем расширение файла
        file_extension = os.path.splitext(file_path)[1]
        return file_extension in ['.txt', '.html', '.rtf', '.doc', '.docx', '.pdf', '.odt', '.htm']

    def upload_files(self, file_path):
        # Загружаем файлы на сервер
        # Если текущая директория отличается от той что прописана в конфиге, то меняем ее
        if self.ftp_connection.pwd() != self.config['files'][file_path]:
            self.ftp_connection.cwd(self.config['files'][file_path])
        with open(file_path, 'rb') as file:
            # Определяем расширение файла и тип загрузки
            if self.is_file_text_extension(file_path):
                self.ftp_connection.storlines('STOR ' + file_path.split('/')[-1], file)
            else:
                self.ftp_connection.storbinary('STOR ' + file_path.split('/')[-1], file, 1024)
            print(file_path + ' successfully uploaded')


ftp = CopyFilesFTP('config.json')
ftp.upload_method(multi_thread=True)
