import tkinter


def idToBool(Id):
    return canvas.itemcget(Id, "fill") == "black"


def neighbors(x, y, M):
    tot = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if not(j == 0 and i == 0):
                tot += idToBool(M[(x+i) % len(M)][(y+j) % len(M[0])])

    return tot


def allNeighbors(pxl, lenM, lenM0):  # list of all neighbors in format [(x,y)]
    allN = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if not(j == 0 and i == 0):
                allN.append(((pxl[0]+i) % lenM, (pxl[1]+j) % lenM0))

    return allN


def union(a, b):
    return list(set(a) | set(b))


def matrixUnion(M):
    U = []
    for i in M:
        U = union(U, i)

    return U


def difference(a, b):
    return list(set(a) - set(b))


def deadPixelsWith3Neighbors(lpl, lenM, lenM0):
    dpw3n = []

    neighborMatrix = []
    for pxl in lpl:
        neighborMatrix.append(allNeighbors(pxl, lenM, lenM0))

    NeighborUnion = matrixUnion(neighborMatrix)

    deadNeighborUnion = difference(NeighborUnion, lpl)

    for pxl in deadNeighborUnion:
        count = 0
        for row in neighborMatrix:  # could speed up by not continuing after count==4
            if pxl in row:
                count += 1

        if count == 3:
            dpw3n.append(pxl)

    return dpw3n


def swichMatrix(lpl, M):  # switches colors of appropriate entries, returns new live pixel list
    spl = []  # switch pixel list
    for pxl in lpl:
        n = neighbors(pxl[0], pxl[1], M)

        if n > 3 or n < 2:
            spl.append(pxl)

    # list of dead pixel list to switch
    sdpl = deadPixelsWith3Neighbors(lpl, len(M), len(M[0]))

    nlpl = difference(lpl, spl)  # new live pxl list
    for pxl in spl:
        canvas.itemconfig(M[pxl[0]][pxl[1]], fill="white")

    nlpl.extend(sdpl)
    for pxl in sdpl:
        canvas.itemconfig(M[pxl[0]][pxl[1]], fill="black")

    return nlpl


def callback(event):
    global startW
    global dW
    global deltaW
    global startH
    global dH
    global deltaH
    global end_startup
    if event.x < startW or event.x > startW+dW or event.y < startH or event.y > startH+dH:
        end_startup = True
    elif not(end_startup):
        i = int((event.x-startW)/deltaW)
        j = int((event.y-startH)/deltaH)
        if idToBool(idMatrix[i][j]):
            canvas.itemconfig(idMatrix[i][j], fill="white")
        else:
            canvas.itemconfig(idMatrix[i][j], fill="black")
            livingPixelList.append((i, j))


ch = 500
cw = 500

root = tkinter.Tk()
canvas = tkinter.Canvas(root, bg="white", height=ch, width=cw)
canvas.bind("<Button-1>", callback)
canvas.pack()

startH = 15
dH = ch-2*startH
endH = startH+dH

startW = 50
dW = cw-2*startW
endW = startW+dW

deltaH = 10
deltaW = 10

numH = int(dH/deltaH)
numW = int(dW/deltaW)

# create the horizontal lines
for i in range(numH+1):
    canvas.create_line(startW, startH+i*10, endW, startH+i*10)

# create the vertical lines
for i in range(numW+1):
    canvas.create_line(startW+i*10, startH, startW+i*10, endH)


idMatrix = []
simpleM = []
# width
for i in range(numW):
    c = []
    sc = []
    # height
    for j in range(numH):
        sy = startW+i*deltaW
        sx = startH+j*deltaH
        Id = canvas.create_rectangle(
            sy, sx, sy+deltaW, sx+deltaH, fill="white")

        c.append(Id)
        sc.append(0)

    idMatrix.append(c)
    simpleM.append(sc)

end_startup = False
#global end_startup
canvas.itemconfig(idMatrix[2][1], fill="black")
canvas.itemconfig(idMatrix[3][2], fill="black")
canvas.itemconfig(idMatrix[3][3], fill="black")
canvas.itemconfig(idMatrix[2][3], fill="black")
canvas.itemconfig(idMatrix[1][3], fill="black")
livingPixelList = [(2, 1), (3, 2), (3, 3), (2, 3), (1, 3)]


def loop():
    global livingPixelList
    global end_startup
    if end_startup:
        livingPixelList = swichMatrix(livingPixelList, idMatrix)

    root.after(1, loop)


root.after(1, loop)
root.mainloop()
