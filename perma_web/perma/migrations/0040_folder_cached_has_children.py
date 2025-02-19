# Generated by Django 4.2.13 on 2024-05-16 20:21

from django.db import migrations, models

from django.db.models import OuterRef, Exists

def update_cached_has_children(apps, schema_editor):
    Folder = apps.get_model('perma', 'Folder')

    print("Updating cached_has_children.")
    Folder.objects.update(
        cached_has_children=Exists(
            Folder.objects.filter(
                parent_id=OuterRef('id')
            )
        )
    )
    print("Updated cached_has_children.")

class Migration(migrations.Migration):

    dependencies = [
        ('perma', '0039_auto_20240412_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='cached_has_children',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(update_cached_has_children, migrations.RunPython.noop, elidable=True),
    ]
