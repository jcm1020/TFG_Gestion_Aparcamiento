from django.test import TestCase

from django.urls import reverse
from apps.usuarios.models import Usuarios
from .models import Espacio, Localizacion

# Create your tests here.

# Ejecutar con python manage.py test apps.espacios -v 2
# O python manage.py test apps.espacios


class EspaciosTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuarios.objects.create(
            nombre='Admin',
            apellidos='Pruebas',
            email='admin@espacios.test',
            login='admin_espacios',
            password='hash-de-prueba',
            nivel_acceso=2,
            activo=True,
        )
        cls.basico = Usuarios.objects.create(
            nombre='Basico',
            apellidos='Pruebas',
            email='basico@espacios.test',
            login='basico_espacios',
            password='hash-de-prueba',
            nivel_acceso=1,
            activo=True,
        )
        cls.inactivo = Usuarios.objects.create(
            nombre='Inactivo',
            apellidos='Pruebas',
            email='inactivo@espacios.test',
            login='inactivo_espacios',
            password='hash-de-prueba',
            nivel_acceso=2,
            activo=False,
        )

    def setUp(self):
        self.espacio = Espacio.objects.create(
            nombre='Plaza A-1',
            ubicacion='Planta 1',
            descripcion='Espacio de prueba',
        )
        Localizacion.objects.get_or_create(
            pk=1,
            defaults={'nombre': 'Localización sin configurar'},
        )

    def iniciar_sesion(self, usuario):
        session = self.client.session
        session['usuario_id'] = usuario.pk
        session['usuario_login'] = usuario.login
        session['usuario_nivel'] = usuario.nivel_acceso
        session.save()


class EspaciosAccesoTest(EspaciosTestMixin, TestCase):
    def test_sin_sesion_lista_redirige_a_login(self):
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertRedirects(respuesta, reverse('usuarios:login'))

    def test_usuario_inactivo_lista_redirige_a_login(self):
        self.iniciar_sesion(self.inactivo)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertRedirects(respuesta, reverse('usuarios:login'))

    def test_basico_ve_el_listado(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Plaza A-1')

    def test_basico_no_ve_botones_de_escritura(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertNotContains(respuesta, 'Nuevo Espacio')
        self.assertNotContains(
            respuesta, reverse('espacios:editar', args=[self.espacio.pk])
        )
        self.assertNotContains(
            respuesta, reverse('espacios:eliminar', args=[self.espacio.pk])
        )

    def test_basico_no_ve_enlace_crear_en_sidebar(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertNotContains(respuesta, reverse('espacios:crear'))

    def test_admin_ve_enlace_crear_en_sidebar(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertContains(respuesta, reverse('espacios:crear'))

    def test_basico_no_puede_crear(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('espacios:crear'))
        self.assertRedirects(respuesta, reverse('dashboard'))
        self.assertEqual(Espacio.objects.count(), 1)

    def test_basico_no_puede_editar_espacio(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(
            reverse('espacios:editar', args=[self.espacio.pk])
        )
        self.assertRedirects(respuesta, reverse('dashboard'))

    def test_basico_no_puede_eliminar_espacio(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.post(
            reverse('espacios:eliminar', args=[self.espacio.pk])
        )
        self.assertRedirects(respuesta, reverse('dashboard'))
        self.assertTrue(Espacio.objects.filter(pk=self.espacio.pk).exists())

    def test_basico_no_puede_editar_localizacion(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.post(
            reverse('espacios:localizacion'),
            {'nombre': 'Cambiada', 'descripcion': ''},
        )
        self.assertRedirects(respuesta, reverse('dashboard'))
        self.assertEqual(
            Localizacion.objects.get(pk=1).nombre,
            'Localización sin configurar',
        )


class EspaciosCrudTest(EspaciosTestMixin, TestCase):
    def test_admin_crea_espacio(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('espacios:crear'),
            {'nombre': 'Plaza B-2', 'ubicacion': 'Planta 2', 'descripcion': ''},
        )
        self.assertRedirects(respuesta, reverse('espacios:lista'))
        self.assertTrue(Espacio.objects.filter(nombre='Plaza B-2').exists())

    def test_admin_actualiza_espacio(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('espacios:editar', args=[self.espacio.pk]),
            {
                'nombre': 'Plaza A-1',
                'ubicacion': 'Sotano',
                'descripcion': 'Actualizado',
            },
        )
        self.assertRedirects(respuesta, reverse('espacios:lista'))
        self.espacio.refresh_from_db()
        self.assertEqual(self.espacio.ubicacion, 'Sotano')

    def test_admin_elimina_espacio(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('espacios:eliminar', args=[self.espacio.pk])
        )
        self.assertRedirects(respuesta, reverse('espacios:lista'))
        self.assertFalse(Espacio.objects.filter(pk=self.espacio.pk).exists())

    def test_eliminar_rechaza_get(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(
            reverse('espacios:eliminar', args=[self.espacio.pk])
        )
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Espacio.objects.filter(pk=self.espacio.pk).exists())

    def test_localizacion_rechaza_get(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:localizacion'))
        self.assertEqual(respuesta.status_code, 405)

    def test_nombre_duplicado_es_invalido(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('espacios:crear'),
            {'nombre': 'Plaza A-1', 'ubicacion': '', 'descripcion': ''},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Espacio.objects.count(), 1)

    def test_admin_actualiza_localizacion(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('espacios:localizacion'),
            {'nombre': 'Aparcamiento UBU', 'descripcion': 'Campus principal'},
        )
        self.assertRedirects(respuesta, reverse('espacios:lista'))
        self.assertEqual(
            Localizacion.objects.get(pk=1).nombre, 'Aparcamiento UBU'
        )


class EspaciosListadoTest(EspaciosTestMixin, TestCase):
    def test_vista_por_defecto_es_lista(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertEqual(respuesta.context['vista'], 'list')

    def test_vista_grid(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:lista'), {'view': 'grid'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['vista'], 'grid')

    def test_vista_invalida_cae_a_lista(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(
            reverse('espacios:lista'), {'view': 'invalida'}
        )
        self.assertEqual(respuesta.context['vista'], 'list')

    def test_estadisticas_de_ubicacion(self):
        Espacio.objects.create(nombre='Plaza B-2', ubicacion='Planta 2')
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertEqual(respuesta.context['total'], 2)
        self.assertEqual(respuesta.context['con_ubicacion'], 2)
        self.assertEqual(respuesta.context['sin_ubicacion'], 0)

    def test_espacio_sin_ubicacion_cuenta_como_sin_ubicacion(self):
        self.espacio.ubicacion = ''
        self.espacio.save()
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertEqual(respuesta.context['con_ubicacion'], 0)
        self.assertEqual(respuesta.context['sin_ubicacion'], 1)
        
    def test_localizacion_ausente_se_recrea_solo(self):
        Localizacion.objects.all().delete()
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('espacios:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Localizacion.objects.filter(pk=1).exists())
        self.assertEqual(
            respuesta.context['localizacion'].nombre,
            'Localización sin configurar',
        )


class DashboardAccesoTest(EspaciosTestMixin, TestCase):
    def test_dashboard_requiere_sesion(self):
        respuesta = self.client.get(reverse('dashboard'))
        self.assertRedirects(respuesta, reverse('usuarios:login'))

    def test_basico_ve_el_dashboard(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Espacios')

    def test_admin_ve_el_dashboard(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)

