import os
import markdown
from fpdf import FPDF

class PDFGenerator(FPDF):
    def __init__(self, font_path=None, bold_font_path=None):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
        # 기본 폰트 설정 (맑은 고딕 사용 - 한글 및 마크다운 스타일 대응)
        reg_path = "C:\\Windows\\Fonts\\malgun.ttf"
        bold_path = "C:\\Windows\\Fonts\\malgunbd.ttf"
        
        if os.path.exists(reg_path):
            self.add_font("Malgun", "", reg_path)
            if os.path.exists(bold_path):
                self.add_font("Malgun", "B", bold_path)
            self.set_font("Malgun", size=11)
        else:
            # 윈도우가 아닌 경우 등 대비
            self.set_font("Arial", size=11)

    def write_markdown(self, md_text):
        # 마크다운을 HTML로 변환
        # fpdf2의 write_html은 기본적인 HTML 태그(<b>, <i>, <h1> 등)를 지원합니다.
        html = markdown.markdown(md_text)
        
        # 한글 폰트가 적용된 상태에서 HTML 렌더링
        # <h1>~<h3> 등을 Malgun 폰트로 매핑하기 위해 스타일 지정 가능
        self.write_html(html)

def create_stock_pdf(report_content, ticker, date):
    pdf = PDFGenerator()
    
    # 제목 추가 (직접 추가하거나 마크다운에 포함)
    pdf.set_font("Malgun", "B", 20)
    pdf.cell(0, 15, f"{ticker} Analysis Report", ln=True, align="C")
    pdf.set_font("Malgun", "", 10)
    pdf.cell(0, 10, f"Date: {date}", ln=True, align="R")
    pdf.ln(5)
    
    # 본문 마크다운 렌더링
    pdf.write_markdown(report_content)
    
    filename = f"{ticker}_Analysis_{date}.pdf".replace("-", "")
    pdf.output(filename)
    return filename
