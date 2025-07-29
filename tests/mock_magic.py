"""
Mock module for python-magic to bypass libmagic dependency during testing.
"""

class Magic:
    def __init__(self, mime=False, magic_file=None, keep_going=False, uncompress=False):
        self.mime = mime
        self.magic_file = magic_file
        self.keep_going = keep_going
        self.uncompress = uncompress
    
    def from_file(self, filename):
        """Mock file type detection"""
        if filename.endswith('.pdf'):
            return 'application/pdf'
        elif filename.endswith('.txt'):
            return 'text/plain'
        elif filename.endswith('.docx'):
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.doc'):
            return 'application/msword'
        else:
            return 'application/octet-stream'
    
    def from_buffer(self, buffer):
        """Mock buffer type detection"""
        if b'%PDF' in buffer[:4]:
            return 'application/pdf'
        elif b'PK' in buffer[:2]:
            return 'application/zip'
        else:
            return 'text/plain'

def from_file(filename, mime=False):
    """Mock function for magic.from_file"""
    magic = Magic(mime=mime)
    return magic.from_file(filename)

def from_buffer(buffer, mime=False):
    """Mock function for magic.from_buffer"""
    magic = Magic(mime=mime)
    return magic.from_buffer(buffer)