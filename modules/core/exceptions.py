class XDownloaderException(Exception): pass
class NavigationException(XDownloaderException): pass
class LoginException(XDownloaderException): pass
class ExtractionException(XDownloaderException): pass
class DownloadException(XDownloaderException): pass
class ConfigurationException(XDownloaderException): pass