from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from flask import (
	Blueprint,
	Flask,
	redirect,
	render_template,
	request,
	send_from_directory,
	session,
	url_for,
)


@dataclass
class Message:
	body: str
	timestamp: str
	is_owner: bool = False


@dataclass
class Thread:
	name: str
	initials: str
	last_timestamp: str
	preview: str
	meta: str
	unread: int = 0
	active: bool = False
	messages: List[Message] = field(default_factory=list)


def build_sample_threads() -> tuple[list[Thread], Thread]:
	now = datetime.utcnow()

	thread_one = Thread(
		name="Av. Merve Kılıç",
		initials="MK",
		last_timestamp="2 dk önce",
		preview="Haricen göndereceğiniz belgeleri bekliyorum.",
		meta="İcra dosyası #4591 · Aktif yetki",
		unread=2,
		active=True,
		messages=[
			Message(
				body="Merhaba, muris muvazaası dosyasındaki son durumu paylaşır mısınız?",
				timestamp=(now - timedelta(hours=5)).strftime("%d.%m.%Y %H:%M"),
			),
			Message(
				body="Tabii, karşı taraftan henüz dönüş olmadı fakat bugün icra müdürlüğü ile görüşeceğim.",
				timestamp=(now - timedelta(hours=4, minutes=20)).strftime("%d.%m.%Y %H:%M"),
				is_owner=True,
			),
			Message(
				body="Tamamdır, ek belgeleri birazdan yüklerim.",
				timestamp=(now - timedelta(hours=2, minutes=45)).strftime("%d.%m.%Y %H:%M"),
			),
			Message(
				body="Teşekkürler. Belgeler gelir gelmez dosyaya ekleyeceğim.",
				timestamp=(now - timedelta(minutes=17)).strftime("%d.%m.%Y %H:%M"),
				is_owner=True,
			),
		],
	)

	thread_two = Thread(
		name="Av. Emre Özkan",
		initials="EÖ",
		last_timestamp="Dün",
		preview="Yeni masraf kalemlerini dosyaya işledim.",
		meta="Ticari tahkim · Kapalı yetki",
		unread=0,
		messages=[
			Message(
				body="Uğur Bey, yarınki duruşma için tanık listesi hazır mı?",
				timestamp=(now - timedelta(days=2, hours=3)).strftime("%d.%m.%Y %H:%M"),
			),
			Message(
				body="Evet, dosyaya yükledim. Ayrıca masraf kalemlerini güncelledim.",
				timestamp=(now - timedelta(days=1, hours=20)).strftime("%d.%m.%Y %H:%M"),
				is_owner=True,
			),
		],
	)

	thread_three = Thread(
		name="Av. Sude Ateş",
		initials="SA",
		last_timestamp="3 gün önce",
		preview="Karşı tarafla uzlaşma teklifini paylaştım.",
		meta="Kat mülkiyeti davası",
		unread=0,
		messages=[
			Message(
				body="Uzlaşma teklifini ilettim, dönüş aldığımda haber veririm.",
				timestamp=(now - timedelta(days=3, hours=4)).strftime("%d.%m.%Y %H:%M"),
			),
			Message(
				body="Harika, bekliyorum. Son taslakta ekstra bir değişiklik yok.",
				timestamp=(now - timedelta(days=3, hours=3)).strftime("%d.%m.%Y %H:%M"),
				is_owner=True,
			),
		],
	)

	threads = [thread_one, thread_two, thread_three]
	return threads, thread_one


