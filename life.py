import tkinter
from collections import defaultdict


class life:
    def __init__(self, width, height):
        """
        width and height are number of boxes on each side.
        """
        self.width = int(width)
        self.height = int(height)

        self.root = tkinter.Tk()

        self.vertical_margin = 15
        self.horizontal_margin = 50
        self.cell_size = 10
        self.grid_height = self.height*self.cell_size
        self.grid_width = self.width*self.cell_size

        # Name attributes which will be created in setup
        self.canvas = None
        self.id_matrix = None
        self.living_pixel_list = set()
        self.setup()

        self.currently_flipped_pixels = set()

        self.running = False
        max_updates_per_second = 20
        self.delay_ms = max(1, 1000//max_updates_per_second)
        self.root.after(self.delay_ms, self.loop)
        self.root.mainloop()

    def setup(self):
        """
        Creates initial grid and pattern as well as button bindings.
        """

        canvas_height = self.grid_height+2*self.vertical_margin
        canvas_width = self.grid_width+2*self.horizontal_margin

        # Construct canvas object
        self.frame = tkinter.Frame(self.root, bg="white", height=canvas_height, width=canvas_width)
        self.canvas = tkinter.Canvas(self.root, bg="white", height=canvas_height, width=canvas_width)
        self.canvas.bind("<ButtonPress-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.pack(side=tkinter.RIGHT)

        self.run_stop_text = tkinter.StringVar()
        button = tkinter.Button(self.frame,
                                textvariable=self.run_stop_text,
                                command=self.run_stop,
                                width=5,
                                height=2)
        self.run_stop_text.set("Run")
        button.pack(side=tkinter.TOP)
        self.frame.pack(side=tkinter.LEFT)



        #button.pack(side=tkinter.LEFT)

        # Create grid
        # Horizontal lines
        for i in range(self.height+1):
            x1 = self.horizontal_margin
            x2 = self.horizontal_margin+self.grid_width
            y1 = self.vertical_margin+i*self.cell_size
            y2 = y1
            self.canvas.create_line(x1, y1, x2, y2)

        # Vertical lines
        for i in range(self.width+1):
            x1 = self.horizontal_margin+i*self.cell_size
            x2 = x1
            y1 = self.vertical_margin
            y2 = self.vertical_margin+self.grid_height
            self.canvas.create_line(x1, y1, x2, y2)

        # Matrix containing ids of each cell in the grid on the canvas
        self.id_matrix = []
        # width
        for i in range(self.width):
            c = []
            # height
            for j in range(self.height):
                sy = self.horizontal_margin+i*self.cell_size
                sx = self.vertical_margin+j*self.cell_size
                Id = self.canvas.create_rectangle(
                    sy, sx, sy+self.cell_size, sx+self.cell_size, fill="white")

                c.append(Id)

            self.id_matrix.append(c)

        glider = [(2, 1), (3, 2), (3, 3), (2, 3), (1, 3)]
        for point in glider:
            self.canvas.itemconfig(self.id_matrix[point[0]][point[1]], fill="black")

        self.living_pixel_list = set(glider)

    def is_alive(self, x, y):
        return (x, y) in self.living_pixel_list

    def num_neighbors(self, x, y):
        tot = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (j == 0 and i == 0):
                    tot += self.is_alive((x+i) % self.width, (y+j) % self.height)

        return tot

    def adjoining_pixel_indices(self, pxl):  # list of all neighbors in format [(x,y)]
        all_neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (j == 0 and i == 0):
                    all_neighbors.append(((pxl[0]+i) % self.width, (pxl[1]+j) % self.height))

        return all_neighbors

    def births(self, lpl):
        """
        Return location of pixels that are currently not living but have 3
        living neighbors. These will be living in the next generation.
        """
        locations = set()

        # Find number of living neighbors for empty pixel neighbors of
        # living pixels
        neighbor_count = defaultdict(int)
        for pxl in lpl:
            for neighbor in self.adjoining_pixel_indices(pxl):
                if neighbor not in lpl:
                    neighbor_count[neighbor] += 1

        for pxl, count in neighbor_count.items():
            if count == 3:
                locations.add(pxl)

        return locations

    def update_generation(self):
        """
        Process new generation for game of life.
        Determines the pixels which change color in new generation and updates
        the canvas to correspond.

        Also updates the living pixel list.
        """
        # set of pixels that die from too many or too few neighbors
        dying_locations = set()
        for pxl in self.living_pixel_list:
            n = self.num_neighbors(pxl[0], pxl[1])

            if n > 3 or n < 2:
                dying_locations.add(pxl)

        # Set of dead pixels which change to alive this generation
        birth_locations = self.births(self.living_pixel_list)

        for pxl in dying_locations:
            self.canvas.itemconfig(self.id_matrix[pxl[0]][pxl[1]], fill="white")

        for pxl in birth_locations:
            self.canvas.itemconfig(self.id_matrix[pxl[0]][pxl[1]], fill="black")

        self.living_pixel_list -= dying_locations
        self.living_pixel_list |= birth_locations

    def event_flip(self, event):
        """
        Checks click events for location and swaps the state of the pixel at
        that location.
        """
        event_left = event.x < self.horizontal_margin
        event_right = event.x >= self.horizontal_margin+self.grid_width
        event_above = event.y < self.vertical_margin
        event_below = event.y >= self.vertical_margin+self.grid_height

        outside = event_left or event_right or event_above or event_below

        if not (self.running) and not outside:
            # Flip cell. Not allowed after starting.
            i = int((event.x-self.horizontal_margin)/self.cell_size)
            j = int((event.y-self.vertical_margin)/self.cell_size)
            if (i, j) not in self.currently_flipped_pixels:
                self.currently_flipped_pixels.add((i, j))
                if self.is_alive(i, j):
                    self.canvas.itemconfig(self.id_matrix[i][j], fill="white")
                    self.living_pixel_list.remove((i, j))
                else:
                    self.canvas.itemconfig(self.id_matrix[i][j], fill="black")
                    self.living_pixel_list.add((i, j))

    # Callback functions
    def click(self, event):
        self.currently_flipped_pixels = set()

        self.event_flip(event)

    def drag(self, event):
        self.event_flip(event)

    def run_stop(self):
        self.running = not self.running

        if self.running:
            self.run_stop_text.set("Stop")
        else:
            self.run_stop_text.set("Run")

    def loop(self):
        if self.running:
            self.update_generation()

        self.root.after(self.delay_ms, self.loop)


if __name__ == '__main__':
    game = life(50, 50)
