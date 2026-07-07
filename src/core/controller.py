import threading
from src.core.config_manager import ConfigManager
from src.services.gemini_extractor import GeminiExtractor
from src.services.docx_generator import DocxGenerator
from src.services.validator import DataValidator
from src.core.logger import logger

class AppController:
    def __init__(self, ui_callback):
        self.config = ConfigManager()
        self.ui_callback = ui_callback # Method to update UI thread safely
        self.current_data = None
        self.current_file = None

    def process_ticket_async(self, file_path):
        self.current_file = file_path
        thread = threading.Thread(target=self._process_ticket_task)
        thread.start()

    def _process_ticket_task(self):
        try:
            api_key = self.config.get("gemini_api_key")
            extractor = GeminiExtractor(api_key)
            
            self.ui_callback("status", "Extracting data with AI...")
            data = extractor.process_document(self.current_file)
            
            self.ui_callback("status", "Validating extracted data...")
            warnings = DataValidator.validate(data)
            
            self.current_data = data
            self.ui_callback("data_ready", {"data": data.model_dump_json(indent=2), "warnings": warnings})
            
        except Exception as e:
            self.ui_callback("error", str(e))

    def generate_document_async(self):
        thread = threading.Thread(target=self._generate_doc_task)
        thread.start()

    def _generate_doc_task(self):
        try:
            self.ui_callback("status", "Generating DOCX file...")
            template = self.config.get("template_path")
            output = self.config.get("output_directory")
            
            generator = DocxGenerator(template, output)
            filepath = generator.generate(self.current_data)
            
            self.ui_callback("success", f"Document generated:\n{filepath}")
        except Exception as e:
            self.ui_callback("error", str(e))