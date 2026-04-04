# Generated migration for adding summary and converting content to RichTextField

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticle',
            name='summary',
            field=models.TextField(blank=True, help_text='Brief summary for cards and listings'),
        ),
        migrations.AlterField(
            model_name='blogarticle',
            name='excerpt',
            field=models.TextField(blank=True, help_text='Short excerpt (deprecated, use summary)'),
        ),
        migrations.AlterField(
            model_name='blogarticle',
            name='content',
            field=ckeditor.fields.RichTextField(help_text='Full article content with rich text formatting'),
        ),
    ]
