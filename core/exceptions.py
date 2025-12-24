class SayonarBaseError(Exception):
    """Barcha loyiha xatoliklari uchun asosiy klass."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

# ==================== SMARTUP XATOLIKLARI ====================
class SmartupError(SayonarBaseError):
    """Smartup API bilan bog'liq umumiy xatolik."""
    pass

class InvalidZipFileError(SmartupError):
    """ZIP fayl noto'g'ri yoki buzilgan bo'lganda."""
    pass

# ==================== SFTP XATOLIKLARI ====================
class SFTPError(SayonarBaseError):
    """SFTP ulanishi yoki fayl yuklash bilan bog'liq xatolik."""
    pass

class SFTPConnectionError(SFTPError):
    """Serverga ulanib bo'lmaganda."""
    pass

# ==================== FAYL TIZIMI XATOLIKLARI ====================
class FileProcessingError(SayonarBaseError):
    """Fayllarni ochish yoki o'chirish bilan bog'liq xatolik."""
    pass

class NoXmlFilesError(FileProcessingError):
    """ZIP ichida XML fayllar topilmaganda."""
    pass