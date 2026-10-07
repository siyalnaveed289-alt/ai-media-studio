cat << 'EOF' > multi_category_book_maker.py
import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDZUhC7WUJnYbVJuoguXnEaMZNIGFHzf-M")

def generate_content(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error generating content from AI."
    except Exception as e:
        return f"Error: {e}"

def create_pdf(filename_prefix, title, content):
    filename = f"/sdcard/Download/{filename_prefix}_{title.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('BookTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=20)
    heading_style = ParagraphStyle('ChapterHeading', parent=styles['Heading2'], fontSize=15, textColor=colors.HexColor('#2C5282'), spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('BookBody', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#2D3748'), leading=16, spaceAfter=10)
    
    story.append(Paragraph(title.upper(), title_style))
    story.append(Spacer(1, 15))
    
    lines = content.split('\n')
    for line in lines:
        if not line.strip():
            continue
        if line.startswith('#') or (line.startswith('**') and len(line) < 60):
            story.append(Paragraph(line.replace('#', '').strip(), heading_style))
        else:
            story.append(Paragraph(line, body_style))
            
    # Box layout for facts and Islamic perspective
    box_data = [
        [Paragraph("<b>Scientific Fact / Research Note</b>", body_style), Paragraph("<b>Islamic Perspective (Quran / Hadith)</b>", body_style)],
        [Paragraph("Research indicates that structured intellectual and creative pursuits enhance cognitive function and mental well-being.", body_style), 
         Paragraph("‘And say: My Lord, increase me in knowledge.’ (Surah Taha: 114)", body_style)]
    ]
    
    t = Table(box_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Key Highlights & Notes</b>", heading_style))
    story.append(t)
    
    doc.build(story)
    print(f"\n[+] PDF successfully created and saved to Downloads: {filename}")

def main():
    while True:
        print("\n==========================================")
        print("    MULTI-CATEGORY CONTENT & PDF MAKER    ")
        print("==========================================")
        print("1. Novel / Story Writing")
        print("2. Complete Book")
        print("3. Article Writing")
        print("4. Essay Writing")
        print("5. Passage Generation")
        print("6. Exit")
        
        choice = input("\nSelect Category (1-6): ")
        
        if choice in ['1', '2', '3', '4', '5']:
            categories = {'1': 'Novel', '2': 'Book', '3': 'Article', '4': 'Essay', '5': 'Passage'}
            cat_name = categories[choice]
            
            title = input(f"Enter {cat_name} Title or Topic: ")
            
            print("\nChoose Language:")
            print("1. English")
            print("2. Urdu")
            lang_choice = input("Select Language (1-2): ")
            lang = "Urdu" if lang_choice == '2' else "English"
            
            print(f"\n[*] Generating {cat_name} in {lang}, please wait...")
            
            prompt = f"""
            Write a professional, comprehensive {cat_name} about '{title}' in {lang} language.
            Include structured headings, engaging details, and well-organized paragraphs.
            """
            
            content = generate_content(prompt)
            create_pdf(cat_name, title, content)
            
        elif choice == '6':
            print("Khuda Hafiz!")
            break
        else:
            print("Invalid choice, please select from 1 to 6.")

if __name__ == "__main__":
    main()
EOF
    
