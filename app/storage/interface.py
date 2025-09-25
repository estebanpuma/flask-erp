from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    def save(self, module: str, file_stream, filename: str) -> str:
        """Guarda el archivo y devuelve el nombre o ruta relativa."""

    @abstractmethod
    def delete(self, module: str, filename: str) -> None:
        """Elimina un archivo."""

    @abstractmethod
    def url(self, module: str, filename: str) -> str:
        """Devuelve la URL pública para servir la imagen."""
