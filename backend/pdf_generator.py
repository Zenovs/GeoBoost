from jinja2 import Environment, FileSystemLoader
import weasyprint
import json
import os

class PDFGenerator:
    def __init__(self, template_dir='../templates'):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_pdf(self, data, output_path):
        template = self.env.get_template('report.html')
        html_content = template.render(data=data)
        
        # Generate PDF
        weasyprint.HTML(string=html_content).write_pdf(output_path)
        print(f"PDF generated: {output_path}")

# Example template in templates/report.html
# Would contain HTML with {{ data.traffic }}, etc.

if __name__ == "__main__":
    gen = PDFGenerator()
    data = {"title": "Test Report"}
    gen.generate_pdf(data, "test.pdf")