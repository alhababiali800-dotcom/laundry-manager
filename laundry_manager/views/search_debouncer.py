from PyQt6.QtCore import QTimer, pyqtSignal, QObject

class SearchDebouncer(QObject):
    """Debounce rapid search input to avoid excessive database queries."""
    search_triggered = pyqtSignal(str)
    
    def __init__(self, delay_ms=300):
        super().__init__()
        self.delay_ms = delay_ms
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timeout)
        self.pending_query = None
    
    def on_text_changed(self, query):
        """Call this from search input's textChanged signal."""
        self.pending_query = query
        self.timer.stop()
        self.timer.start(self.delay_ms)
    
    def _on_timeout(self):
        if self.pending_query is not None:
            self.search_triggered.emit(self.pending_query)
            self.pending_query = None
        self.timer.stop()
    
    def cancel(self):
        """Cancel pending search."""
        self.timer.stop()
        self.pending_query = None
