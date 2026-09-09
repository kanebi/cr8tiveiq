from django import forms
from django.contrib import admin

from .models import PortfolioGalleryImage, PortfolioProject, PortfolioVideo


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        return single_file_clean(data, initial)


class PortfolioProjectAdminForm(forms.ModelForm):
    gallery_uploads = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        help_text='Select multiple gallery images. This is separate from the featured image.',
    )
    video_uploads = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'video/*'}),
        help_text='Select multiple video files, or add YouTube/Vimeo links in the videos section below.',
    )

    class Meta:
        model = PortfolioProject
        fields = '__all__'


class PortfolioGalleryImageInline(admin.TabularInline):
    model = PortfolioGalleryImage
    extra = 1
    fields = ('image', 'caption', 'order')


class PortfolioVideoInline(admin.TabularInline):
    model = PortfolioVideo
    extra = 1
    fields = ('video', 'embed_url', 'title', 'order')


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(admin.ModelAdmin):
    form = PortfolioProjectAdminForm
    list_display = ('title', 'client_name', 'category', 'is_featured', 'gallery_count', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'client_name', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('services_used',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = (PortfolioGalleryImageInline, PortfolioVideoInline)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'client_name', 'category')
        }),
        ('Content', {
            'fields': ('description', 'featured_image', 'gallery_uploads', 'video_uploads')
        }),
        ('Details', {
            'fields': ('services_used', 'timeline', 'results')
        }),
        ('Settings', {
            'fields': ('is_featured', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('gallery_items', 'video_items')

    @admin.display(description='Gallery')
    def gallery_count(self, obj):
        return f'{obj.gallery_items.count()} images / {obj.video_items.count()} videos'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        project = form.instance
        images = request.FILES.getlist('gallery_uploads')
        start = project.gallery_items.count()
        for index, uploaded in enumerate(images):
            PortfolioGalleryImage.objects.create(
                project=project,
                image=uploaded,
                order=start + index,
            )
        videos = request.FILES.getlist('video_uploads')
        start = project.video_items.count()
        for index, uploaded in enumerate(videos):
            PortfolioVideo.objects.create(
                project=project,
                video=uploaded,
                order=start + index,
            )
