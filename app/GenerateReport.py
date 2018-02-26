import pdfkit
from flask import render_template
import random
from bs4 import BeautifulSoup

class GenerateReport:
    def __init__(self, save_location):
        self.loc = save_location

    def create_and_save_report(self, file_name, slide_info, annotations):
        name = file_name + str(random.randint(1, 1000000)) + ".pdf"
        #print("Generating report for " + slide_info[0] + ", called " + name)
        print(len(annotations))
        report_render = render_template("report.html", slide_info=slide_info, annotations=annotations)
        soup = BeautifulSoup(report_render, 'html.parser')
        #print(soup.prettify())
        options = {
            'no-outline': None
        }
        pdfkit.from_string(report_render, self.loc + "/" + name, options=options)
        return name