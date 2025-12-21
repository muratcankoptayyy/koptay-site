from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, JobPost, JobApplication, Notification
from . import jobs_bp
from datetime import datetime, timedelta

@jobs_bp.route('/')
@login_required
def index():
    """İş ilanları ana sayfası"""
    # Filtreleme
    position_type = request.args.get('position')
    city = request.args.get('city')
    
    query = JobPost.query.filter_by(is_active=True)
    
    if position_type:
        query = query.filter_by(position_type=position_type)
    if city:
        query = query.filter(JobPost.city.ilike(f"%{city}%"))
        
    jobs = query.order_by(JobPost.created_at.desc()).all()
    
    return render_template('pages/jobs/index.html', jobs=jobs)

@jobs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni iş ilanı oluştur"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        position_type = request.form.get('position_type')
        employment_type = request.form.get('employment_type')
        city = request.form.get('city')
        district = request.form.get('district')
        office_name = request.form.get('office_name')
        
        # Opsiyonel alanlar
        salary_min = request.form.get('salary_min')
        salary_max = request.form.get('salary_max')
        experience_years = request.form.get('experience_years')
        
        if not all([title, description, position_type, city]):
            flash('Lütfen zorunlu alanları doldurun.', 'error')
            return redirect(url_for('jobs.create'))
            
        job = JobPost(
            user_id=current_user.id,
            title=title,
            description=description,
            position_type=position_type,
            employment_type=employment_type,
            city=city,
            district=district,
            office_name=office_name or current_user.full_name,
            salary_min=float(salary_min) if salary_min else None,
            salary_max=float(salary_max) if salary_max else None,
            experience_years=int(experience_years) if experience_years else None,
            expires_at=datetime.now() + timedelta(days=30) # 30 gün yayında kalsın
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('İş ilanı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('jobs.index'))
        
    return render_template('pages/jobs/create.html')

@jobs_bp.route('/<int:id>')
@login_required
def detail(id):
    """İlan detayı"""
    job = JobPost.query.get_or_404(id)
    
    # Kullanıcı daha önce başvurmuş mu?
    has_applied = False
    if current_user.is_authenticated:
        application = JobApplication.query.filter_by(
            post_id=job.id, 
            applicant_id=current_user.id
        ).first()
        if application:
            has_applied = True
            
    return render_template('pages/jobs/detail.html', job=job, has_applied=has_applied)

@jobs_bp.route('/<int:id>/apply', methods=['POST'])
@login_required
def apply(id):
    """İlana başvur"""
    job = JobPost.query.get_or_404(id)
    
    if job.user_id == current_user.id:
        flash('Kendi ilanınıza başvuramazsınız.', 'error')
        return redirect(url_for('jobs.detail', id=id))
        
    # Zaten başvurmuş mu?
    existing_app = JobApplication.query.filter_by(
        post_id=job.id, 
        applicant_id=current_user.id
    ).first()
    
    if existing_app:
        flash('Bu ilana zaten başvurdunuz.', 'warning')
        return redirect(url_for('jobs.detail', id=id))
        
    cover_letter = request.form.get('cover_letter')
    
    application = JobApplication(
        post_id=job.id,
        applicant_id=current_user.id,
        message=cover_letter
    )
    
    job.applications_count += 1
    db.session.add(application)
    
    # Bildirim oluştur
    notification = Notification(
        user_id=job.user_id,
        type='new_application',
        title='Yeni İş Başvurusu',
        message=f'{current_user.full_name} "{job.title}" ilanınıza başvurdu.',
        action_url=url_for('jobs.view_applications', id=job.id),
        related_user_id=current_user.id,
        related_job_post_id=job.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    flash('Başvurunuz başarıyla gönderildi.', 'success')
    return redirect(url_for('jobs.detail', id=id))

@jobs_bp.route('/cv/edit', methods=['GET', 'POST'])
@login_required
def cv_edit():
    """CV Düzenle"""
    if request.method == 'POST':
        # Personal Info
        birth_date_str = request.form.get('birth_date')
        if birth_date_str:
            try:
                current_user.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        current_user.birth_place = request.form.get('birth_place')
        current_user.drivers_license = request.form.get('drivers_license')

        # Education
        schools = request.form.getlist('school[]')
        degrees = request.form.getlist('degree[]')
        years = request.form.getlist('year[]')
        
        education = []
        for i in range(len(schools)):
            if schools[i]:
                education.append({
                    'school': schools[i],
                    'degree': degrees[i],
                    'year': years[i]
                })
        
        # Work History
        companies = request.form.getlist('company[]')
        positions = request.form.getlist('position[]')
        work_years = request.form.getlist('work_year[]')
        
        work_history = []
        for i in range(len(companies)):
            if companies[i]:
                work_history.append({
                    'company': companies[i],
                    'position': positions[i],
                    'years': work_years[i]
                })
        
        # References
        ref_names = request.form.getlist('ref_name[]')
        ref_positions = request.form.getlist('ref_position[]')
        ref_phones = request.form.getlist('ref_phone[]')
        
        references = []
        for i in range(len(ref_names)):
            if ref_names[i]:
                references.append({
                    'name': ref_names[i],
                    'position': ref_positions[i],
                    'phone': ref_phones[i]
                })
                
        # Skills
        skills_input = request.form.get('skills')
        skills = [s.strip() for s in skills_input.split(',')] if skills_input else []
        
        current_user.education = education
        current_user.work_history = work_history
        current_user.skills = skills
        current_user.cv_references = references
        
        db.session.commit()
        flash('CV bilgileriniz güncellendi.', 'success')
        return redirect(url_for('jobs.cv_edit'))
        
    return render_template('pages/jobs/cv_edit.html')

@jobs_bp.route('/post/<int:id>/applications')
@login_required
def view_applications(id):
    """İlana gelen başvuruları görüntüle"""
    job = JobPost.query.get_or_404(id)
    
    if job.user_id != current_user.id:
        abort(403)
        
    applications = JobApplication.query.filter_by(post_id=id).order_by(JobApplication.created_at.desc()).all()
    return render_template('pages/jobs/applications.html', job=job, applications=applications)

@jobs_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """İş ilanını düzenle"""
    job = JobPost.query.get_or_404(id)
    
    # Yetki kontrolü
    if job.user_id != current_user.id:
        abort(403)
        
    if request.method == 'POST':
        job.title = request.form.get('title')
        job.description = request.form.get('description')
        job.position_type = request.form.get('position_type')
        job.employment_type = request.form.get('employment_type')
        job.city = request.form.get('city')
        job.district = request.form.get('district')
        job.office_name = request.form.get('office_name')
        
        salary_min = request.form.get('salary_min')
        salary_max = request.form.get('salary_max')
        experience_years = request.form.get('experience_years')
        
        job.salary_min = float(salary_min) if salary_min else None
        job.salary_max = float(salary_max) if salary_max else None
        job.experience_years = int(experience_years) if experience_years else None
        
        job.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('İlan başarıyla güncellendi.', 'success')
        return redirect(url_for('jobs.detail', id=job.id))
        
    return render_template('pages/jobs/edit.html', job=job)

@jobs_bp.route('/my-postings')
@login_required
def my_postings():
    """Yayınladığım ilanlar"""
    jobs = JobPost.query.filter_by(user_id=current_user.id).order_by(JobPost.created_at.desc()).all()
    return render_template('pages/jobs/my_postings.html', jobs=jobs)

@jobs_bp.route('/my-applications')
@login_required
def my_applications():
    """Yaptığım başvurular"""
    applications = JobApplication.query.filter_by(applicant_id=current_user.id).order_by(JobApplication.created_at.desc()).all()
    return render_template('pages/jobs/my_applications.html', applications=applications)
