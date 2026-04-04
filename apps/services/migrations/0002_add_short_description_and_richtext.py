# Generated migration for adding short_description and converting description to RichTextField

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='short_description',
            field=models.TextField(default='', help_text='Brief summary for cards and listings'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='service',
            name='description',
            field=ckeditor.fields.RichTextField(help_text='Full content with rich text formatting'),
        ),
    ]
