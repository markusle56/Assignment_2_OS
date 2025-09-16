import random
from mmu import MMU

class RandMMU(MMU):
    def __init__(self, frames):
        super().__init__()
        self.frame = []
        self.max_framess = frames
        self.page_faults = 0
        self.disk_reads = 0
        self.disk_writes = 0
        self.mode = "debug"

    def set_debug(self):
        self.mode = "debug"

    def reset_debug(self):
        self.mode = "quiet"

    def print_debug(self, msg):
        if self.mode == "debug":
            print(msg)
            
    def read_memory(self, page_number):
        if page_number in self.frame:
            self.print_debug(f"READ: Page {page_number} already in frame (HIT).")
            return 
    
        self.print_debug(f"READ: Page {page_number} not in frame (FAULT).")
        if len(self.frame) >= self.max_frames:
            overwrite_page = random.randint(0, self.max_frames - 1)
            self.print_debug(f"      Drop page {self.frame[overwrite_page]}")
            self.frame[overwrite_page] = page_number
            self.disk_reads += 1
            self.page_faults += 1
        else:
            self.frame.append(page_number)
            self.print_debug(f"      Loading page {page_number} into free frame.")
            self.page_faults += 1
            self.disk_reads += 1 

    def write_memory(self, page_number):
        if page_number in self.frame:
            self.print_debug(f"WRITE: Page {page_number} already in frame (HIT).")
            return 
        
        self.print_debug(f"WRITE: Page {page_number} not in frame (FAULT).")
        self.disk_reads += 1
        if len(self.frame) >= self.max_frames:
            overwrite_page = random.randint(0, self.max_frames - 1)
            self.print_debug(f"      Drop page {self.frame[overwrite_page]}")
            self.frame[overwrite_page] = page_number
            self.disk_writes += 1
            self.page_faults += 1
        else:
            self.frame.append(page_number)
            self.print_debug(f"      Loading page {page_number} into free frame.")
            self.page_faults += 1
            self.disk_writes += 1 

    def get_total_disk_reads(self):
        return self.disk_reads
    

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
