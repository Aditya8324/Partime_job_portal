from fpdf import FPDF


LEVEL_LABELS = {
    "masters": "Masters",
    "bachelors": "Bachelors",
    "twelfth": "Class 12th",
    "tenth": "Class 10th",
}


def generate_resume_pdf(user) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header — Name
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, user.full_name or "", ln=True, align="C")

    # Contact line — email | phone
    pdf.set_font("Helvetica", "", 11)
    contact = f"{user.email or ''}  |  {user.phone}"
    pdf.cell(0, 8, contact, ln=True, align="C")
    pdf.ln(4)

    # Divider
    pdf.set_draw_color(120, 120, 120)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    _section(pdf, "Summary", user.summary or "")
    _section(pdf, "Skills", user.skills or "")
    _section(pdf, "Experience", user.experience or "")
    _education_section(pdf, user.education)

    return bytes(pdf.output())


def _section(pdf: FPDF, title: str, body: str):
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, title, ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, body or "")
    pdf.ln(3)


def _education_section(pdf: FPDF, education):
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Education", ln=True)

    if not education:
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, "")
        pdf.ln(3)
        return

    for level_key, label in LEVEL_LABELS.items():
        entry = education.get(level_key)
        if not entry:
            continue

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, label, ln=True)

        pdf.set_font("Helvetica", "", 11)
        for line in _format_entry(entry):
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, line)
        pdf.ln(2)


def _format_entry(entry: dict) -> list[str]:
    lines = []

    line1_parts = [entry.get("degree"), entry.get("specialization")]
    line1 = " - ".join(p for p in line1_parts if p)
    if line1:
        lines.append(line1)

    line2_parts = [entry.get("institute"), entry.get("board_or_university")]
    line2 = ", ".join(p for p in line2_parts if p)
    if line2:
        lines.append(line2)

    if entry.get("year"):
        lines.append(f"Year: {entry['year']}")

    return lines
