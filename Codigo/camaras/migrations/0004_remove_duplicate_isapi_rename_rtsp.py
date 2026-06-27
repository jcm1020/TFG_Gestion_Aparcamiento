from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camaras', '0003_camara_url_stream_isapi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='camara',
            name='url_stream_isapi',
        ),
        migrations.RenameField(
            model_name='camara',
            old_name='url_stream_rtsp',
            new_name='url_stream_isapi',
        ),
        migrations.AlterField(
            model_name='camara',
            name='url_stream_isapi',
            field=models.CharField(
                blank=True,
                default='http://{ip}/ISAPI/Streaming/channels/101/picture',
                help_text='URL de captura ISAPI. Ejemplo: http://{ip}/ISAPI/Streaming/channels/101/picture',
                max_length=500,
                verbose_name='URL Stream ISAPI',
            ),
        ),
    ]
