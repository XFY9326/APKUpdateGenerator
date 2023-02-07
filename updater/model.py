from dataclasses import dataclass


@dataclass
class DownloadSource:
    source_name: str
    url: str
    is_direct_link: bool

    def to_dict(self) -> dict[str, any]:
        return {"sourceName": self.source_name, "url": self.url, "isDirectLink": self.is_direct_link}

    @staticmethod
    def empty_instance() -> "DownloadSource":
        return DownloadSource(source_name="", url="", is_direct_link=True)

    @staticmethod
    def from_dict(data: dict) -> "DownloadSource":
        return DownloadSource(source_name=data["sourceName"], url=data["url"], is_direct_link=data["isDirectLink"])


@dataclass
class VersionIndex:
    version: int
    force_update: bool

    def to_dict(self) -> dict[str, any]:
        return {"version": self.version, "forceUpdate": self.force_update}

    @staticmethod
    def from_dict(data: dict) -> "VersionIndex":
        return VersionIndex(version=data["version"], force_update=data["forceUpdate"])


@dataclass
class VersionInfo:
    version_code: int
    version_name: str
    force_update: bool
    change_log: str
    download_source: list[DownloadSource]

    def to_dict(self) -> dict[str, any]:
        return {
            "versionCode": self.version_code,
            "versionName": self.version_name,
            "forceUpdate": self.force_update,
            "changeLog": self.change_log,
            "downloadSource": [i.to_dict() for i in self.download_source],
        }

    def to_index(self) -> VersionIndex:
        return VersionIndex(version=self.version_code, force_update=self.force_update)

    def to_download_dict(self) -> dict[str, any]:
        recommend_source = None
        if len(self.download_source) > 0:
            direct_sources = [i for i in self.download_source if i.is_direct_link]
            if len(direct_sources) > 0:
                recommend_source = direct_sources[0]
            else:
                recommend_source = self.download_source[0]
        return {
            "versionCode": self.version_code,
            "versionName": self.version_name,
            "url": recommend_source.url if recommend_source is not None else None,
        }

    @staticmethod
    def empty_instance() -> "VersionInfo":
        return VersionInfo(version_code=0, version_name="", force_update=False, change_log="", download_source=[DownloadSource.empty_instance()])

    @staticmethod
    def from_dict(data: dict) -> "VersionInfo":
        return VersionInfo(
            version_code=data["versionCode"],
            version_name=data["versionName"],
            force_update=data["forceUpdate"],
            change_log=data["changeLog"],
            download_source=[DownloadSource.from_dict(i) for i in data["downloadSource"]],
        )
