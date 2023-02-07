import os
from typing import Callable, Optional

from update_io import UpdateFileManager
from update_model import VersionInfo
from update_view import UpdateViewMenus, UpdateViewInputs, UpdateViewOutputs


class UpdateController:
    def __init__(self, product: str, source_root: str, recent_index_length: int):
        self._product: str = product
        self._recent_index_length: int = recent_index_length
        self._files: UpdateFileManager = UpdateFileManager(source_root, product)

    @property
    def product(self) -> str:
        return self._product

    @property
    def files(self) -> str:
        return self._files

    @staticmethod
    def get_file_exists_validator(path: str) -> Callable[[str], bool]:
        def _validator(name: str) -> bool:
            if os.path.exists(os.path.join(path, name)):
                UpdateViewOutputs.file_name_exist(name, path)
                return False
            return True

        return _validator

    def get_choose_version_code_validator(self) -> Callable[[int], bool]:
        def _validator(code: int) -> bool:
            if self._files.has_version_code(code):
                return True
            else:
                UpdateViewOutputs.unknown_version_code(code)
                return False

        return _validator

    @staticmethod
    def create_product(source_root: str, name: str, validate: bool = True) -> Optional[str]:
        if not validate or UpdateController.get_file_exists_validator(source_root)(name):
            UpdateFileManager.new_product(source_root, name)
            UpdateViewOutputs.new_product_created(name)
            return name
        else:
            return None

    def create_new_version_template(self, new_version_folder: str, new_file_name: str, validate: bool = True) -> Optional[str]:
        if not validate or UpdateController.get_file_exists_validator(new_version_folder)(new_file_name):
            new_file_path = self._files.save_template_version_info(new_file_name, new_version_folder)
            UpdateViewOutputs.new_version_template_created(new_file_path)
            return new_file_path
        else:
            return None

    def reset_index(self):
        version_codes = self._files.list_version_codes()
        self._files.save_version_index_file(version_codes)
        version_indexes = [self._files.read_version_code_version_info(i).to_index() for i in version_codes[: self._recent_index_length]]
        self._files.save_recent_index_list(version_indexes)

    def get_latest_version(self) -> Optional[VersionInfo]:
        version_codes = self._files.list_version_codes()
        if len(version_codes) > 0:
            return self._files.read_version_code_version_info(version_codes[0])
        return None

    def reset_latest(self):
        latest_version_info = self.get_latest_version()
        if latest_version_info is not None:
            self._files.save_latest_version_info(latest_version_info)
            self._files.save_latest_download_info(latest_version_info)
        else:
            self._files.delete_latest_files()

    def reset_index_and_latest(self):
        self.reset_index()
        self.reset_latest()

    def get_versions(self) -> list[int]:
        return self._files.list_version_codes(descending=False)

    def is_adding_old_version(self, new_version_info: VersionInfo) -> bool:
        latest_version_info = self.get_latest_version()
        return latest_version_info is not None and new_version_info.version_code < latest_version_info.version_code

    def add_version(
        self,
        version_info: VersionInfo,
        replaceable: bool,
        on_adding_old_version: Optional[Callable[[VersionInfo], bool]] = None,
        on_replace_version: Optional[Callable[[VersionInfo], bool]] = None,
    ):
        if not replaceable and self.is_adding_old_version(version_info):
            if on_adding_old_version is not None and not on_adding_old_version(version_info):
                return
        version_exists = self._files.has_version_code(version_info.version_code)
        if not replaceable and version_exists:
            UpdateViewOutputs.same_version_code_exists(version_info.version_code)
        else:
            if replaceable and version_exists:
                old_version_info = self._files.read_version_code_version_info(version_info.version_code)
                if not on_replace_version(old_version_info):
                    return
            self._files.save_version_code_version_info(version_info)
            self.reset_index_and_latest()
            if replaceable:
                UpdateViewOutputs.new_version_replaced(version_info.version_code, version_info.version_name)
            else:
                UpdateViewOutputs.new_version_added(version_info.version_code, version_info.version_name)

    def delete_version(self, version_code: int, on_deleteing_version: Optional[Callable[[VersionInfo], bool]] = None):
        version_info = self._files.read_version_code_version_info(version_code)
        if on_deleteing_version is not None and not on_deleteing_version(version_info):
            return
        self._files.delete_version_code_version_info(version_code)
        self.reset_index_and_latest()
        UpdateViewOutputs.version_deleted(version_info.version_code, version_info.version_name)


class UpdateInteractiveController:
    def __init__(self, product: str, source_root: str, recent_index_length: int, new_version_folder: str):
        self._new_version_folder: str = new_version_folder
        self._controller = UpdateController(product, source_root, recent_index_length)

    @staticmethod
    def get_product(source_root: str) -> Optional[str]:
        products = UpdateFileManager.get_products(source_root)
        product = UpdateViewMenus.choose_product_menu(products) if len(products) > 0 else None
        if product is None:
            product = UpdateViewInputs.create_new_product(UpdateController.get_file_exists_validator(source_root))
            return UpdateController.create_product(source_root, product, False) if product is not None else None
        return product

    def _get_new_version_template(self) -> Optional[VersionInfo]:
        new_versions = UpdateFileManager.get_new_version_templates(self._new_version_folder)
        file_name = UpdateViewMenus.choose_version_template_menu(new_versions) if len(new_versions) > 0 else None
        if file_name is None:
            new_file_name = UpdateViewInputs.create_new_version_template(self._controller.get_file_exists_validator(self._new_version_folder))
            if new_file_name is not None:
                self._controller.create_new_version_template(self._new_version_folder, new_file_name, False)
            return None
        else:
            return self._controller._files.read_version_info(os.path.join(self._new_version_folder, file_name))

    def _list_versions(self):
        UpdateViewOutputs.list_versions(self._controller.get_versions())

    def _check_add_old_version(self, version_info: VersionInfo) -> bool:
        if self._controller.is_adding_old_version(version_info):
            return UpdateViewInputs.check_add_old_version(version_info.version_code, version_info.version_name)
        return True

    def _add_version(self, replaceable: bool):
        version_info = self._get_new_version_template()
        if version_info is None:
            return
        self._controller.add_version(
            version_info=version_info,
            replaceable=replaceable,
            on_adding_old_version=self._check_add_old_version,
            on_replace_version=lambda old_version_info: UpdateViewInputs.validate_replace_version(
                version_info.version_code, version_info.version_name, old_version_info.version_code, old_version_info.version_name
            ),
        )

    def _delete_version(self):
        version_code = UpdateViewInputs.get_delete_version_code(self._controller.get_choose_version_code_validator())
        if version_code is None:
            return
        self._controller.delete_version(
            version_code=version_code,
            on_deleteing_version=lambda version_info: UpdateViewInputs.validate_delete_version(
                version_info.version_code,
                version_info.version_name,
            ),
        )

    def _reset_index_and_latest(self):
        self._controller.reset_index_and_latest()
        UpdateViewOutputs.index_and_latest_refreshed()

    def launch_interactive_menu(self):
        UpdateViewMenus.product_functions_menu(
            product=self._controller.product,
            on_list_versions=self._list_versions,
            on_add_version=lambda: self._add_version(False),
            on_replace_version=lambda: self._add_version(True),
            on_delete_version=self._delete_version,
            on_refresh_index_and_latest=self._reset_index_and_latest,
        )
