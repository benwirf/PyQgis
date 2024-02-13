class MyButtonStyle(QProxyStyle):
    def __init__(self):
        QProxyStyle.__init__(self)
        
    def styleHint(self, hint, option=None, widget=None, return_data=None):
        if hint == QStyle.SH_ToolButton_PopupDelay:
            return 3000
        return QProxyStyle.styleHint(self, hint, option, widget, return_data)

btn = QgsSymbolButton()
#menu = btn.findChild(QMenu)
#print(menu)
btn.setPopupMode(QToolButton.DelayedPopup)
btn.setStyle(MyButtonStyle())
btn.show()
        