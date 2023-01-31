import os
from typing import Callable, Optional

from update_io import UpdateFileManager, list_jsons
from update_model import VersionInfo
from update_view import UpdateViewMenus, UpdateViewInputs, UpdateViewOutputs


class UpdateController:
    def __init__(self, product: str, source_root: str, new_version_folder: str, recent_index_length: int):
        self._product: str = product
        self._new_version_folder: str = new_version_folder
        self._recent_index_length: int = recent_index_length
        self._files: UpdateFileManager = UpdateFileManager(source_root, product)

    @staticmethod
    def _file_exists_validator(path: str) -> Callable[[str], bool]:
        def _validator(name: str) -> bool:
            if os.path.exists(os.path.join(path, name)):
                UpdateViewOutputs.file_name_exist(name, path)
                return False
            return True

        return _validator

    def _choose_version_code_validator(self) -> Callable[[int], bool]:
        def _validator(code: int) -> bool:
            if self._files.has_version_code(code):
                return True
            else:
                UpdateViewOutputs.unknown_version_code(code)
                return False

        return _validator

    @staticmethod
    def get_product(source_root: str) -> Optional[str]:
        products = UpdateFileManager.get_products(source_root) if os.path.exists(source_root) else []
        product = UpdateViewMenus.choose_product_menu(products) if len(products) > 0 else None
        if product is None:
            product = UpdateViewInputs.create_new_product(UpdateController._file_exists_validator(source_root))
            if product is not None:
                UpdateFileManager.new_product(source_root, product)
                UpdateViewOutputs.new_product_created(product)
                return product
            else:
                return None
        return product

    def _get_new_version_template(self) -> Optional[VersionInfo]:
        new_versions = list_jsons(self._new_version_folder) if os.path.exists(self._new_version_folder) else []
        file_name = UpdateViewMenus.choose_version_template_menu(new_versions) if len(new_versions) > 0 else None
        if file_name is None:
            new_file_name = UpdateViewInputs.create_new_version_template(self._file_exists_validator(self._new_version_folder))
            if new_file_name is not None:
                new_file_path = self._files.save_template_version_info(new_file_name, self._new_version_folder)
                UpdateViewOutputs.new_version_template_created(new_file_path)
            return None
        else:
            return self._files.read_version_info(os.path.join(self._new_version_folder, file_name))

    def _reset_index(self):
        version_codes = self._files.list_version_codes()
        self._files.save_version_index_file(version_codes)
        version_indexes = [self._files.read_version_code_version_info(i).to_index() for i in version_codes[: self._recent_index_length]]
        self._files.save_recent_index_list(version_indexes)

    def _get_latest_version(self) -> Optional[VersionInfo]:
        version_codes = self._files.list_version_codes()
        if len(version_codes) > 0:
            return self._files.read_version_code_version_info(version_codes[0])
        return None

    def _reset_latest(self):
        latest_version_info = self._get_latest_version()
        if latest_version_info is not None:
            self._files.save_latest_version_info(latest_version_info)
            self._files.save_latest_download_info(latest_version_info)
        else:
            self._files.delete_latest_files()

    def _list_versions(self):
        versions = self._files.list_version_codes(descending=False)
        UpdateViewOutputs.list_versions(versions)

    def _check_add_old_version(self, version_info: VersionInfo) -> bool:
        latest_version_info = self._get_latest_version()
        if latest_version_info is not None and version_info.version_code < latest_version_info.version_code:
            return UpdateViewInputs.check_add_old_version(version_info.version_code, version_info.version_name)
        return True

    def _add_version(self, replaceable: bool):
        version_info = self._get_new_version_template()
        if version_info is None:
            return
        if not replaceable and not self._check_add_old_version(version_info):
            return
        version_exists = self._files.has_version_code(version_info.version_code)
        if not replaceable and version_exists:
            UpdateViewOutputs.same_version_code_exists(version_info.version_code)
        else:
            if replaceable and version_exists:
                old_version_info = self._files.read_version_code_version_info(version_info.version_code)
                if not UpdateViewInputs.validate_replace_version(
                    version_info.version_code, version_info.version_name, old_version_info.version_code, old_version_info.version_name
                ):
                    return
            self._files.save_version_code_version_info(version_info)
            self._reset_index()
            self._reset_latest()
            if replaceable:
                UpdateViewOutputs.new_version_replaced(version_info.version_code, version_info.version_name)
            else:
                UpdateViewOutputs.new_version_added(version_info.version_code, version_info.version_name)

    def _delete_version(self):
        version_code = UpdateViewInputs.get_delete_version_code(self._choose_version_code_validator())
        if version_code is None:
            return
        version_info = self._files.read_version_code_version_info(version_code)
        if not UpdateViewInputs.validate_delete_version(
            version_info.version_code,
            version_info.version_name,
        ):
            return
        self._files.delete_version_code_version_info(version_code)
        self._reset_index()
        self._reset_latest()
        UpdateViewOutputs.version_deleted(version_info.version_code, version_info.version_name)

    def launch_product_functions(self):
        UpdateViewMenus.product_functions_menu(
            product=self._product,
            on_list_versions=self._list_versions,
            on_add_version=lambda: self._add_version(False),
            on_replace_version=lambda: self._add_version(True),
            on_delete_version=self._delete_version,
        )
