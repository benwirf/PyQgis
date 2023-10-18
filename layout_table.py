layout = QgsProject.instance().layoutManager().layoutByName('Layout 2')

frame = [f for f in layout.items() if isinstance(f, QgsLayoutFrame)][0]

# Access the table item
tbl = frame.multiFrame()

tbl_contents = tbl.tableContents()
print(tbl_contents)

col = 1
row = 1

tbl_cell = tbl_contents[col][row]
tbl_cell.setBackgroundColor(QColor('yellow'))

print(tbl_cell.textFormat().color())

txt_format = tbl_cell.textFormat()

txt_format.setFont(QFont('Comic Sans', 10))
txt_format.setColor(QColor(0, 255, 0))

tbl_cell.setTextFormat(txt_format)

tbl.refresh()
frame.redraw()
layout.refresh()