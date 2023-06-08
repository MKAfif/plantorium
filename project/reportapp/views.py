from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages


#Generate PDF report
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from shopper.models import *


def report_generator(request, orders):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, bottomup=0)
    c.setAuthor("Plantorium")
    c.setTitle("Sales report")

    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    max_orders_per_page = 4
    max_lines_per_page = 36
    order_count = 0
    line_count = 0
    lines = []

    order_count = orders.count()
    page_count = (order_count + max_orders_per_page - 1) // max_orders_per_page

    for page in range(page_count):
        lines.clear()

        start_index = page * max_orders_per_page
        end_index = start_index + max_orders_per_page
        page_orders = orders[start_index:end_index]

        for order in page_orders:
            lines.append("===========================Start===========================")
            lines.append("Order ID:"      + str(order.id))
            lines.append("Product ID:"    + str(order.product.id))
            lines.append("Product Name:"  + str(order.product. product_name))
            lines.append("Quantity:"      + str(order.quantity))
            lines.append("Amount:"        + str(order.amount))
            lines.append("Address:"       + str(order.address.address1))
            lines.append("Payment:"       + str(order.payment_type))
            lines.append("Date:"          + str(order.date))
            lines.append("Order Status:"  + str(order.status))
           

        for line in lines:
            line_count += 1
            textob.textLine(line)
            if line_count % max_lines_per_page == 0:
                c.drawText(textob)
                c.showPage()
                textob = c.beginText()
                textob.setTextOrigin(inch, inch)
                textob.setFont("Helvetica", 14)
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders report.pdf')


def report_pdf_order(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        return report_generator(request, orders)
    
    
import json

def chart_demo(request):
    orders = Order.objects.order_by('-id')[:5]
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(order.amount)
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }

    return render(request, 'chart_demo.html', context)


