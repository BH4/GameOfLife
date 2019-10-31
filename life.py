import tkinter


class life:
    def __init__(self, width, height):
        """
        width and height are number of boxes on each side.
        """
        self.width = int(width)
        self.height = int(height)

        self.root = tkinter.Tk()

        self.verticle_margin = 15
        self.horizontal_margin = 50
        self.cell_size = 10
        self.grid_height = height*self.cell_size
        self.grid_width = width*self.cell_size

        # Name attributes which will be created in setup
        self.canvas = None
        self.idMatrix = None
        self.livingPixelList = None
        self.setup()

        self.currently_flipped_pixels = set()

        self.end_startup = False
        self.root.after(1, self.loop)
        self.root.mainloop()

    def setup(self):
        """
        Creates initial grid and pattern as well as button bindings.
        """

        numH = self.height
        canvas_height = self.grid_height+2*self.verticle_margin

        numW = self.width
        canvas_width = self.grid_width+2*self.horizontal_margin

        # Construct canvas object
        self.canvas = tkinter.Canvas(self.root, bg="white", height=canvas_height, width=canvas_width)
        self.canvas.bind("<ButtonPress-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.pack()

        # Create grid
        # Horizontal lines
        for i in range(numH+1):
            x1 = self.horizontal_margin
            x2 = self.horizontal_margin+self.grid_width
            y1 = self.verticle_margin+i*self.cell_size
            y2 = y1
            self.canvas.create_line(x1, y1, x2, y2)

        # Vertical lines
        for i in range(numW+1):
            x1 = self.horizontal_margin+i*self.cell_size
            x2 = x1
            y1 = self.verticle_margin
            y2 = self.verticle_margin+self.grid_height
            self.canvas.create_line(x1, y1, x2, y2)

        # Matrix containing ids of each cell in the grid on the canvas
        self.idMatrix = []
        # width
        for i in range(numW):
            c = []
            # height
            for j in range(numH):
                sy = self.horizontal_margin+i*self.cell_size
                sx = self.verticle_margin+j*self.cell_size
                Id = self.canvas.create_rectangle(
                    sy, sx, sy+self.cell_size, sx+self.cell_size, fill="white")

                c.append(Id)

            self.idMatrix.append(c)

        glider = [(2, 1), (3, 2), (3, 3), (2, 3), (1, 3)]
        for point in glider:
            self.canvas.itemconfig(self.idMatrix[point[0]][point[1]], fill="black")

        self.livingPixelList = glider

    def is_alive(self, x, y):
        Id = self.idMatrix[x][y]
        return self.canvas.itemcget(Id, "fill") == "black"

    def num_neighbors(self, x, y):
        tot = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not(j == 0 and i == 0):
                    tot += self.is_alive((x+i) % self.width, (y+j) % self.height)

        return tot

    def adjoining_pixel_indices(self, pxl):  # list of all neighbors in format [(x,y)]
        allN = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not(j == 0 and i == 0):
                    allN.append(((pxl[0]+i) % self.width, (pxl[1]+j) % self.height))

        return allN

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

        neighborMatrix = []
        for pxl in lpl:
            neighborMatrix.append(self.adjoining_pixel_indices(pxl))

        NeighborUnion = self.matrix_union(neighborMatrix)

        deadNeighborUnion = self.difference(NeighborUnion, lpl)

        for pxl in deadNeighborUnion:
            count = 0
            for row in neighborMatrix:  # could speed up by not continuing after count==4
                if pxl in row:
                    count += 1

            if count == 3:
                locations.append(pxl)

        return locations

    def swich_matrix(self):  # switches colors of appropriate entries, returns new live pixel list
        spl = []  # switch pixel list
        for pxl in self.livingPixelList:
            n = self.num_neighbors(pxl[0], pxl[1])

            if n > 3 or n < 2:
                spl.append(pxl)

        # list of dead pixel list to switch
        sdpl = self.births(self.livingPixelList)

        nlpl = self.difference(self.livingPixelList, spl)  # new live pxl list
        for pxl in spl:
            self.canvas.itemconfig(self.idMatrix[pxl[0]][pxl[1]], fill="white")

        nlpl.extend(sdpl)
        for pxl in sdpl:
            self.canvas.itemconfig(self.idMatrix[pxl[0]][pxl[1]], fill="black")

        return nlpl

    def event_flip(self, event):
        event_left = event.x < self.horizontal_margin
        event_right = event.x > self.horizontal_margin+self.grid_width
        event_above = event.y < self.verticle_margin
        event_below = event.y > self.verticle_margin+self.grid_height

        if event_left or event_right or event_above or event_below:
            # Clicking outside the grid starts the run
            self.end_startup = True
        elif not(self.end_startup):
            # Flip cell. Not allowed after starting.
            i = int((event.x-self.horizontal_margin)/self.cell_size)
            j = int((event.y-self.verticle_margin)/self.cell_size)
            if (i, j) not in self.currently_flipped_pixels:
                self.currently_flipped_pixels.add((i, j))
                if self.is_alive(i, j):
                    self.canvas.itemconfig(self.idMatrix[i][j], fill="white")
                else:
                    self.canvas.itemconfig(self.idMatrix[i][j], fill="black")
                    self.livingPixelList.append((i, j))

    def click(self, event):
        self.currently_flipped_pixels = set()

        self.event_flip(event)

    def drag(self, event):
        self.event_flip(event)

    def loop(self):
        if self.end_startup:
            self.livingPixelList = self.swich_matrix()

        self.root.after(1, self.loop)


if __name__ == '__main__':
    game = life(50, 50)