def create_app() -> Flask:
	app = Flask(
		__name__,
		template_folder="templates",
		static_folder="static",
	)
	app.secret_key = "phoenix-demo-secret"

	phoenix_bp = Blueprint(
		"phoenix",
		__name__,
	)

	demo_credentials = {
		"email": "demo@tevkil.com",
		"password": "Phoenix2025!",
	}

	demo_user = {
		"full_name": "Av. Ayşe Koptay",
		"initials": "AK",
		"bar": "İstanbul Barosu",
		"city": "İstanbul",
		"member_no": "2015/89231",
		"email": "ayse.koptay@example.com",
		"phone": "+90 532 123 45 67",
		"expertise": ["İcra ve İflas", "Ticaret Hukuku", "Aile Hukuku"],
		"languages": ["Türkçe", "İngilizce"],
		"bio": (
			"10+ yıllık icra ve ticaret hukuku deneyimiyle şirketlerin takip süreçlerini "
			"yöneten ve çok lokasyonlu duruşmaları koordine eden avukat."
		),
	}

	dashboard_metrics = [
		{"label": "Aktif İlan", "value": "8", "trend": 12, "icon": "rocket_launch"},
		{"label": "Bekleyen Başvuru", "value": "17", "trend": 5, "icon": "assignment_turned_in"},
		{"label": "Mesaj Yanıt Süresi", "value": "1s 20dk", "trend": -9, "icon": "schedule"},
		{"label": "Tamamlanan Tevkil", "value": "42", "trend": 4, "icon": "verified"},
	]

	dashboard_workflows = [
		{
			"title": "İcra dosyası #4591",
			"client": "Av. Merve Kılıç",
			"city": "İstanbul",
			"status": "İmza bekleniyor",
			"deadline": "08 Kas 2025",
		},
		{
			"title": "Ankara ticaret tahkimi",
			"client": "Av. Emre Özkan",
			"city": "Ankara",
			"status": "Yetki gönderildi",
			"deadline": "12 Kas 2025",
		},
		{
			"title": "Kat mülkiyeti uyuşmazlığı",
			"client": "Av. Sude Ateş",
			"city": "İzmir",
			"status": "Uzlaşma teklifi",
			"deadline": "15 Kas 2025",
		},
	]

	dashboard_hearings = [
		{
			"date": "04 Kas 2025",
			"time": "10:30",
			"title": "İcra Müdürlüğü görüşmesi",
			"court": "Bakırköy 5. İcra Müdürlüğü",
			"counterpart": "Alacaklı Vekili",
		},
		{
			"date": "05 Kas 2025",
			"time": "14:00",
			"title": "Ticaret Mahkemesi duruşması",
			"court": "Ankara 2. Asliye Ticaret Mahkemesi",
			"counterpart": "Davalı Şirket Vekili",
		},
		{
			"date": "07 Kas 2025",
			"time": "09:00",
			"title": "Aile Mahkemesi keşfi",
			"court": "İzmir 3. Aile Mahkemesi",
			"counterpart": "Karşı taraf vekili",
		},
	]

	dashboard_stats = {
		"rating_count": 112,
		"success_rate": 93,
		"completed_jobs": 128,
		"avg_response": 58,
		"active_applications": 9,
	}

	dashboard_notifications = [
		{
			"icon": "task_alt",
			"title": "Bakırköy icra dosyasında yeni belge",
			"description": "Müvekkiliniz yetki belgesini imzaladı.",
			"time": "3 dk önce",
		},
		{
			"icon": "campaign",
			"title": "Ankara tahkim dosyasında mesaj",
			"description": "Av. Emre Özkan: 'Masraf kalemlerini güncelledim.'",
			"time": "27 dk önce",
		},
		{
			"icon": "verified_user",
			"title": "Yeni avukat doğrulaması tamamlandı",
			"description": "Av. Pelin Şahin profilini doğruladı.",
			"time": "1 saat önce",
		},
	]

	schedule_calendar = [
		{"label": "Pzt", "date": 3, "is_today": False, "has_event": False},
		{"label": "Sal", "date": 4, "is_today": True, "has_event": True},
		{"label": "Çar", "date": 5, "is_today": False, "has_event": True},
		{"label": "Per", "date": 6, "is_today": False, "has_event": False},
		{"label": "Cum", "date": 7, "is_today": False, "has_event": True},
		{"label": "Cmt", "date": 8, "is_today": False, "has_event": False, "is_weekend": True},
		{"label": "Paz", "date": 9, "is_today": False, "has_event": False, "is_weekend": True},
	]

	schedule_summary = {
		"week": "3-9 Kasım 2025",
		"total_sessions": 6,
		"completed_sessions": 2,
		"pending_documents": 3,
	}

	schedule_upcoming = [
		{
			"title": "Bakırköy icra dosyası",
			"datetime": "04 Kas 2025 · 10:30",
			"location": "Bakırköy 5. İcra Müdürlüğü",
			"status": "Hazırlık devam ediyor",
		},
		{
			"title": "Tahkim duruşması",
			"datetime": "05 Kas 2025 · 14:00",
			"location": "ATO Ticaret Merkezi",
			"status": "Yetki belgesi gönderildi",
		},
		{
			"title": "Aile mahkemesi keşfi",
			"datetime": "07 Kas 2025 · 09:00",
			"location": "İzmir Karşıyaka",
			"status": "Karşı taraf randevusu bekleniyor",
		},
	]

	schedule_tasks = [
		{"title": "Dosya özetini paylaş", "due": "Bugün", "assignee": "Av. Ayşe"},
		{"title": "Tanık listesi revizyonu", "due": "05 Kas", "assignee": "Av. Emre"},
		{"title": "Masraf kalemi onayı", "due": "06 Kas", "assignee": "Tevkil ekibi"},
	]

	posts_filters = {
		"cities": ["İstanbul", "Ankara", "İzmir", "Bursa"],
		"categories": ["İcra", "Ticaret", "Gayrimenkul", "Aile"],
	}

	posts_explore_data = [
		{
			"category": "İcra",
			"city": "İstanbul",
			"courthouse": "Bakırköy Adliyesi",
			"title": "İcra takip dosyası için duruşma temsilcisi",
			"excerpt": (
				"Dosya kapsamındaki haciz, ödeme ve icra işlemlerinin duruşma takibini "
				"üstlenecek meslektaş arıyoruz."
			),
			"tags": ["haciz", "alacak", "icra"],
			"budget": "12.500 ₺",
			"deadline": "08 Kas 2025",
		},
		{
			"category": "Ticaret",
			"city": "Ankara",
			"courthouse": "Ankara Bölge Adliye Mahkemesi",
			"title": "Tahkim dosyası keşfi için vekil",
			"excerpt": (
				"Kurumsal müvekkilimizin ticari tahkim dosyasında yerel temsil arayışımız "
				"bulunmaktadır."
			),
			"tags": ["tahkim", "sözleşme", "ticari"],
			"budget": "18.000 ₺",
			"deadline": "12 Kas 2025",
		},
		{
			"category": "Gayrimenkul",
			"city": "İzmir",
			"courthouse": "İzmir Adliyesi",
			"title": "Kat mülkiyeti davası için keşif",
			"excerpt": (
				"Kat mülkiyeti uyuşmazlığında keşfe katılacak ve tutanakları hazırlayacak "
				"deneyimli meslektaş arıyoruz."
			),
			"tags": ["kat mülkiyeti", "keşif", "gayrimenkul"],
			"budget": "9.000 ₺",
			"deadline": "15 Kas 2025",
		},
	]

	posts_pagination = {
		"total": 24,
		"start": 1,
		"end": 9,
		"current": 1,
		"pages": [1, 2, 3],
	}

	posts_manage_data = [
		{
			"title": "İcra dosyası #4591",
			"published_at": "01 Kas 2025",
			"city": "İstanbul",
			"budget": "12.500 ₺",
			"applications": 6,
			"status": "Başvuru bekliyor",
			"status_class": "bg-amber-100 text-amber-700",
		},
		{
			"title": "Tahkim dosyası",
			"published_at": "27 Eki 2025",
			"city": "Ankara",
			"budget": "18.000 ₺",
			"applications": 4,
			"status": "Görüşmede",
			"status_class": "bg-sky-100 text-sky-700",
		},
		{
			"title": "Kat mülkiyeti keşfi",
			"published_at": "19 Eki 2025",
			"city": "İzmir",
			"budget": "9.000 ₺",
			"applications": 9,
			"status": "Yetki gönderildi",
			"status_class": "bg-emerald-100 text-emerald-700",
		},
		{
			"title": "Vakıf üniversitesi sözleşmesi",
			"published_at": "10 Eki 2025",
			"city": "Bursa",
			"budget": "22.500 ₺",
			"applications": 3,
			"status": "Taslak",
			"status_class": "bg-slate-200 text-slate-700",
		},
	]

	posts_manage_pagination = {
		"summary": "Toplam 8 ilandan 1-4 arası gösteriliyor",
	}

	profile_summary = {
		"headline": "Çok lokasyonlu icra ve ticaret dosyalarında 10+ yıllık deneyim",
		"stats": {
			"rating": 4.8,
			"completed": 128,
			"response_time": "58 dk",
			"followers": 312,
		},
		"badges": [
			"KVKK Uyum Sertifikası",
			"Baro Yetki Onayı",
			"24 Saat Yanıt Garantisi",
		],
	}

	profile_timeline = [
		{
			"year": "2025",
			"title": "Bakırköy icra platformu",
			"description": "Kurumsal müvekkiller için icra takip otomasyonunu hayata geçirdi.",
		},
		{
			"year": "2023",
			"title": "Ankara tahkim temsilciliği",
			"description": "Çok taraflı ticaret uyuşmazlığında davacı vekilliği yaptı.",
		},
		{
			"year": "2019",
			"title": "İstanbul Barosu eğitim komisyonu",
			"description": "Genç avukatlar için icra hukuku eğitimleri organize etti.",
		},
	]

	profile_reviews = [
		{
			"author": "Av. Merve Kılıç",
			"role": "Müvekkil vekili",
			"comment": (
				"Duruşma raporlaması ve belge paylaşımı konusunda çok sistematik. Harika bir "
				"iş birliği deneyimi yaşadık."
			),
			"rating": 5,
			"date": "Eylül 2025",
		},
		{
			"author": "Av. Emre Özkan",
			"role": "Tahkim partneri",
			"comment": (
				"Yerel prosedürleri çok iyi biliyor, kısa sürede yetki ve keşif süreçlerini "
				"tamamladı."
			),
			"rating": 5,
			"date": "Temmuz 2025",
		},
	]

	settings_sections = [
		{
			"title": "Bildirim Tercihleri",
			"description": "Mesaj, başvuru ve duruşma hatırlatmaları için bildirim kanallarını seç.",
			"options": [
				{"label": "E-posta bildirimleri", "subtext": "Tüm yeni başvuru ve mesajlarda", "enabled": True},
				{"label": "Mobil push", "subtext": "Duruşma hatırlatmaları ve kritik aksiyonlarda", "enabled": True},
				{"label": "WhatsApp bilgilendirmesi", "subtext": "Yetki belgesi onayında", "enabled": False},
			],
		},
		{
			"title": "Güvenlik",
			"description": "Hesabının güvenliğini artır.",
			"options": [
				{"label": "Çok faktörlü doğrulama", "subtext": "SMS + Authenticator uygulaması", "enabled": True},
				{"label": "Oturum hatırlatıcıları", "subtext": "Yeni cihaz girişlerinde uyarı al", "enabled": True},
				{"label": "Otomatik çıkış", "subtext": "15 dakika pasiflik sonrası", "enabled": False},
			],
		},
		{
			"title": "Entegrasyonlar",
			"description": "Harici sistemlerle veri paylaşımını yönet.",
			"options": [
				{"label": "Google Takvim", "subtext": "Duruşma takviminle senkronize et", "enabled": True},
				{"label": "Muhasebe API", "subtext": "Masraf kalemlerini otomatik aktar", "enabled": False},
			],
		},
	]

	admin_metrics = [
		{"label": "Aktif kullanıcı", "value": "1.842", "change": "+6%", "icon": "group"},
		{"label": "Bekleyen doğrulama", "value": "12", "change": "-3", "icon": "verified_user"},
		{"label": "SLA uyumu", "value": "%98", "change": "+2%", "icon": "schedule"},
		{"label": "Destek talepleri", "value": "27", "change": "Yeni", "icon": "support"},
	]

	admin_verifications = [
		{
			"name": "Av. Pelin Şahin",
			"bar": "İzmir Barosu",
			"submitted_at": "02 Kas 2025",
			"status": "Belgeler incelenecek",
		},
		{
			"name": "Av. Can Yıldız",
			"bar": "Ankara Barosu",
			"submitted_at": "01 Kas 2025",
			"status": "Telefon doğrulaması bekliyor",
		},
		{
			"name": "Av. Derya Tüfekçi",
			"bar": "İstanbul Barosu",
			"submitted_at": "30 Eki 2025",
			"status": "Onaylandı",
		},
	]

	admin_audit_log = [
		{
			"actor": "Av. Ayşe Koptay",
			"action": "Tahkim dosyası için yetki belgesi talep etti",
			"time": "5 dk önce",
			"status": "Başarılı",
		},
		{
			"actor": "Sistem",
			"action": "Bakırköy icra dosyası belgeleri arşivlendi",
			"time": "1 saat önce",
			"status": "Tamamlandı",
		},
		{
			"actor": "Av. Emre Özkan",
			"action": "Yeni mesaj gönderdi",
			"time": "3 saat önce",
			"status": "Başarılı",
		},
	]

	contact_channels = [
		{
			"label": "Müşteri başarı",
			"value": "destek@tevkil.com",
			"icon": "support_agent",
			"description": "Hafta içi 09:00-19:00 arasında yanıt veriyoruz.",
			"cta": "E-posta gönder",
		},
		{
			"label": "WhatsApp destek",
			"value": "+90 542 000 00 00",
			"icon": "chat",
			"description": "Yetki belgesi ve ödeme hatırlatmalarında hızlı destek.",
			"cta": "Sohbeti başlat",
		},
		{
			"label": "Ofis",
			"value": "Levent Mah. Büyükdere Cd. No:201/a, İstanbul",
			"icon": "location_on",
			"description": "Hafta içi randevu ile görüşme sağlanır.",
			"cta": "Haritada aç",
		},
	]

	policy_content = {
		"privacy": {
			"title": "Gizlilik Politikası",
			"lead": "Tevkil Phoenix kullanıcı verilerini KVKK kapsamında işler ve saklar.",
			"updated": "01 Kasım 2025",
			"sections": [
				{
					"heading": "Toplanan Veriler",
					"body": [
						"Kimlik ve iletişim bilgilerinizi (ad, soyad, baro kaydı, e-posta, telefon) alırız.",
						"Mesleki yetkinlik belgeleri ve yetki belgesi kayıtları.",
					],
				},
				{
					"heading": "İşleme Amaçları",
					"items": [
						"İş devri eşleştirme süreçlerini yönetmek",
						"Yetki belgelerinin mevzuata uygun şekilde arşivlenmesi",
						"Destek taleplerine yanıt vermek",
					],
				},
			],
		},
		"terms": {
			"title": "Kullanım Koşulları",
			"lead": "Platformu kullanarak aşağıdaki koşulları kabul etmiş olursunuz.",
			"updated": "01 Kasım 2025",
			"sections": [
				{
					"heading": "Hizmet Tanımı",
					"body": [
						"Tevkil Phoenix avukatlar arasında iş devri ve duruşma temsilini kolaylaştırır.",
						"Platformda oluşturulan tüm ilanlar ilgili baro kurallarına uygun olmalıdır.",
					],
				},
				{
					"heading": "Kullanıcı Yükümlülükleri",
					"items": [
						"Baro kayıt bilgilerinin güncel tutulması",
						"Yetki belgesi süreçlerinde doğru bilgi paylaşımı",
						"Meslek etiğine aykırı davranışlardan kaçınma",
					],
				},
			],
		},
		"cookie": {
			"title": "Çerez Politikası",
			"lead": "Web deneyimini iyileştirmek için zorunlu ve tercihe bağlı çerezler kullanıyoruz.",
			"updated": "01 Kasım 2025",
			"sections": [
				{
					"heading": "Çerez Türleri",
					"items": [
						"Oturum çerezleri: Giriş bilgilerinizin korunmasını sağlar.",
						"Analitik çerezler: Anonim kullanım metriklerini ölçer.",
						"Tercih çerezleri: Dil ve tema tercihinizi kaydeder.",
					],
				},
				{
					"heading": "Yönetim",
					"body": [
						"Tarayıcı ayarlarınız üzerinden çerez tercihlerinizi güncelleyebilirsiniz.",
						"Tercih çerezlerini reddetmeniz bazı özellikleri kısıtlayabilir.",
					],
				},
			],
		},
	}

	@phoenix_bp.app_context_processor
	def inject_common():
		"""Expose helpers and demo user info to all templates."""

		return {"now": datetime.now, "user": demo_user}

	@phoenix_bp.route("/")
	def home():
		return render_template("phoenix/pages/home.html")

	@app.route("/phoenix/static/<path:filename>")
	def phoenix_static(filename: str):
		return send_from_directory(app.static_folder, filename)

	@phoenix_bp.route("/dashboard")
	def dashboard_overview():
		return render_template(
			"phoenix/pages/dashboard/overview.html",
			metrics=dashboard_metrics,
			workflows=dashboard_workflows,
			hearings=dashboard_hearings,
			stats=dashboard_stats,
			notifications=dashboard_notifications,
		)

	@phoenix_bp.route("/dashboard/schedule")
	def dashboard_schedule():
		return render_template(
			"phoenix/pages/dashboard/schedule.html",
			calendar_days=schedule_calendar,
			summary=schedule_summary,
			upcoming_hearings=schedule_upcoming,
			tasks=schedule_tasks,
		)

	@phoenix_bp.route("/messages")
	def messages_center():
		threads, active_thread = build_sample_threads()
		login_success = session.pop("phoenix_demo_login_success", False)
		return render_template(
			"phoenix/pages/messages/center.html",
			threads=threads,
			active_thread=active_thread,
			login_success=login_success,
		)

	@phoenix_bp.route("/posts")
	def posts_explore():
		return render_template(
			"phoenix/pages/posts/explore.html",
			filters=posts_filters,
			posts=posts_explore_data,
			pagination=posts_pagination,
		)

	@phoenix_bp.route("/posts/manage")
	def posts_manage():
		return render_template(
			"phoenix/pages/posts/manage.html",
			posts=posts_manage_data,
			pagination=posts_manage_pagination,
		)

	@phoenix_bp.route("/profile")
	def profile_view():
		return render_template(
			"phoenix/pages/profile/view.html",
			profile=profile_summary,
			timeline=profile_timeline,
			reviews=profile_reviews,
		)

	@phoenix_bp.route("/settings")
	def settings_preferences():
		return render_template(
			"phoenix/pages/settings/preferences.html",
			sections=settings_sections,
		)

	@phoenix_bp.route("/admin")
	def admin_overview():
		return render_template(
			"phoenix/pages/admin/overview.html",
			metrics=admin_metrics,
			verifications=admin_verifications,
			audit_log=admin_audit_log,
		)

	@phoenix_bp.route("/auth/login", methods=["GET", "POST"])
	def auth_login():
		error: str | None = None
		email_value = ""

		if request.method == "POST":
			email_value = (request.form.get("email") or "").strip()
			password_value = request.form.get("password") or ""
		else:
			email_value = (request.args.get("email") or "").strip()
			password_value = request.args.get("password") or ""

		if email_value or password_value:
			if (
				email_value.lower() == demo_credentials["email"]
				and password_value == demo_credentials["password"]
			):
				session["phoenix_demo_user"] = demo_credentials["email"]
				session["phoenix_demo_login_success"] = True
				return redirect(url_for("phoenix.messages_center"))

			error = "E-posta veya şifre eşleşmedi. Lütfen aşağıdaki demo bilgilerini kullanın."

		return render_template(
			"phoenix/pages/auth/login.html",
			error=error,
			email=email_value,
		)

	@phoenix_bp.route("/auth/register")
	def auth_register():
		return render_template("phoenix/pages/auth/register.html")

	@phoenix_bp.route("/auth/forgot")
	def auth_forgot():
		return render_template("phoenix/pages/auth/forgot_password.html")

	@phoenix_bp.route("/policies/privacy")
	def policy_privacy():
		return render_template(
			"phoenix/pages/static/policy.html",
			policy=policy_content["privacy"],
		)

	@phoenix_bp.route("/policies/terms")
	def policy_terms():
		return render_template(
			"phoenix/pages/static/policy.html",
			policy=policy_content["terms"],
		)

	@phoenix_bp.route("/policies/cookie")
	def policy_cookie():
		return render_template(
			"phoenix/pages/static/policy.html",
			policy=policy_content["cookie"],
		)

	@phoenix_bp.route("/contact")
	def contact():
		return render_template(
			"phoenix/pages/contact.html",
			channels=contact_channels,
		)

	app.register_blueprint(phoenix_bp)

	return app


if __name__ == "__main__":
	application = create_app()
	application.run(debug=True, port=5050)
