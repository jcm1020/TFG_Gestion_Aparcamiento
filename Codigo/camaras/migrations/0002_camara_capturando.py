from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camaras', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='camara',
            name='capturando',
            field=models.BooleanField(default=False, verbose_name='Capturando', help_text='Indica si la camara esta capturando imagenes continuamente'),
        ),
    ]
