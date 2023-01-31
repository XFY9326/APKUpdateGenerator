import os
import json
from typing import Union, Optional
from update_model import VersionInfo, VersionIndex


def list_jsons(folder_path: str) -> list[str]:
    return sorted(
        [i for i in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, i)) and i.endswith(".json") and not i.startswith(".")]
    )


def _load_json(path: str) -> Union[dict, list]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(path: str, content: Union[dict, list]):
    with open(path, "w", encoding="utf-8") as f:
        return json.dump(content, f)


def _prepare_parent_dir(path: str):
    parent_dir = os.path.dirname(path)
    if not parent_dir.isspace() or len(parent_dir) == 0:
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)


class UpdateFileManager:
    _VERSIONS_DIR = "Version"
    _VERSIONS_INDEX_FILE = "Index"
    _RECENT_INDEX_FILE = "Index"
    _LATEST_FILE = "Latest"
    _LATEST_DOWNLOAD_FILE = "LatestDownload"

    def __init__(self, source_root: str, product: str):
        self._source_root: str = source_root
        self._product: str = product
        self._product_root: str = os.path.join(source_root, product)
        if not os.path.exists(self._product_root):
            raise FileNotFoundError(self._product_root)

    @property
    def source_root(self) -> str:
        return self._source_root

    @property
    def product_root(self) -> str:
        return self._product_root

    @property
    def product_name(self) -> str:
        return self._product

    @property
    def versions_dir(self) -> str:
        return os.path.join(self._product_root, self._VERSIONS_DIR)

    @property
    def versions_index_file(self) -> str:
        return os.path.join(self.versions_dir, self._VERSIONS_INDEX_FILE)

    def version_file(self, version_code: int) -> str:
        return os.path.join(self.versions_dir, str(version_code))

    @property
    def recent_index_file(self) -> str:
        return os.path.join(self._product_root, self._RECENT_INDEX_FILE)

    @property
    def latest_file(self) -> str:
        return os.path.join(self._product_root, self._LATEST_FILE)

    @property
    def latest_download_file(self) -> str:
        return os.path.join(self._product_root, self._LATEST_DOWNLOAD_FILE)

    @staticmethod
    def read_version_info(path: str) -> VersionInfo:
        return VersionInfo.from_dict(_load_json(path))

    @staticmethod
    def delete_version_info(path: str):
        os.remove(path)

    def read_version_code_version_info(self, version_code: int) -> VersionInfo:
        return self.read_version_info(self.version_file(version_code))

    def delete_version_code_version_info(self, version_code: int):
        self.delete_version_info(self.version_file(version_code))

    def read_recent_version_index_list(self, num: Optional[int] = None, descending: bool = True) -> list[VersionIndex]:
        indexes = [VersionIndex.from_dict(i) for i in _load_json(self.recent_index_file)]
        indexes.sort(key=lambda x: x.version, reverse=descending)
        if num is not None:
            indexes = indexes[:num]
        return indexes

    def _get_version_code_list(self) -> list[int]:
        folder_path = self.versions_dir
        if not os.path.exists(folder_path):
            return []
        else:
            return [int(i) for i in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, i)) and i.isdigit()]

    def list_version_codes(self, descending: bool = True) -> list[int]:
        versions = self._get_version_code_list()
        versions.sort(reverse=descending)
        return versions

    def has_version_code(self, version_code: int) -> bool:
        versions = self._get_version_code_list()
        return version_code in versions

    @staticmethod
    def save_version_info(path: str, info: VersionInfo):
        _prepare_parent_dir(path)
        _dump_json(path, info.to_dict())

    def save_version_code_version_info(self, info: VersionInfo):
        self.save_version_info(self.version_file(info.version_code), info)

    def save_latest_version_info(self, info: VersionInfo):
        self.save_version_info(self.latest_file, info)

    def save_template_version_info(self, name: str, path: str) -> str:
        if not name.endswith(".json"):
            name += ".json"
        file_path = os.path.join(path, name)
        self.save_version_info(file_path, VersionInfo.empty_instance())
        return file_path

    def save_latest_download_info(self, info: VersionInfo):
        _prepare_parent_dir(self.latest_download_file)
        _dump_json(self.latest_download_file, info.to_download_dict())

    def save_recent_index_list(self, indexes: list[VersionIndex]):
        _prepare_parent_dir(self.recent_index_file)
        _dump_json(self.recent_index_file, [i.to_dict() for i in indexes])

    def save_version_index_file(self, version_codes: list[int]):
        _prepare_parent_dir(self.recent_index_file)
        _dump_json(self.versions_index_file, version_codes)

    def delete_latest_files(self):
        os.remove(self.latest_file)
        os.remove(self.latest_download_file)

    @staticmethod
    def new_product(source_root: str, product: str):
        product_dir = os.path.join(source_root, product)
        if not os.path.exists(product_dir):
            os.makedirs(product_dir)

    @staticmethod
    def get_products(source_root: str) -> list[str]:
        return sorted([i for i in os.listdir(source_root) if os.path.isdir(os.path.join(source_root, i)) and not i.startswith(".")])
