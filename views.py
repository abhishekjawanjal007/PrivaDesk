from pyexpat.errors import messages
from tokenize import Comment
from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .utils import generate_verification_code
from .models import ChatMessage,IncidentReport
from .models import Comment,ChatMessage
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.core.mail import send_mail

def HomePage(request):
    return render(request,'home.html')

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def SignupPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Check if a user with the provided email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('signup')  # Redirect back to the signup page

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
        else:
            # Use email as the username
            my_user = User.objects.create_user(username=email, email=email, password=pass1)
            my_user.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
        
    return render(request, 'signup.html')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse

def LoginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Email or password is incorrect.")
    return render(request, 'login.html')


@login_required
def createTicket(request):
    if request.method == 'POST':
        issue_type = request.POST.get('issueType')
        location = request.POST.get('location')
        description = request.POST.get('description')
        witnesses = request.POST.getlist('witness')
        evidence = request.FILES.get('evidence')
        created_anonymously = request.POST.get('created_anonymously')

        if created_anonymously == 'on':
            # Create the IncidentReport object anonymously
            incident_report = IncidentReport.objects.create(
                issue_type=issue_type,
                date_time=timezone.now(),
                location=location,
                description=description,
                witness=witnesses,
                evidence=evidence,
                created_anonymously=True
            )
        else:
            # Create the IncidentReport object for logged-in users
            incident_report = IncidentReport.objects.create(
                user=request.user,
                issue_type=issue_type,
                date_time=timezone.now(),
                location=location,
                description=description,
                witness=witnesses,
                evidence=evidence
            )
        # Send email notification to the user
        if not created_anonymously and request.user.email:
            send_mail(
                subject='Ticket Created Successfully',
                message=f'Your ticket with ID {incident_report.id} has been created successfully.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Ticket created successfully and notification email sent.')

        return HttpResponseRedirect('/home/?ticket_created=true')

    #employees = employees.objects.all()  # Retrieve all employees
    return render(request, 'createTicket.html')

@login_required
def my_tickets(request):
    tickets = IncidentReport.objects.filter(user=request.user)
    print(tickets)  # For debugging: this will print the QuerySet of tickets to the console
    return render(request, 'my_Ticket.html', {'tickets': tickets})


@login_required
def ticket_details(request, ticket_id):
    ticket = get_object_or_404(IncidentReport, id=ticket_id, user=request.user)
    case_status = ticket.status
    case_type = ticket.issue_type
    created_by = ticket.user
    created_datetime = ticket.date_time
    assigned_to = ticket.assigned_to.username if ticket.assigned_to else None 
    if isinstance(ticket,IncidentReport):
        communication_history = Comment.objects.filter(ticket=ticket).order_by('created_at')
    else:
        communication_history = None  # Set communication_history to None or handle the case as needed
    return render(request, 'ticket_details.html', {
        'ticket': ticket,
        'case_status': ticket.status,
        'issue_type': ticket.issue_type,
        'created_by': ticket.user,
        'created_datetime': ticket.date_time,
        'assigned_to': ticket.assigned_to.username if ticket.assigned_to else None,
        'communication_history': communication_history,
    })

@login_required
def chat_box(request):
    # Fetch all chat messages
    user_messages = ChatMessage.objects.filter(sender=request.user) | ChatMessage.objects.filter(receiver=request.user)
    admin_messages = ChatMessage.objects.filter(sender__is_superuser=True)
    all_messages = user_messages | admin_messages
    return render(request, 'ticket_details.html', {'messages': messages})


@login_required
def send_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message_text')
        receiver = User.objects.filter(is_superuser=True).first()
        ChatMessage.objects.create(sender=request.user, receiver=receiver, message=message_text)
        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        # Redirect back to the chat box page for non-AJAX requests
        return HttpResponseRedirect('/chat_box/') 
    return render(request, 'ticket_details.html')



def fetch_messages(request):
    # Fetch and serialize messages
    messages = ChatMessage.objects.all()  # Fetch messages as per your requirements
    rendered_messages = render_to_string('message_template.html', {'messages': messages})
    return JsonResponse({'messages_html': rendered_messages})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def send_admin_reply(request, ticket_id):
    if request.method == 'POST':
        message_text = request.POST.get('message_text')
        ticket = get_object_or_404(IncidentReport, id=ticket_id, user=request.user)
        admin = request.user
        ChatMessage.objects.create(ticket=ticket, sender=admin, receiver=ticket.user, message=message_text)
        return redirect('ticket_details', ticket_id=ticket_id)

    return redirect('home')  # Redirect to home or any other appropriate URL

  # Import the generate_verification_code function
@csrf_exempt
def send_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            verification_code = generate_verification_code()
            subject = 'Email Verification Code'
            message = f'Your verification code is: {verification_code}'
            sender_email = settings.EMAIL_HOST_USER
            recipientlist = [email]
            send_mail(subject, message, sender_email, recipientlist)
            return JsonResponse({'message': 'Verification email sent successfully.', 'code': verification_code}, status=200)
        else:
            return JsonResponse({'error': 'Email not provided.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def verify_verification_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('verification_code')  # Assuming the field name is 'verification_code'
        
        # Perform your verification logic here
        expected_code = '123456'  # Replace with your actual expected verification code
        
        if code == expected_code:
            # Code is valid
            return JsonResponse({'success': True, 'message': 'Verification successful.'})
        else:
            # Code is invalid
            return JsonResponse({'success': False, 'message': 'Invalid verification code.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)