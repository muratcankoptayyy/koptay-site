#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile.html dosyasını düzgün bir şekilde oluşturur"""

content = """{% extends "base.html" %}

{% block title %}{{ user.full_name }} - Profil - Ulusal Tevkil Ağı Projesi{% endblock %}

{% block content %}
<div class="px-2 sm:px-4 md:px-6 lg:px-10 xl:px-20 flex flex-1 justify-center py-3 sm:py-5">
    <div class="layout-content-container flex flex-col w-full max-w-7xl">
        <!-- Back Button -->
        <div class="p-2 sm:p-4 mb-2">
            <a href="{{ url_for('dashboard') if current_user.is_authenticated and current_user.id == user.id else url_for('list_posts') }}" class="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors">
                <span class="material-symbols-outlined text-xl">arrow_back</span>
                <span class="text-sm font-medium">Geri Dön</span>
            </a>
        </div>
        
        <!-- Profile Header -->
        <div class="relative bg-gradient-to-br from-primary via-blue-600 to-indigo-700 rounded-2xl p-4 sm:p-6 md:p-8 mb-4 sm:mb-6 text-white overflow-hidden">
            <!-- Background Pattern -->
            <div class="absolute inset-0 opacity-10 pointer-events-none">
                <div class="absolute top-0 left-0 w-64 h-64 bg-white rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
                <div class="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl transform translate-x-1/2 translate-y-1/2"></div>
            </div>
            
            <div class="relative z-10 flex flex-col md:flex-row items-center gap-4 sm:gap-6">
                <!-- Profile Photo -->
                <div class="relative group flex-shrink-0">
                    <img src="{{ user.avatar_url if user.avatar_url else 'https://ui-avatars.com/api/?name=' + user.full_name + '&background=ffffff&color=1661da&size=160' }}" 
                         alt="{{ user.full_name }}" 
                         class="w-28 h-28 sm:w-32 sm:h-32 md:w-40 md:h-40 rounded-full border-4 border-white shadow-2xl object-cover">
                    
                    {% if current_user.is_authenticated and current_user.id == user.id %}
                    <a href="{{ url_for('edit_profile') }}" class="absolute inset-0 rounded-full bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                        <div class="text-center">
                            <span class="material-symbols-outlined text-3xl sm:text-4xl mb-1">photo_camera</span>
                            <p class="text-xs hidden sm:block">Fotoğraf<br>Değiştir</p>
                        </div>
                    </a>
                    {% endif %}
                    
                    {% if user.verified %}
                    <div class="absolute bottom-1 right-1 sm:bottom-2 sm:right-2 bg-white rounded-full p-1 sm:p-1.5 shadow-lg" title="Doğrulanmış Üye">
                        <span class="material-symbols-outlined text-green-500 text-xl sm:text-2xl">verified</span>
                    </div>
                    {% endif %}
                </div>
                
                <div class="flex-1 text-center md:text-left w-full md:w-auto">
                    <div class="mb-3">
                        <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black mb-2 leading-tight break-words">{{ user.full_name }}</h1>
                        {% if user.lawyer_type == 'stajyer' %}
                        <span class="inline-flex items-center gap-1 px-3 py-1 bg-yellow-500/20 backdrop-blur-sm border border-yellow-300/30 rounded-full text-xs sm:text-sm font-semibold">
                            <span class="material-symbols-outlined text-sm sm:text-base">school</span>
                            <span class="whitespace-nowrap">Stajyer Avukat</span>
                        </span>
                        {% else %}
                        <span class="inline-flex items-center gap-1 px-3 py-1 bg-white/20 backdrop-blur-sm border border-white/30 rounded-full text-xs sm:text-sm font-semibold">
                            <span class="material-symbols-outlined text-sm sm:text-base">gavel</span>
                            <span class="whitespace-nowrap">Avukat</span>
                        </span>
                        {% endif %}
                    </div>
                    
                    <div class="flex flex-wrap gap-2 sm:gap-3 justify-center md:justify-start text-white/90 mb-3 sm:mb-4 text-xs sm:text-sm">
                        <span class="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg">
                            <span class="material-symbols-outlined text-base sm:text-lg">location_on</span>
                            <span class="truncate max-w-[120px] sm:max-w-none">{{ user.city }}{% if user.district %}, {{ user.district }}{% endif %}</span>
                        </span>
                        <span class="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg">
                            <span class="material-symbols-outlined text-base sm:text-lg">email</span>
                            <span class="truncate max-w-[120px] sm:max-w-[200px]">{{ user.email }}</span>
                        </span>
                        {% if user.phone %}
                        <span class="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg">
                            <span class="material-symbols-outlined text-base sm:text-lg">phone</span>
                            <span class="whitespace-nowrap">{{ user.phone }}</span>
                        </span>
                        {% endif %}
                        {% if user.whatsapp_number %}
                        <span class="flex items-center gap-1 bg-green-500/20 backdrop-blur-sm px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg border border-green-400/30">
                            <span class="material-symbols-outlined text-base sm:text-lg">chat</span>
                            <span class="whitespace-nowrap">WhatsApp</span>
                        </span>
                        {% endif %}
                    </div>
                    
                    {% if user.specializations %}
                    <div class="flex flex-wrap gap-2 justify-center md:justify-start mb-3 sm:mb-4">
                        {% for spec in user.specializations %}
                        <span class="px-2 sm:px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs sm:text-sm font-medium border border-white/20">{{ spec }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                
                <div class="flex-shrink-0 w-full md:w-auto mt-2 md:mt-0">
                    {% if current_user.is_authenticated and current_user.id == user.id %}
                    <a href="{{ url_for('edit_profile') }}" class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-4 sm:px-6 py-2 sm:py-3 bg-white text-primary rounded-xl font-semibold hover:bg-gray-100 transition-all hover:shadow-xl text-sm sm:text-base whitespace-nowrap">
                        <span class="material-symbols-outlined text-xl">edit</span>
                        <span>Profili Düzenle</span>
                    </a>
                    {% else %}
                    <a href="{{ url_for('send_message', receiver_id=user.id) }}" class="w-full md:w-auto inline-flex items-center justify-center gap-2 px-4 sm:px-6 py-2 sm:py-3 bg-white text-primary rounded-xl font-semibold hover:bg-gray-100 transition-all hover:shadow-xl text-sm sm:text-base whitespace-nowrap">
                        <span class="material-symbols-outlined text-xl">chat</span>
                        <span>Mesaj Gönder</span>
                    </a>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Achievement Badges -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 sm:gap-3 md:gap-4 mb-4 sm:mb-6">
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-3 sm:p-4 md:p-6 text-white text-center shadow-lg hover:shadow-2xl transition-shadow">
                <div class="text-2xl sm:text-3xl md:text-4xl font-black mb-1 sm:mb-2">{{ user.completed_tasks_count }}</div>
                <div class="text-[10px] sm:text-xs font-medium opacity-90 flex items-center justify-center gap-0.5 sm:gap-1 flex-wrap">
                    <span class="material-symbols-outlined text-sm sm:text-base">task_alt</span>
                    <span><span class="hidden sm:inline">Tamamlanan </span>Görev</span>
                </div>
            </div>
            
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-3 sm:p-4 md:p-6 text-white text-center shadow-lg hover:shadow-2xl transition-shadow">
                <div class="text-2xl sm:text-3xl md:text-4xl font-black mb-1 sm:mb-2">{{ user.attended_hearings_count }}</div>
                <div class="text-[10px] sm:text-xs font-medium opacity-90">Duruşma</div>
            </div>
            
            <div class="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl p-3 sm:p-4 md:p-6 text-white text-center shadow-lg hover:shadow-2xl transition-shadow">
                <div class="text-2xl sm:text-3xl md:text-4xl font-black mb-1 sm:mb-2 flex items-center justify-center gap-1">
                    {% if user.rating_average %}{{ "%.1f"|format(user.rating_average) }}<span class="material-symbols-outlined text-lg sm:text-2xl">star</span>{% else %}-{% endif %}
                </div>
                <div class="text-[10px] sm:text-xs font-medium opacity-90"><span class="hidden sm:inline">Ortalama </span>Puan</div>
            </div>
            
            <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-3 sm:p-4 md:p-6 text-white text-center shadow-lg hover:shadow-2xl transition-shadow">
                <div class="text-2xl sm:text-3xl md:text-4xl font-black mb-1 sm:mb-2">{{ user.rating_count }}</div>
                <div class="text-[10px] sm:text-xs font-medium opacity-90">Değerlendirme</div>
            </div>
            
            <div class="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-3 sm:p-4 md:p-6 text-white text-center shadow-lg hover:shadow-2xl transition-shadow col-span-2 sm:col-span-1">
                <div class="text-2xl sm:text-3xl md:text-4xl font-black mb-1 sm:mb-2">{% if user.total_jobs > 0 %}{{ ((user.completed_jobs / user.total_jobs) * 100)|round|int }}%{% else %}-%{% endif %}</div>
                <div class="text-[10px] sm:text-xs font-medium opacity-90">Başarı Oranı</div>
            </div>
        </div>
        
        <!-- Rest of content will be added in next part -->
    </div>
</div>
{% endblock %}
"""

# Dosyayı yaz
with open('templates/profile.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Profile.html dosyası oluşturuldu!")
