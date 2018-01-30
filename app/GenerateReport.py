import pdfkit
from flask import render_template
import random

class GenerateReport:
    def __init__(self, save_location):
        self.loc = save_location

    def create_and_save_report(self, file_name, slide_info, annotations):
        name = file_name + str(random.randint(1, 1000000))
        print("Generating report for " + slide_info[0] + ", called " + name)
        pdfkit.from_string(render_template("report.html", slide_info=slide_info, annotations=annotations), self.loc + "/" + name)
        return self.loc + "/" + name