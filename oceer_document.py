import re


class OceerDocument:
    def __init__(self):
        self.page_text = []
        self.page_vertices = []
        self.page_size = []

    def get_document_length(self):
        return len(self.page_text)

    def get_page(self, index, add_indication=False):
        if add_indication:
            return f"=== Page : {index + 1} ===\n\n" + self.page_text[index].rstrip()

        return self.page_text[index].rstrip()

    # act like a range start : 0, end : 3 -> 0, 1, 2
    def get_pages_by_region(self, start, end, add_indication=False):
        pages_text = ''
        for i in range(start, end):
            pages_text += '\n' + re.sub(r'\.{2,}', '.', self.get_page(i, add_indication).replace("…", "."))

        return pages_text

    def merge_document(self, doc_to_merge):
        for page in doc_to_merge.page_text:
            self.page_text.append(page)

        for page_vertices in doc_to_merge.page_vertices:
            self.page_vertices.append(page_vertices)

        for page_size in doc_to_merge.page_size:
            self.page_size.append(page_size)

    def cut_document(self, start, end):
        document = OceerDocument()
        for i in range(start, end):
            if 0 <= i < self.get_document_length():
                document.page_text.append(self.page_text[i])
            if 0 <= i < len(self.page_vertices):
                document.page_vertices.append(self.page_vertices[i])

            if 0 <= i < len(self.page_size):
                document.page_size.append(self.page_size[i])

        return document

    def to_json(self):
        return {
            "page_text": self.page_text,
            "page_vertices": self.page_vertices,
            "page_size": self.page_size
        }

    def to_v1_json(self):
        return {
            "raw": self.page_text,
            "treated": self.page_text,
            "paragraphs": self.page_vertices,
            "page_size": self.page_size
        }

    def load_old_oceer_format(self, json_data):
        self.page_text = json_data.get("raw", [])
        self.page_vertices = json_data.get("paragraphs", [])
        self.page_size = json_data.get("page_size", [])

    def from_json(self, json_data):
        if 'raw' in json_data:
            self.load_old_oceer_format(json_data)
        else:
            self.page_text = json_data.get("page_text", [])
            self.page_vertices = json_data.get("page_vertices", [])
            self.page_size = json_data.get("page_size", [])

    def __str__(self):
        text_preview = next((text.lstrip()[:50] for text in self.page_text if text.strip()), 'No text available')
        if text_preview != 'No text available':
            text_preview += '...' if len(text_preview) >= 50 else ''

        details = [
            f"Number of pages: {len(self.page_text)}",
            f"Text Preview: {text_preview}",
            f"Number of vertices: {len(self.page_vertices) if self.page_vertices else 'No vertices available'}"
        ]
        return "OceerDocument:\n" + "\n".join(details)

    def copy(self):
        new_doc = OceerDocument()
        new_doc.page_text = self.page_text[:]
        new_doc.page_vertices = [vertices[:] for vertices in self.page_vertices]
        new_doc.page_size = self.page_size[:]
        return new_doc
