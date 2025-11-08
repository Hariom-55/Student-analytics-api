import requests
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# configurations
API_URL = "http://127.0.0.1:5000/students"
REPORT_PDF = "Student_Analytics_Report.pdf"

#fetch data from API
print("📡 Fetching student data from API...")
response = requests.get(API_URL)

if response.status_code != 200:
    print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
    exit()

students = response.json()
df = pd.DataFrame(students)
print(f"✅ Loaded {len(df)} student records.")

# analysis and stats

# Basic stats
total_students = len(df)
avg_age = round(df['age'].mean(), 2)
male_count = len(df[df['gender'].str.lower() == 'male'])
female_count = len(df[df['gender'].str.lower() == 'female'])

# Course-wise count
course_counts = df['course'].value_counts()

# generate charts

# Course Distribution Bar Chart
plt.figure(figsize=(8, 5))
course_counts.plot(kind='bar', title="Students per Course")
plt.xlabel("Courses")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig("course_distribution.png")
plt.close()

#  Gender Distribution Pie Chart
plt.figure(figsize=(6, 6))
gender_counts = df['gender'].value_counts()
gender_counts.plot(kind='pie', autopct='%1.1f%%', title="Gender Distribution")
plt.ylabel("")
plt.tight_layout()
plt.savefig("gender_distribution.png")
plt.close()

# generate pdf report

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Student Analytics Report", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

pdf = PDF()
pdf.add_page()

# Title Section
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Overview", 0, 1)
pdf.set_font("Arial", "", 12)
pdf.multi_cell(0, 8, f"""
Total Students: {total_students}
Average Age: {avg_age}
Male Students: {male_count}
Female Students: {female_count}
""")

# Course distribution summary
pdf.ln(5)
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Course Distribution", 0, 1)
pdf.set_font("Arial", "", 11)

for course, count in course_counts.items():
    pdf.cell(0, 8, f"- {course}: {count} students", 0, 1)


pdf.ln(10)
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Visual Insights", 0, 1)

pdf.image("course_distribution.png", x=20, w=170)
pdf.ln(5)
pdf.image("gender_distribution.png", x=40, w=130)


pdf.output(REPORT_PDF)
print(f"✅ Report generated successfully: {REPORT_PDF}")