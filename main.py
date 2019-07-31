from ftplib import FTP
import os
import json
import threading


class ConnectionFTPError(Exception):
    pass


class CopyFilesFTP:
    def __init__(self, path: str):
        # Парсим конфиг файл
        self.path = path
        with open(self.path, 'r') as file:
            self.config = json.load(file)
        self.host = self.config['host']
        self.port = self.config['port'] if self.config['port'] else 21
        self.username = self.config['username']
        self.password = self.config['password']
        self.files = self.config['files']
        self.threads_num = self.config['threads']
        # Создаем подключение
        self.ftp_connection = self._connect_and_login()

    def _connect_and_login(self):
        try:
            ftp_obj = FTP(host=self.host, timeout=10)
            ftp_obj.connect(port=self.port)
            ftp_obj.login(self.username, self.password)
        except:
            raise ConnectionFTPError('Connection Error, check your connection data')
        return ftp_obj

    def upload_method(self, multi_thread: bool):
        # Если значение multi_thread - True загружаем файлы используя многопоточность
        if multi_thread:
            threads = [threading.Thread(target=self.upload_files, args=(file_path,)) for file_path in self.files]
            if self.threads_num < len(self.files):
                # Запускаем потоки и ждем их выполнения
                for i in range(0, len(threads), self.threads_num):
                    for y in threads[i:self.threads_num+i]:
                        y.start()
                        y.join()
        else:
            for file_path in self.files:
                self.upload_files(file_path)

    @staticmethod
    def is_file_text_extension(file_path: str):
        # Определяем расширение файла
        file_extension = os.path.splitext(file_path)[1]
        return file_extension in ['.txt', '.html', '.rtf', '.doc', '.docx', '.pdf', '.odt', '.htm']

    def upload_files(self, file_path: list):
        # Загружаем файлы на сервер
        # Если текущая директория отличается от той что прописана в конфиге, то меняем ее
        if self.ftp_connection.pwd() != file_path[1]:
            self.ftp_connection.cwd(file_path[1])
        with open(file_path[0], 'rb') as file:
            # Определяем расширение файла и тип загрузки
            if self.is_file_text_extension(file_path[0]):
                self.ftp_connection.storlines('STOR ' + file_path[0].split('/')[-1], file)
            else:
                self.ftp_connection.storbinary('STOR ' + file_path[0].split('/')[-1], file, 1024)
            print(file_path[0] + ' successfully uploaded')


ftp = CopyFilesFTP('config.json')
ftp.upload_method(multi_thread=True)
