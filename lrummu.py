from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        self.num_frames = frames
        self.frames = [None] * frames
        self.reference_bits = [0] * frames
        self.dirty_bits = [0] * frames
        self.page_table = {}
        self.time = 0
        self.page_access_time = {}
        self.total_disk_reads = 0
        self.total_disk_writes = 0
        self.total_page_faults = 0
        self.debug = False

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        if page_number in self.page_table:
            frame = self.page_table[page_number]
            self.reference_bits[frame] = 1
            self.page_access_time[page_number] = self.time
            self.time += 1
            if self.debug:
                print(f"Read hit: page {page_number} in frame {frame}")
        else:
            self.total_page_faults += 1
            self.total_disk_reads += 1
            self.load_page(page_number, is_write = False)
            if self.debug:
                print(f"Read miss: page {page_number} loaded")

    def write_memory(self, page_number):
        if page_number in self.page_table:
            frame = self.page_table[page_number]
            self.reference_bits[frame] = 1
            self.dirty_bits[frame] = 1
            self.page_access_time[page_number] = self.time
            self.time += 1
            if self.debug:
                print(f"Write hit: page {page_number} in frame {frame}")
        else:
            self.total_page_faults += 1
            self.total_disk_reads += 1
            self.load_page(page_number, is_write = True)
            if self.debug:
                print(f"Write miss: page {page_number} loaded and marked dirty")
                
    def load_page(self, page_number, is_write):
        if len(self.page_table) >= self.num_frames:
            self.replace_page(page_number, is_write)
        else:
            frame = len(self.page_table)
            if is_write:
                self.page_table[page_number] = frame
                self.dirty_bits[frame] = 1
            else:
                self.page_table[page_number] = frame
                self.dirty_bits[frame] = 0
            self.page_access_time[page_number] = self.time
            self.time += 1
            if self.debug:
                print(f"Loaded page {page_number} into frame {frame}.")
            
    def replace_page(self, page_number, isWrite):
        # Least recently used page
        lru_page = min(self.page_access_time, key=self.page_access_time.get)
        frame = self.page_table[lru_page]
        dirty_bit = self.dirty_bits[frame]
        #print(f"frame: {frame}, dirty bit: {dirty_bit}")
        
        if dirty_bit:
            self.total_disk_writes += 1
            if self.debug:
                print(f"Replaced dirty page {lru_page} with page {page_number} and wrote dirty page to disk.")
        else:
            if self.debug:
                print(f"Replaced page {lru_page} with page {page_number}.")
            
        del self.page_table[lru_page]
        del self.page_access_time[lru_page]
        if isWrite:
            self.page_table[page_number] = frame
            self.dirty_bits[frame] = 1
        else:
            self.page_table[page_number] = frame
            self.dirty_bits[frame] = 0
        self.page_access_time[page_number] = self.time
        self.time += 1
        if self.debug:
            print(f"Loaded page {page_number} into frame {frame}.")
            
    def get_total_disk_reads(self):
        return self.total_disk_reads

    def get_total_disk_writes(self):
        return self.total_disk_writes

    def get_total_page_faults(self):
        return self.total_page_faults
