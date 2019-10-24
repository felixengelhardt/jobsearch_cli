import PyQt5.QtGui
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QHBoxLayout, QWidget, QSplitter, QPushButton, \
    QLineEdit, QGridLayout, QLabel, QCheckBox

import jobsearch


class Gui:
    def __init__(self, app):
        self.app = app
        widget = QWidget()
        grid = QGridLayout()
        layout = QHBoxLayout()
        splitter = QSplitter()

        self.jobs = jobsearch.jobSearch()
        queries_dict = self.jobs.create_queries()

        self.list_widget = QListWidget()
        self.web = QWebEngineView()

        job_title_label = QLabel()
        job_title_label.setText("Job title:")
        location_label = QLabel()
        location_label.setText("Location:")
        radius_label = QLabel()
        radius_label.setText("Radius:")

        button = QPushButton()
        button.setText("Search")
        button.clicked.connect(self.on_button_click)

        self.line_edit_jobtitle = QLineEdit()
        self.line_edit_jobtitle.setText(self.jobs.search_queries_default['jobtitle'])
        self.line_edit_location = QLineEdit()
        self.line_edit_location.setText(self.jobs.search_queries_default['location'])
        self.line_edit_radius = QLineEdit()
        self.line_edit_radius.setText(self.jobs.search_queries_default['radius'])

        header_layout_1 = QHBoxLayout()
        header_layout_1.addWidget(button)
        header_layout_1.addWidget(job_title_label)
        header_layout_1.addWidget(self.line_edit_jobtitle)
        header_layout_1.addWidget(location_label)
        header_layout_1.addWidget(self.line_edit_location)
        header_layout_1.addWidget(radius_label)
        header_layout_1.addWidget(self.line_edit_radius)
        grid.addLayout(header_layout_1, 0, 0)

        self.checkbox_monster = QCheckBox("Monster")
        self.checkbox_indeed = QCheckBox("Indeed")
        self.checkbox_stepstone = QCheckBox("Stepstone")

        header_layout_2 = QHBoxLayout()
        header_layout_2.addWidget(self.checkbox_monster)
        header_layout_2.addWidget(self.checkbox_indeed)
        header_layout_2.addWidget(self.checkbox_stepstone)
        grid.addLayout(header_layout_2, 1, 0)

        self.my_font = PyQt5.QtGui.QFont()
        self.my_font.setBold(True)
        self.my_font.setFamily("Arial")
        self.my_font.setPointSize(10)

        for engine in queries_dict:
            page = self.jobs.request_page(queries_dict[engine])
            results = self.jobs.parse_page(page, engine)
            for result in results:
                item = QListWidgetItem()
                item.setFont(self.my_font)
                item.setText('{}\n\t({})'.format(result[0], result[1]))
                item.setData(32, result[2])
                self.list_widget.addItem(item)

        self.web.load(QUrl(self.list_widget.item(0).data(32)))

        self.list_widget.itemActivated.connect(self.load_website_for_list_item)
        self.list_widget.itemClicked.connect(self.load_website_for_list_item)
        self.list_widget.setCurrentItem(self.list_widget.item(0))

        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.web)

        layout.addWidget(splitter)
        grid.addLayout(layout, 2, 0)
        widget.setLayout(grid)
        widget.show()

        self.app.exec_()

    def load_website_for_list_item(self, item):
        self.web.load(QUrl(item.data(32)))

    def on_button_click(self):
        self.list_widget.clear()
        jobtitle = self.line_edit_jobtitle.text().replace(" ", "%20")
        location = self.line_edit_location.text().replace(" ", "%20")
        radius = self.line_edit_radius.text().replace(" ", "%20")
        self.jobs.search_queries_default['jobtitle'] = jobtitle
        self.jobs.search_queries_default['location'] = location
        self.jobs.search_queries_default['radius'] = radius
        queries_dict = self.jobs.create_queries()
        for engine in queries_dict:
            page = self.jobs.request_page(queries_dict[engine])
            results = self.jobs.parse_page(page, engine)
            for result in results:
                item = QListWidgetItem()
                item.setFont(self.my_font)
                item.setText('{}\n\t({})'.format(result[0], result[1]))
                item.setData(32, result[2])
                self.list_widget.addItem(item)
        self.web.load(QUrl(self.list_widget.item(0).data(32)))



def main():
    app = QApplication([])
    app.setApplicationName("JobSearch QtGui")
    Gui(app)


if __name__ == "__main__":
    main()
