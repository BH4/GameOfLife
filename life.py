import tkinter


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
        self.living_pixel_list = None
        self.setup()

        self.currently_flipped_pixels = set()

        self.running = False
        self.root.after(1, self.loop)
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
                                command=self.run_stop)
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

        self.living_pixel_list = glider

    def is_alive(self, x, y):
        Id = self.id_matrix[x][y]
        return self.canvas.itemcget(Id, "fill") == "black"

    def num_neighbors(self, x, y):
        tot = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not(j == 0 and i == 0):
                    tot += self.is_alive((x+i) % self.width, (y+j) % self.height)

        return tot

    def adjoining_pixel_indices(self, pxl):  # list of all neighbors in format [(x,y)]
        all_neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (j == 0 and i == 0):
                    all_neighbors.append(((pxl[0]+i) % self.width, (pxl[1]+j) % self.height))

        return all_neighbors

    def union(self, a, b):
        return list(set(a) | set(b))

    def matrix_union(self, M):
        U = []
        for i in M:
            U = self.union(U, i)

        return U

    def difference(self, a, b):
        return list(set(a) - set(b))

    def births(self, lpl):
        """
        Pixels that are currently not living but have 3 living neighbors will
        be living next generation.
        """
        locations = []

        neighbor_matrix = []
        for pxl in lpl:
            neighbor_matrix.append(self.adjoining_pixel_indices(pxl))

        neighbor_union = self.matrix_union(neighbor_matrix)

        dead_neighbor_union = self.difference(neighbor_union, lpl)

        for pxl in dead_neighbor_union:
            count = 0
            for row in neighbor_matrix:  # could speed up by not continuing after count==4
                if pxl in row:
                    count += 1

            if count == 3:
                locations.append(pxl)

        return locations

    def switch_matrix(self):  # switches colors of appropriate entries, returns new live pixel list
        spl = []  # switch pixel list
        for pxl in self.living_pixel_list:
            n = self.num_neighbors(pxl[0], pxl[1])

            if n > 3 or n < 2:
                spl.append(pxl)

        # list of dead pixel list to switch
        sdpl = self.births(self.living_pixel_list)

        nlpl = self.difference(self.living_pixel_list, spl)  # new live pxl list
        for pxl in spl:
            self.canvas.itemconfig(self.id_matrix[pxl[0]][pxl[1]], fill="white")

        nlpl.extend(sdpl)
        for pxl in sdpl:
            self.canvas.itemconfig(self.id_matrix[pxl[0]][pxl[1]], fill="black")

        return nlpl

    def event_flip(self, event):
        event_left = event.x < self.horizontal_margin
        event_right = event.x >= self.horizontal_margin+self.grid_width
        event_above = event.y < self.vertical_margin
        event_below = event.y >= self.vertical_margin+self.grid_height

        if event_left or event_right or event_above or event_below:
            # Clicking outside the grid starts the run
            # self.running = True
            pass
        elif not(self.running):
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
                    self.living_pixel_list.append((i, j))

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
            self.living_pixel_list = self.switch_matrix()

        self.root.after(1, self.loop)


if __name__ == '__main__':
    game = life(50, 50)
