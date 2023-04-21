import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from reportlab.lib.enums import TA_CENTER

# Create your views here.
from .models import MilkEvaluation, Sacco, Milk


def index(request):
    if request.user.is_authenticated:
        return redirect(to='home')
    return render(request, 'mFarm/index.html')


@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(to='/admin')
        evaluation = MilkEvaluation.objects.all().filter(the_milk__farmer=request.user)
        context = {'milk_evaluation': evaluation, 'currentYear': datetime.now().year}
        return render(request=request, template_name='mFarm/home.html', context=context)
    return redirect(to='login')


def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(to='/admin')
        redirect(to='home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect(to='/admin')
            return redirect(to='home')
        else:
            messages.info(request, 'Email or password is incorrect')
    context = {'messages': messages, 'currentYear': datetime.now().year}
    return render(request=request, template_name='mFarm/login.html', context=context)


def logout_view(request):
    logout(request)
    return redirect(to='index')


def signup(request):
    saccos = Sacco.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')

        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        pattern = "^0(7(?:(?:[129][0-9])|(?:0[0-8])|(4[0-1]))[0-9]{6})$"
        if not re.match(pattern, request.POST.get('phone')):
            messages.add_message(request, messages.ERROR, 'Phone number is not valid')
            return redirect(to='signup')
        phone = request.POST.get('phone')

        if request.POST.get('sacco') == 'Select Sacco':
            messages.add_message(request, messages.ERROR, 'Please select a Sacco')
            return redirect(to='signup')
        saccoId = request.POST.get('sacco')
        if saccoId is None:
            messages.add_message(request, messages.ERROR, 'Please select a Sacco')
            return redirect(to='signup')

        sacco = Sacco.objects.get(id=saccoId)
        address = sacco.location

        try:
            if password2 != password1:
                messages.error(request, 'Passwords do not match')
                return redirect(to='signup')
            user = get_user_model().objects.create_user(name=name, phone=phone, email=email, address=address,
                                                        sacco=sacco, password=password1)
            user.save()

            messages.add_message(request, messages.INFO, 'Account created successfully')
            login(request, user)
            return redirect(to='home')
        except Exception as e:
            print(e)
            messages.add_message(request, messages.ERROR, e)
            return redirect(to='signup')
    else:
        context = {'saccos': saccos, 'messages': messages.get_messages(request)}
    return render(request, 'mFarm/signUp.html', context)


#
# from io import BytesIO
# from datetime import datetime
# from django.http import HttpResponse
# from reportlab.pdfgen import canvas
#
#
# def generate_receipt(request, milk_id):
#     # Get the milk object
#     milk = Milk.objects.get(pk=milk_id)
#
#     # Create the PDF object
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer)
#
#     # Set the PDF metadata
#     pdf.setAuthor('Your Name')
#     pdf.setTitle('Milk Receipt')
#
#     # Add content to the PDF
#     pdf.drawString(100, 750, 'Milk Receipt')
#     pdf.drawString(100, 700, 'Date: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
#     pdf.drawString(100, 650, 'Name: {}'.format(milk.farmer.name))
#     pdf.drawString(100, 600, 'Address: {}'.format(milk.farmer.address))
#     pdf.drawString(100, 550, 'Phone: {}'.format(milk.farmer.phone))
#     pdf.drawString(100, 500, 'Email: {}'.format(milk.farmer.email))
#     pdf.drawString(100, 450, 'Quantity: {} litres'.format(milk.quantity))
#     pdf.drawString(100, 400, 'Status: {}'.format(milk.status.status))
#     pdf.drawString(100, 350, 'Butter Fat: {}'.format(MilkEvaluation.objects.get(the_milk=milk).butter_fat))
#     pdf.drawString(100, 300, 'Protein Content: {}'.format(MilkEvaluation.objects.get(the_milk=milk).protein_content))
#     pdf.drawString(100, 250,
#                    'Total Amount: KES {}'.format(MilkEvaluation.objects.get(the_milk=milk).calculate_base_amount()))
#
#     # Close the PDF object cleanly, and we're done.
#     pdf.showPage()
#     pdf.save()
#
#     # File response with the PDF content.
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="milk_receipt.pdf"'
#     return response


