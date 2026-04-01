from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.doctors.models import HealthcareStaff, QRScanLog


def is_admin(user):
    return user.is_authenticated and user.is_staff


# ─── CONNEXION ────────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('web_admin:dashboard')

    error = None
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone=phone, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('web_admin:dashboard')
        error = 'Téléphone ou mot de passe incorrect, ou accès non autorisé.'

    return render(request, 'web_admin/login.html', {'error': error})


def admin_logout(request):
    logout(request)
    return redirect('web_admin:login')


# ─── DASHBOARD ────────────────────────────────────────────

@login_required(login_url='/portail-admin/login/')
@user_passes_test(is_admin, login_url='/portail-admin/login/')
def dashboard(request):
    pending = HealthcareStaff.objects.filter(verification_status='PENDING').order_by('-created_at')
    verified = HealthcareStaff.objects.filter(verification_status='VERIFIED').order_by('-verified_at')
    rejected = HealthcareStaff.objects.filter(verification_status='REJECTED').order_by('-updated_at')

    stats = {
        'pending_count': pending.count(),
        'verified_count': verified.count(),
        'rejected_count': rejected.count(),
        'total_scans': QRScanLog.objects.count(),
    }

    return render(request, 'web_admin/dashboard.html', {
        'pending': pending,
        'verified': verified,
        'rejected': rejected,
        'stats': stats,
    })


# ─── ACTIONS VÉRIFICATION ────────────────────────────────

@login_required(login_url='/portail-admin/login/')
@user_passes_test(is_admin, login_url='/portail-admin/login/')
@require_POST
def verify_staff(request, staff_id):
    staff = get_object_or_404(HealthcareStaff, id=staff_id)
    staff.verified = True
    staff.verification_status = 'VERIFIED'
    staff.verified_by = request.user
    staff.verified_at = timezone.now()
    staff.save()
    return JsonResponse({'status': 'ok', 'message': f'{staff.full_name} vérifié avec succès.'})


@login_required(login_url='/portail-admin/login/')
@user_passes_test(is_admin, login_url='/portail-admin/login/')
@require_POST
def reject_staff(request, staff_id):
    staff = get_object_or_404(HealthcareStaff, id=staff_id)
    staff.verified = False
    staff.verification_status = 'REJECTED'
    staff.save()
    return JsonResponse({'status': 'ok', 'message': f'{staff.full_name} rejeté.'})


@login_required(login_url='/portail-admin/login/')
@user_passes_test(is_admin, login_url='/portail-admin/login/')
def staff_detail(request, staff_id):
    staff = get_object_or_404(HealthcareStaff, id=staff_id)
    scans = QRScanLog.objects.filter(healthcare_staff=staff).order_by('-timestamp')[:20]
    return render(request, 'web_admin/staff_detail.html', {'staff': staff, 'scans': scans})
