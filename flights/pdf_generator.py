import io
import os
import qrcode
from django.conf import settings
from .models import Payment
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

NAVY = HexColor('#050c1e')
DARK_NAVY = HexColor('#0a1628')
CYAN = HexColor('#0ea5e9')
BLUE = HexColor('#4f46e5')
LIGHT_BLUE = HexColor('#818cf8')
ORANGE = HexColor('#f59e0b')
GRAY = HexColor('#94a3b8')
LIGHT_GRAY = HexColor('#e2e8f0')
WHITE = white
GREEN = HexColor('#10b981')

FLYEASE_LOGO = "✈ FlyEase"


def generate_qr_code(data_str, box_size=4):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#050c1e",
                        back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def _register_fonts():
    pass


class FlyEaseNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for (i, state) in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self._draw_page_footer(i + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_page_footer(self, page_num, total_pages):
        w, h = A4
        self.saveState()
        self.setStrokeColor(CYAN)
        self.setLineWidth(1.5)
        self.drawString(20 * mm, 11 * mm,
                        f"FlyEase E-Ticket — Page {page_num} of {total_pages}")
        self.drawRightString(w - 20 * mm, 11 * mm,
                              "© 2026 FlyEase Simulator — For demonstration purposes only")
        self.restoreState()


def build_eticket_pdf(booking, passengers_data, payment=None):
    _register_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=14 * mm,
        title=f"FlyEase E-Ticket - {booking.pnr}",
        subject=f"E-Ticket PNR {booking.pnr}",
        author="FlyEase",
        creator="FlyEase Flight Booking Simulator",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='FlyEaseTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        textColor=NAVY,
    ))
    styles.add(ParagraphStyle(
        name='FlyEaseTag',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=CYAN,
        spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name='SectionHead',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=NAVY,
        spaceBefore=4,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name='SmallMeta',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=GRAY,
    ))
    styles.add(ParagraphStyle(
        name='FieldValue',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=NAVY,
    ))
    styles.add(ParagraphStyle(
        name='SmallBody',
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=HexColor('#334155'),
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='ConfirmedBadge',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=GREEN,
    ))

    story = []

    # ============ HEADER WITH LOGO + QR + PNR ============
    pnr_val = booking.pnr
    ticket_val = booking.ticket_number or f"TK{booking.id:08d}"
    booking_date = booking.created_at.strftime("%d %b %Y · %H:%M") if booking.created_at else "—"

    # Public digital ticket verification URL encoded in QR Code
    # When scanned with any mobile camera, it opens the verified digital boarding pass
    qr_payload = f"http://127.0.0.1:8000/verify/{pnr_val}/"
    qr_buf = generate_qr_code(qr_payload, box_size=3)
    qr_img = Image(qr_buf, width=24 * mm, height=24 * mm)

    left_branding = [
        Paragraph("<b>FlyEase</b>", styles['FlyEaseTitle']),
        Paragraph("FLY SMARTER · BOOK BETTER", styles['FlyEaseTag']),
        Paragraph(f"E-Ticket Itinerary — Issued {booking_date}", styles['SmallMeta']),
    ]

    right_meta_data = [
        [Paragraph("<b>PNR:</b>", styles['SmallMeta']),
         Paragraph(f"<font color='#0284c7'><b>{pnr_val}</b></font>",
                   ParagraphStyle('pnr', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=CYAN))],
        [Paragraph("<b>Ticket #:</b>", styles['SmallMeta']),
         Paragraph(f"<b>{ticket_val}</b>", styles['FieldValue'])],
        [Paragraph("<b>Status:</b>", styles['SmallMeta']),
         Paragraph("<font color='#10b981'><b>CONFIRMED</b></font>", styles['ConfirmedBadge'])],
    ]
    right_meta_table = Table(right_meta_data, colWidths=[20 * mm, 46 * mm])
    right_meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    header_main_row = [
        [
            left_branding,
            qr_img,
            right_meta_table,
        ]
    ]
    header_table = Table(header_main_row, colWidths=[90 * mm, 28 * mm, 68 * mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 2 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN, spaceAfter=2 * mm, spaceBefore=1 * mm))

    # ============ FLIGHT DETAILS CARD ============
    story.append(Paragraph("Flight Itinerary", styles['SectionHead']))

    flight = booking.flight
    airline_name = flight.airline.name if flight.airline else "FlyEase"
    airline_code = flight.airline.code if flight.airline else "FE"
    dep_dt = flight.departure_time
    arr_dt = flight.arrival_time
    duration_min = int((arr_dt - dep_dt).total_seconds() // 60)
    duration_str = f"{duration_min // 60}h {duration_min % 60}m"

    orig = flight.origin
    dest = flight.destination

    flight_header = [
        [
            Paragraph(f"<font size='7.5' color='#64748b'>{orig.city}</font><br/><font size='18' color='#0284c7'><b>{orig.code}</b></font>",
                      ParagraphStyle('Org', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=NAVY)),
            Paragraph(
                f"<font size='9' color='#0284c7'><b>✈</b></font><br/>"
                f"<font size='7.5' color='#64748b'>{duration_str} · Non-stop</font>",
                ParagraphStyle('Mid', alignment=TA_CENTER, fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(f"<font size='7.5' color='#64748b'>{dest.city}</font><br/><font size='18' color='#0284c7'><b>{dest.code}</b></font>",
                      ParagraphStyle('Dst', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=NAVY,
                                     alignment=TA_RIGHT)),
        ]
    ]
    flight_header_tbl = Table(flight_header, colWidths=[62 * mm, 62 * mm, 62 * mm])
    flight_header_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f9ff')),
        ('BOX', (0, 0), (-1, -1), 0.6, CYAN),
    ]))
    story.append(flight_header_tbl)
    story.append(Spacer(1, 1.5 * mm))

    flight_info_rows = [
        [Paragraph("<b>Airline</b>", ParagraphStyle('L', fontName='Helvetica', fontSize=7.5, leading=9, textColor=GRAY)),
         Paragraph(airline_name, styles['FieldValue']),
         Paragraph("<b>Flight No.</b>", ParagraphStyle('L2', fontName='Helvetica', fontSize=7.5, leading=9, textColor=GRAY, alignment=TA_RIGHT)),
         Paragraph(f"{airline_code}-{flight.flight_number}", ParagraphStyle('V2', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=NAVY, alignment=TA_RIGHT)),
         ],
        [Paragraph("<b>Departs</b>", ParagraphStyle('L', fontName='Helvetica', fontSize=7.5, leading=9, textColor=GRAY)),
         Paragraph(f"{dep_dt.strftime('%d %b %Y · %H:%M')}",
                   ParagraphStyle('Dv', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=NAVY)),
         Paragraph("<b>Arrives</b>", ParagraphStyle('L2', fontName='Helvetica', fontSize=7.5, leading=9, textColor=GRAY, alignment=TA_RIGHT)),
         Paragraph(f"{arr_dt.strftime('%d %b %Y · %H:%M')}",
                   ParagraphStyle('Av', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=NAVY, alignment=TA_RIGHT)),
         ],
        [Paragraph("<b>Aircraft</b>", ParagraphStyle('L', fontName='Helvetica', fontSize=7.5, leading=9, textColor=GRAY)),
         Paragraph(flight.aircraft.model_name if flight.aircraft else "Airbus A320neo",
                   ParagraphStyle('Ac', fontName='Helvetica', fontSize=8.5, leading=11, textColor=NAVY)),
         Paragraph("<b>Cabin</b>", ParagraphStyle('L2', fontName='Helvetica', fontSize=7.5, leading=9, textColor=GRAY, alignment=TA_RIGHT)),
         Paragraph(booking.booking_passengers.first().seat.seat_class if (
             booking.booking_passengers.exists()
             and booking.booking_passengers.first().seat
         ) else "Economy",
                   ParagraphStyle('Cb', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=NAVY, alignment=TA_RIGHT)),
         ],
    ]
    fi_table = Table(flight_info_rows, colWidths=[25 * mm, 68 * mm, 25 * mm, 68 * mm])
    fi_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(fi_table)
    story.append(Spacer(1, 2 * mm))

    # ============ PASSENGERS & SEATS TABLE ============
    story.append(Paragraph(f"Passengers ({len(passengers_data)})", styles['SectionHead']))

    pax_header = [
        [Paragraph("<b>#</b>", ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=WHITE)),
         Paragraph("<b>Name</b>", ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=WHITE)),
         Paragraph("<b>Seat</b>", ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=WHITE)),
         Paragraph("<b>Class</b>", ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=WHITE)),
         Paragraph("<b>Document</b>", ParagraphStyle('ph', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=WHITE))],
    ]
    pax_rows = []
    for (i, p) in enumerate(passengers_data, 1):
        seat_num = p.get('seat', '—')
        p_class = p.get('seat_class', 'Economy')
        doc_str = p.get('passport_id') or p.get('govt_id') or (f"DOB: {p['dob']}" if p.get('dob') else "Verified")
        pax_rows.append([
            Paragraph(str(i), ParagraphStyle('pb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(f"<b>{p['first_name']} {p['last_name']}</b>", ParagraphStyle('pb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(f"<font color='#0284c7'><b>{seat_num}</b></font>", ParagraphStyle('pb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(p_class.replace('_', ' ').title(), ParagraphStyle('pb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(doc_str, ParagraphStyle('pb', fontName='Helvetica', fontSize=8, leading=10)),
        ])

    pax_table = Table(pax_header + pax_rows,
                      colWidths=[10 * mm, 62 * mm, 22 * mm, 34 * mm, 58 * mm], repeatRows=1)
    pax_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.4, LIGHT_GRAY),
        ('BOX', (0, 0), (-1, -1), 0.5, NAVY),
    ]))
    story.append(pax_table)
    story.append(Spacer(1, 2.5 * mm))

    # ============ FARE BREAKDOWN ============
    story.append(Paragraph("Fare Breakdown & Payment", styles['SectionHead']))

    price_per_pax = float(booking.price_paid or 0) / max(1, len(passengers_data))
    base_fare = round(price_per_pax * 0.79, 2)
    taxes = round(float(booking.price_paid or 0) - (base_fare * len(passengers_data)), 2)
    discount = float(booking.discount_amount or 0)
    offer_label = None

    if booking.deal_title:
        offer_label = f"Offer: {booking.deal_title}"
    elif booking.coupon:
        offer_label = f"Promo Code ({booking.coupon.code})"

    fare_rows = [
        [Paragraph("<b>Description</b>", ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=NAVY)),
         Paragraph("<b>Qty</b>", ParagraphStyle('fhc', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=NAVY, alignment=TA_CENTER)),
         Paragraph("<b>Unit (INR)</b>", ParagraphStyle('fhr', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=NAVY, alignment=TA_RIGHT)),
         Paragraph("<b>Amount (INR)</b>", ParagraphStyle('fhr', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=NAVY, alignment=TA_RIGHT))],
        [Paragraph("Base Fare & Dynamic Pricing", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
         Paragraph(str(len(passengers_data)), ParagraphStyle('fbc', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_CENTER)),
         Paragraph(f"{base_fare:,.2f}", ParagraphStyle('fbr', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT)),
         Paragraph(f"{base_fare * len(passengers_data):,.2f}", ParagraphStyle('fbr', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT))],
        [Paragraph("Taxes & Surcharges (18% GST)", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
         Paragraph("", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
         Paragraph("", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
         Paragraph(f"{taxes:,.2f}", ParagraphStyle('fbr', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT))],
    ]
    if getattr(booking, 'has_insurance', False):
        fare_rows.append([
            Paragraph("Travel Protection & Delay Insurance", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(str(len(passengers_data)), ParagraphStyle('fbc', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_CENTER)),
            Paragraph(f"{float(booking.insurance_fee or 499):,.2f}", ParagraphStyle('fbr', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT)),
            Paragraph(f"{float(booking.insurance_fee or 499):,.2f}", ParagraphStyle('fbr', fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT))
        ])

    if discount > 0 and offer_label:
        fare_rows.append([
            Paragraph(offer_label, ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph("", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph("", ParagraphStyle('fb', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(f"-{discount:,.2f}", ParagraphStyle('fbr', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=GREEN, alignment=TA_RIGHT))
        ])

    total_paid_str = f"INR {float(booking.price_paid or 0):,.2f}"
    fare_rows.append([
        Paragraph("<b>TOTAL PAID</b>", ParagraphStyle('tot', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=NAVY)),
        Paragraph("", ParagraphStyle('tot', fontName='Helvetica', fontSize=9, leading=11)),
        Paragraph("", ParagraphStyle('tot', fontName='Helvetica', fontSize=9, leading=11)),
        Paragraph(f"<b>{total_paid_str}</b>", ParagraphStyle('totr', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=BLUE, alignment=TA_RIGHT)),
    ])

    fare_table = Table(fare_rows, colWidths=[92 * mm, 18 * mm, 38 * mm, 38 * mm])
    fare_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f9ff')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f0f9ff')),
        ('GRID', (0, 0), (-1, -2), 0.4, LIGHT_GRAY),
        ('LINEABOVE', (0, -1), (-1, -1), 0.8, CYAN),
        ('BOX', (0, 0), (-1, -1), 0.5, NAVY),
    ]))
    story.append(fare_table)
    story.append(Spacer(1, 2 * mm))

    # Payment method summary
    if payment:
        method_label = dict(Payment.METHOD_CHOICES).get(payment.method, payment.method)
        pm_row = [[
            Paragraph(f"<b>Payment Method:</b> <font color='#64748b'>{method_label} · Status: {payment.status}</font>",
                      ParagraphStyle('p1', fontName='Helvetica', fontSize=7.5, leading=10, textColor=NAVY)),
            Paragraph(f"<b>Transaction ID:</b> <font color='#64748b'>{payment.transaction_id or 'N/A'}</font>",
                      ParagraphStyle('p2', fontName='Helvetica', fontSize=7.5, leading=10, textColor=NAVY,
                                     alignment=TA_RIGHT)),
        ]]
        pm_table = Table(pm_row, colWidths=[93 * mm, 93 * mm])
        pm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 0.4, LIGHT_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(pm_table)
    story.append(Spacer(1, 2.5 * mm))

    # ============ BOARDING PASS PREVIEW (per pax, compact) ============
    story.append(Paragraph("Boarding Pass Preview", styles['SectionHead']))
    boarding_blocks = []
    for (i, p) in enumerate(passengers_data, 1):
        seat = p.get('seat', '—')
        bp_inner = [
            [Paragraph(f"<font size='7' color='#64748b'>{orig.city}</font><br/><font size='14' color='#0284c7'><b>{orig.code}</b></font>",
                       ParagraphStyle(f'bo{i}', fontName='Helvetica-Bold', fontSize=8, leading=11)),
             Paragraph("<font size='12' color='#0284c7'><b>✈</b></font>",
                       ParagraphStyle(f'pm{i}', fontName='Helvetica', fontSize=12, leading=14,
                                      textColor=BLUE, alignment=TA_CENTER)),
             Paragraph(f"<font size='7' color='#64748b'>{dest.city}</font><br/><font size='14' color='#0284c7'><b>{dest.code}</b></font>",
                       ParagraphStyle(f'de{i}', fontName='Helvetica-Bold', fontSize=8, leading=11,
                                      alignment=TA_RIGHT)),
             Paragraph(f"<font size='7' color='#64748b'>SEAT</font><br/><font size='14' color='#d97706'><b>{seat}</b></font>",
                       ParagraphStyle(f'se{i}', fontName='Helvetica-Bold', fontSize=8, leading=11,
                                      textColor=ORANGE, alignment=TA_RIGHT)),
            ]
        ]
        bp_row1_tbl = Table(bp_inner, colWidths=[42 * mm, 42 * mm, 42 * mm, 42 * mm])
        bp_row1_tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        bp_info = [
            [Paragraph(f"<b>Passenger:</b> {p['first_name']} {p['last_name']}",
                       ParagraphStyle(f'px{i}', fontName='Helvetica', fontSize=7.5, leading=9)),
             Paragraph(f"<b>Flight:</b> {airline_code}-{flight.flight_number}",
                       ParagraphStyle(f'fx{i}', fontName='Helvetica', fontSize=7.5, leading=9, alignment=TA_CENTER)),
             Paragraph(f"<b>Departs:</b> {dep_dt.strftime('%d %b %H:%M')}",
                       ParagraphStyle(f'dx{i}', fontName='Helvetica', fontSize=7.5, leading=9,
                                      alignment=TA_RIGHT)),
            ]
        ]
        bp_info_tbl = Table(bp_info, colWidths=[66 * mm, 50 * mm, 52 * mm])
        bp_info_tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        bp_full_rows = [
            [bp_row1_tbl],
            [bp_info_tbl]
        ]
        boarding_wrap = Table(bp_full_rows, colWidths=[186 * mm])
        boarding_wrap.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), white),
            ('BOX', (0, 0), (-1, -1), 0.5, CYAN),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        boarding_blocks.append(boarding_wrap)
        boarding_blocks.append(Spacer(1, 1.5 * mm))
    for b in boarding_blocks:
        story.append(b)
    story.append(Spacer(1, 2 * mm))

    # ============ TERMS & TRAVEL INFO ============
    story.append(Paragraph("Important Travel Information", styles['SectionHead']))

    terms = [
        "<b>Check-in:</b> Online check-in opens 24h prior and closes 60m before departure. Valid govt photo ID required for all passengers.",
        "<b>Baggage Allowance:</b> Economy: 1 hand baggage (max 7kg) + 1 personal item. Check-in luggage rules apply per airline fare rules.",
        "<b>Cancellations & Changes:</b> Eligible for refund according to airline fare conditions if cancelled > 24h before scheduled departure.",
        "<b>Security Screening:</b> All passengers & luggage subject to mandatory airport security. Arrive 2-3 hours prior to departure.",
    ]
    for t in terms:
        story.append(Paragraph(f"• {t}", styles['SmallBody']))
        story.append(Spacer(1, 0.8 * mm))

    story.append(Spacer(1, 2.5 * mm))
    story.append(HRFlowable(width="60%", thickness=0.6, color=GRAY, spaceAfter=2 * mm))
    story.append(Paragraph(
        "<b>FlyEase</b> — <i>Fly Smarter. Book Better.</i><br/>"
        "<font size='6.5' color='#94a3b8'>Computer-generated e-ticket from FlyEase Simulator. For simulation & demonstration purposes only.</font>",
        ParagraphStyle('footer-msg', alignment=TA_CENTER, fontName='Helvetica', fontSize=7.5,
                       leading=9.5, textColor=NAVY),
    ))

    doc.build(story, canvasmaker=FlyEaseNumberedCanvas)
    buffer.seek(0)
    return buffer