# from io import BytesIO
# from datetime import datetime
# from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
#
#
# def generate_receipt(request, milk_id):
#     # Get the milk object
#     milk = Milk.objects.get(pk=milk_id)
#
#     # Create the PDF object
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)
#
#     # Set the PDF metadata
#     pdf.setAuthor('MFarm')
#     pdf.setTitle(milk.farmer.name+"'s Milk  Payment Receipt "+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#
#     # Add content to the PDF
#     pdf.setFontSize(16)
#     pdf.drawCentredString(letter[0] / 2, 750, milk.farmer.name+"'s Milk Receipt")
#
#     pdf.setFontSize(12)
#     pdf.drawString(inch, 700, 'Date: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
#     pdf.drawString(inch, 650, 'Name: {}'.format(milk.farmer.name))
#     pdf.drawString(inch, 625, 'Address: {}'.format(milk.farmer.address))
#     pdf.drawString(inch, 600, 'Phone: {}'.format(milk.farmer.phone))
#     pdf.drawString(inch, 575, 'Email: {}'.format(milk.farmer.email))
#
#     pdf.line(inch, 550, letter[0] - inch, 550)
#     pdf.setFontSize(14)
#     pdf.drawString(inch, 530, 'Milk Details')
#     pdf.setFontSize(12)
#     pdf.drawString(inch, 500, 'Quantity: {} litres'.format(milk.quantity))
#     pdf.drawString(inch, 475, 'Status: {}'.format(milk.status.status))
#
#     pdf.line(inch, 450, letter[0] - inch, 450)
#     pdf.setFontSize(14)
#     pdf.drawString(inch, 430, 'Milk Evaluation')
#     pdf.setFontSize(12)
#     pdf.drawString(inch, 400, 'Butter Fat Content: {}'.format(MilkEvaluation.objects.get(the_milk=milk).butter_fat))
#     pdf.drawString(inch, 375, 'Protein Content: {}'.format(MilkEvaluation.objects.get(the_milk=milk).protein_content))
#     pdf.line(inch, 370, letter[0] - inch, 370)
#     pdf.line(inch, 348, letter[0] - inch, 348)
#     pdf.drawString(inch, 348, 'Total Amount: KES {}'.format(MilkEvaluation.objects.get(the_milk=milk).calculate_base_amount()))
#
#     # Close the PDF object cleanly, and we're done.
#     pdf.showPage()
#     pdf.save()
#
#     # File response with the PDF content.
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="'+milk.farmer.name+"'s Milk  Payment Receipt "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.pdf"'
#     return response
#


# from io import BytesIO
# from datetime import datetime
# from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
#
#
# def generate_receipt(request, milk_id):
#     # Get the milk object
#     milk = Milk.objects.get(pk=milk_id)
#
#     # Create the PDF object
#     buffer = BytesIO()
#     pdf = canvas.Canvas(buffer)
#
#     # Set the PDF metadata
#     pdf.setAuthor('Your Name')
#     pdf.setTitle('Milk Receipt')
#
#     # Define the table style
#     table_style = [
#         ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
#         ('BACKGROUND', (0, 0), (-1, 0), '#007bff'),
#         ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
#         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#         ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
#         ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
#         ('GRID', (0, 0), (-1, -1), 0.5, 'BLACK'),
#     ]
#
#     # Add content to the PDF
#     pdf.drawString(100, 750, 'Milk Receipt')
#     pdf.drawString(100, 700, 'Date: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
#
#     # Create the table
#     data = [
#         ['Name', milk.farmer.name],
#         ['Address', milk.farmer.address],
#         ['Phone', str(milk.farmer.phone)],
#         ['Email', milk.farmer.email],
#         ['Quantity', str(milk.quantity) + ' litres'],
#         ['Status', milk.status.status],
#         ['Butter Fat', str(MilkEvaluation.objects.get(the_milk=milk).butter_fat)],
#         ['Protein Content', str(MilkEvaluation.objects.get(the_milk=milk).protein_content)],
#         ['Total Amount', 'KES ' + str(MilkEvaluation.objects.get(the_milk=milk).calculate_base_amount())],
#     ]
#
#     table = Table(data, colWidths=[1.5 * inch, 4 * inch])
#     table.setStyle(TableStyle(table_style))
#     table.wrapOn(pdf, 0, 0)
#     table.drawOn(pdf, 100, 500)
#
#     # Close the PDF object cleanly, and we're done.
#     pdf.showPage()
#     pdf.save()
#
#     # File response with the PDF content.
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="milk_receipt.pdf"'
#     return response


from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_receipt(request, milk_id):
    # Get the milk object
    milk = Milk.objects.get(pk=milk_id)

    # Get the milk evaluation object
    milk_evaluation = MilkEvaluation.objects.get(the_milk=milk)

    # Create the PDF object
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    # Define the style sheet
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

    # Define the data for the table
    data = [["Milk Payment receipt   for " + milk.farmer.name],
            ['Farmer Name:', milk.farmer.name],
            ['Address:', milk.farmer.address],
            ['Phone:', str(milk.farmer.phone)],
            ['Email:', milk.farmer.email],
            ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Quantity:', str(milk.quantity) + ' litres'],
            ['Status:', milk.status.status],
            ['Butter Fat Content:', str(milk_evaluation.butter_fat) + "%"],
            ['Protein Content:', str(milk_evaluation.protein_content) + "%"],
            ['Total Amount:', 'KES ' + str(milk_evaluation.calculate_base_amount())]]

    # Create the table and add the data
    table = Table(data, colWidths=[2 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f2f2f2')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.red),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
    ]))

    # Add the table to the document and close it
    doc.build([table])

    # File response with the PDF content.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response[
        'Content-Disposition'] = 'attachment; filename="' + milk.farmer.name + "'s Milk  Payment Receipt " + datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S') + '.pdf"'
    return response
