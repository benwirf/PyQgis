layout = QgsProject.instance().layoutManager().layoutByName('Test Layout')

frame = [f for f in layout.items() if isinstance(f, QgsLayoutFrame)][0]

# Access the table item
tbl = frame.multiFrame()

# Retrieve the table contents (nested lists)
tbl_contents = tbl.tableContents()

# Define the column & row indexes for your target cell
# *mind that the indexing starts from zero
col_idx = 1
row_idx = 1

# Retrieve the cell content
cell_content = tbl_contents[row_idx][col_idx].content()

# Create a new cell with the same content
new_cell = QgsTableCell(cell_content)

# Create a new text format object with font & color of your choice
txt_format = QgsTextFormat()
txt_format.setFont(QFont('Times'))
txt_format.setSize(12)
txt_format.setColor(QColor(0, 255, 0))

# Set text format to new cell
new_cell.setTextFormat(txt_format)

# Place the new cell in the table contents matrix
tbl_contents[row_idx][col_idx] = new_cell

# Set the modified contents to the table
tbl.setTableContents(tbl_contents)

# Refresh the layout
layout.refresh()