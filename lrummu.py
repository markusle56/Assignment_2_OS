from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        super().__init__(frames)
        self.time = 0
        self.page_access_time = {}
        self.isWrite = False
        self.debug = False

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        if page_number in self.page_table:
            self.page_access_time[page_number] = self.time
            self.time += 1
            if self.debug:
                print(f"Read page {page_number} from memory.")
        else:
            self.page_faults += 1
            self.disk_reads += 1
            self.load_page(page_number, False)
            if len(self.page_table) < self.num_frames and self.debug:
                print(f"Page fault: Loaded page {page_number} into memory.")

    def write_memory(self, page_number):
        if page_number in self.page_table:
            frame, _ = self.page_table[page_number]
            self.page_table[page_number] = (frame, True)
            self.page_access_time[page_number] = self.time
            self.time += 1
            if self.debug:
                print(f"Wrote to page {page_number} in frame {frame}.")
        else:
            self.page_faults += 1
            self.disk_reads += 1
            self.load_page(page_number, True)
            if len(self.page_table) < self.num_frames and self.debug:
                print(f"Page fault: Loaded page {page_number} and wrote to it.")
                
    def load_page(self, page_number, isWrite):
        if len(self.page_table) >= self.num_frames:
            self.replace_page(page_number, isWrite)
        else:
            frame = len(self.page_table)
            if isWrite:
                self.page_table[page_number] = (frame, True)
            else:
                self.page_table[page_number] = (frame, False)
            self.page_access_time[page_number] = self.time
            self.time += 1
            if self.debug:
                print(f"Loaded page {page_number} into frame {frame}.")
            
    def replace_page(self, page_number, isWrite):
        # Least recently used page
        lru_page = min(self.page_access_time, key=self.page_access_time.get)
        frame, dirty_bit = self.page_table[lru_page]
        #print(f"frame: {frame}, dirty bit: {dirty_bit}")
        
        if dirty_bit:
            self.disk_writes += 1
            if self.debug:
                print(f"Replaced dirty page {lru_page} with page {page_number} and wrote dirty page to disk.")
        else:
            if self.debug:
                print(f"Replaced page {lru_page} with page {page_number}.")
            
        del self.page_table[lru_page]
        del self.page_access_time[lru_page]
        if isWrite:
            self.page_table[page_number] = (frame, True)
        else:
            self.page_table[page_number] = (frame, False)
        self.page_access_time[page_number] = self.time
        self.time += 1
        if self.debug:
            print(f"Loaded page {page_number} into frame {frame}.")
            
    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults