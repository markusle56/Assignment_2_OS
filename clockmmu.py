from mmu import MMU


class ClockMMU(MMU):
    def __init__(self, frames):
        self.num_frames = frames
        self.frames = [None] * frames
        self.reference_bits = [0] * frames
        self.dirty_bits = [0] * frames
        self.pointer = 0
        self.page_table = {}
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
            if self.debug:
                print(f"Read hit: page {page_number} in frame {frame}")
        else:
            self.total_page_faults += 1
            self.total_disk_reads += 1
            self._replace_page(page_number, is_write=False)
            if self.debug:
                print(f"Read miss: page {page_number} loaded")

    def write_memory(self, page_number):
        if page_number in self.page_table:
            frame = self.page_table[page_number]
            self.reference_bits[frame] = 1
            self.dirty_bits[frame] = 1
            if self.debug:
                print(f"Write hit: page {page_number} in frame {frame}")
        else:
            self.total_page_faults += 1
            self.total_disk_reads += 1
            self._replace_page(page_number, is_write=True)
            if self.debug:
                print(f"Write miss: page {page_number} loaded and marked dirty")

    def _replace_page(self, page_number, is_write):
        while True:
            if self.frames[self.pointer] is None:
                break
            if self.reference_bits[self.pointer] == 0:
                break
            self.reference_bits[self.pointer] = 0
            self.pointer = (self.pointer + 1) % self.num_frames

        evicted_page = self.frames[self.pointer]
        if evicted_page is not None:
            if self.dirty_bits[self.pointer]:
                self.total_disk_writes += 1
            del self.page_table[evicted_page]

        self.frames[self.pointer] = page_number
        self.reference_bits[self.pointer] = 1
        self.dirty_bits[self.pointer] = 1 if is_write else 0
        self.page_table[page_number] = self.pointer
        self.pointer = (self.pointer + 1) % self.num_frames

    def get_total_disk_reads(self):
        return self.total_disk_reads

    def get_total_disk_writes(self):
        return self.total_disk_writes

    def get_total_page_faults(self):
        return self.total_page_faults
