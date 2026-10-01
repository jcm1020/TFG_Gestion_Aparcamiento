from django.test import TestCase

# Create your tests here.

from django.test import TestCase

from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password

from .models import Usuarios
from .forms import UsuariosForm

# Create your tests here.

# Ejecutar con python manage.py test apps.usuarios -v 2
# O python manage.py test apps.usuarios


class UsuariosTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.admin = Usuarios.objects.create(
            nombre='Admin',
            apellidos='Pruebas',
            email='admin@usuarios.test',
            login='admin_usuarios',
            password='hash-de-prueba',
            nivel_acceso=2,
            activo=True,
        )
        cls.basico = Usuarios.objects.create(
            nombre='Basico',
            apellidos='Pruebas',
            email='basico@usuarios.test',
            login='basico_usuarios',
            password='hash-de-prueba',
            nivel_acceso=1,
            activo=True,
        )
        cls.inactivo = Usuarios.objects.create(
            nombre='Inactivo',
            apellidos='Pruebas',
            email='inactivo@usuarios.test',
            login='inactivo_usuarios',
            password='hash-de-prueba',
            nivel_acceso=2,
            activo=False,
        )

    def iniciar_sesion(self, usuario):
        session = self.client.session
        session['usuario_id'] = usuario.pk
        session['usuario_login'] = usuario.login
        session['usuario_nivel'] = usuario.nivel_acceso
        session.save()

    def datos_alta(self, **sobrescribir):
        datos = {
            'nombre': 'Pepe',
            'apellidos': 'Guzman',
            'email': 'pepe@usuarios.test',
            'telefono': '+341234567',
            'direccion': 'C/ Cespedes de Guzman',
            'login': 'pepe',
            'nueva_password': 'Secreto123',
            'confirmar_password': 'Secreto123',
            'nivel_acceso': '2',
            'comentarios': 'Este es Pepe',
        }
        datos.update(sobrescribir)
        return datos


class UsuariosAltaTest(UsuariosTestMixin, TestCase):
    def test_admin_crea_usuario(self):
        # Este test es en el que se detecto el bug de la vista crear_usuario:
        # la llamada al formulario estaba comentada, asi que 'usuario' nunca
        # existia y la siguiente linea (usuario.save()) hacia NameError.
        # El cliente de test de Django relanza la excepcion, por eso aqui falla.
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(reverse('usuarios:crear'), self.datos_alta())

        self.assertRedirects(respuesta, reverse('usuarios:lista'))
        self.assertTrue(Usuarios.objects.filter(login='pepe').exists())

        creado = Usuarios.objects.get(login='pepe')
        self.assertEqual(creado.email, 'pepe@usuarios.test')
        self.assertEqual(creado.nivel_acceso, 2)

    def test_contrasena_se_guarda_hasheada(self):
        self.iniciar_sesion(self.admin)
        self.client.post(reverse('usuarios:crear'), self.datos_alta())

        creado = Usuarios.objects.get(login='pepe')

        # Nunca en texto plano: debe ser un hash y ademas debe validar.
        self.assertNotEqual(creado.password, 'Secreto123')
        self.assertTrue(creado.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(check_password('Secreto123', creado.password))

    def test_nuevo_usuario_nace_inactivo_aunque_el_post_lo_pida(self):
        # El save() del formulario fuerza activo=False en toda alta, por mucho
        # que el POST mande el checkbox marcado.
        self.iniciar_sesion(self.admin)
        self.client.post(reverse('usuarios:crear'), self.datos_alta(activo='on'))

        self.assertFalse(Usuarios.objects.get(login='pepe').activo)

    def test_password_no_es_campo_del_formulario(self):
        # Si 'password' volviera a 'fields', el formulario pediria el hash por
        # pantalla y el usuario tendria que teclear una cadena ilegible.
        campos = UsuariosForm().fields
        self.assertNotIn('password', campos)
        self.assertIn('nueva_password', campos)
        self.assertIn('confirmar_password', campos)

    def test_alta_sin_contrasena_es_invalida(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:crear'),
            self.datos_alta(nueva_password='', confirmar_password=''),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuarios.objects.filter(login='pepe').exists())
        self.assertIn('nueva_password', respuesta.context['form'].errors)

    def test_alta_con_confirmacion_distinta_es_invalida(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:crear'),
            self.datos_alta(confirmar_password='OtraCosa'),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuarios.objects.filter(login='pepe').exists())
        self.assertIn('confirmar_password', respuesta.context['form'].errors)

    def test_alta_con_confirmacion_correcta_es_valida(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:crear'),
            self.datos_alta(nueva_password='Secreto123', confirmar_password='Secreto123'),
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Usuarios.objects.filter(login='pepe').exists())

    def test_email_duplicado_es_invalido(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:crear'),
            self.datos_alta(email='admin@usuarios.test'),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuarios.objects.filter(login='pepe').exists())
        self.assertIn('email', respuesta.context['form'].errors)

    def test_login_duplicado_es_invalido(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:crear'),
            self.datos_alta(login='admin_usuarios'),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuarios.objects.filter(nombre='Pepe').exists())
        self.assertIn('login', respuesta.context['form'].errors)


class UsuariosAccesoTest(UsuariosTestMixin, TestCase):
    def test_sin_sesion_lista_redirige_a_login(self):
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertRedirects(respuesta, reverse('usuarios:login'))

    def test_usuario_inactivo_lista_redirige_a_login(self):
        self.iniciar_sesion(self.inactivo)
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertRedirects(respuesta, reverse('usuarios:login'))

    def test_basico_no_puede_crear(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.post(reverse('usuarios:crear'), self.datos_alta())

        self.assertRedirects(respuesta, reverse('dashboard'))
        self.assertFalse(Usuarios.objects.filter(login='pepe').exists())

    def test_basico_no_puede_editar(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.post(
            reverse('usuarios:editar', args=[self.basico.pk]),
            self.datos_alta(nombre='Intruso'),
        )

        self.assertRedirects(respuesta, reverse('dashboard'))
        self.basico.refresh_from_db()
        self.assertEqual(self.basico.nombre, 'Basico')

    def test_basico_no_puede_eliminar(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.post(
            reverse('usuarios:eliminar', args=[self.admin.pk])
        )

        self.assertRedirects(respuesta, reverse('dashboard'))
        self.assertTrue(Usuarios.objects.filter(pk=self.admin.pk).exists())

    def test_basico_no_cede_lista(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertEqual(respuesta.status_code, 200)

    def test_nivel_se_refresca_en_cada_peticion(self):
        # actualizar_sesion() relee el nivel desde la base de datos en cada
        # peticion protegida, asi que degradar a un usuario surte efecto
        # inmediatamente, sin esperar a que cierre sesion.
        self.iniciar_sesion(self.basico)
        self.assertEqual(self.client.session['usuario_nivel'], 1)

        Usuarios.objects.filter(pk=self.basico.pk).update(nivel_acceso=2)

        respuesta = self.client.get(reverse('usuarios:crear'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.client.session['usuario_nivel'], 2)


class UsuariosCrudTest(UsuariosTestMixin, TestCase):
    def test_admin_actualiza_usuario(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:editar', args=[self.basico.pk]),
            self.datos_alta(
                nombre='Actualizado',
                email='actualizado@usuarios.test',
                login='basico_usuarios',
                nueva_password='',
                confirmar_password='',
                nivel_acceso='1',
            ),
        )

        self.assertRedirects(respuesta, reverse('usuarios:lista'))
        self.basico.refresh_from_db()
        self.assertEqual(self.basico.nombre, 'Actualizado')
        self.assertEqual(self.basico.email, 'actualizado@usuarios.test')

    def test_editar_sin_contrasena_conserva_el_hash(self):
        # Con nueva_password vacia el save() del formulario NO debe tocar el hash existente. 
        # Si se tocara, la cuenta se quedaria sin contraseña y el usuario no podria volver a entrar.
        self.iniciar_sesion(self.admin)
        hash_antes = self.basico.password

        self.client.post(
            reverse('usuarios:editar', args=[self.basico.pk]),
            self.datos_alta(
                nombre='Cambiado',
                email='basico@usuarios.test',
                login='basico_usuarios',
                nueva_password='',
                confirmar_password='',
                nivel_acceso='1',
            ),
        )

        self.basico.refresh_from_db()
        self.assertEqual(self.basico.password, hash_antes)
        self.assertNotEqual(self.basico.password, '')

    def test_editar_con_contrasena_nueva_rehashea(self):
        self.iniciar_sesion(self.admin)
        hash_antes = self.basico.password

        self.client.post(
            reverse('usuarios:editar', args=[self.basico.pk]),
            self.datos_alta(
                nombre='Basico',
                email='basico@usuarios.test',
                login='basico_usuarios',
                nueva_password='NuevaClave456',
                confirmar_password='NuevaClave456',
                nivel_acceso='1',
            ),
        )

        self.basico.refresh_from_db()
        self.assertNotEqual(self.basico.password, hash_antes)
        self.assertTrue(check_password('NuevaClave456', self.basico.password))

    def test_editar_con_confirmacion_distinta_es_invalido(self):
        self.iniciar_sesion(self.admin)
        hash_antes = self.basico.password

        respuesta = self.client.post(
            reverse('usuarios:editar', args=[self.basico.pk]),
            self.datos_alta(
                nueva_password='Secreto123',
                confirmar_password='OtraCosa',
                nivel_acceso='1',
            ),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.basico.refresh_from_db()
        self.assertEqual(self.basico.password, hash_antes)

    def test_admin_activa_el_usuario_desde_el_formulario(self):
        # El campo activo si esta en el formulario, y eso es intencionado:
        # es la via por la que un administrador reactiva una cuenta creada
        # desde el alta (que siempre nace inactiva).
        self.inactivo.activo = False
        self.inactivo.save()

        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:editar', args=[self.inactivo.pk]),
            self.datos_alta(
                nombre='Inactivo',
                email='inactivo@usuarios.test',
                login='inactivo_usuarios',
                nueva_password='',
                confirmar_password='',
                nivel_acceso='2',
                activo='on',
            ),
        )

        self.assertRedirects(respuesta, reverse('usuarios:lista'))
        self.inactivo.refresh_from_db()
        self.assertTrue(self.inactivo.activo)

    def test_admin_elimina_usuario(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.post(
            reverse('usuarios:eliminar', args=[self.basico.pk])
        )

        self.assertRedirects(respuesta, reverse('usuarios:lista'))
        self.assertFalse(Usuarios.objects.filter(pk=self.basico.pk).exists())

    def test_eliminar_rechaza_get(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(
            reverse('usuarios:eliminar', args=[self.basico.pk])
        )

        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Usuarios.objects.filter(pk=self.basico.pk).exists())


# Sin UsuariosTestMixin a proposito: registro_view asigna nivel 2 solo cuando
# Usuarios.objects.count() == 0, y el mixin crea tres usuarios en# setUpTestData, lo que haria imposible probar ese caso.
class UsuariosRegistroTest(TestCase):
    def datos_registro(self, **sobrescribir):
        datos = {
            'nombre': 'Nuevo',
            'apellidos': 'Alta',
            'email': 'nuevo@usuarios.test',
            'telefono': '',
            'login': 'nuevo',
            'password1': 'Secreto123',
            'password2': 'Secreto123',
        }
        datos.update(sobrescribir)
        return datos

    def test_primer_usuario_registrado_es_administrador(self):
        self.assertEqual(Usuarios.objects.count(), 0)

        respuesta = self.client.post(
            reverse('usuarios:registro'), self.datos_registro()
        )

        self.assertRedirects(respuesta, reverse('usuarios:login'))
        self.assertEqual(Usuarios.objects.get(login='nuevo').nivel_acceso, 2)

    def test_usuarios_siguientes_registran_como_basicos(self):
        Usuarios.objects.create(
            nombre='Primero',
            email='primero@usuarios.test',
            login='primero',
            password='hash',
            nivel_acceso=2,
            activo=True,
        )

        self.client.post(reverse('usuarios:registro'), self.datos_registro())

        self.assertEqual(Usuarios.objects.get(login='nuevo').nivel_acceso, 1)

    def test_usuario_registrado_nace_inactivo(self):
        self.client.post(reverse('usuarios:registro'), self.datos_registro())
        self.assertFalse(Usuarios.objects.get(login='nuevo').activo)

    def test_contrasena_registrada_se_hashea(self):
        self.client.post(reverse('usuarios:registro'), self.datos_registro())

        creado = Usuarios.objects.get(login='nuevo')
        self.assertNotEqual(creado.password, 'Secreto123')
        self.assertTrue(check_password('Secreto123', creado.password))

    def test_registro_con_contrasenas_distintas_es_invalido(self):
        respuesta = self.client.post(
            reverse('usuarios:registro'),
            self.datos_registro(password2='OtraCosa'),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Usuarios.objects.filter(login='nuevo').exists())
        self.assertIn('password2', respuesta.context['form'].errors)

    def test_registro_con_email_duplicado_es_invalido(self):
        Usuarios.objects.create(
            nombre='Existente',
            email='nuevo@usuarios.test',
            login='otro',
            password='hash',
            nivel_acceso=2,
            activo=True,
        )

        respuesta = self.client.post(
            reverse('usuarios:registro'), self.datos_registro()
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('email', respuesta.context['form'].errors)

    def test_registro_con_login_duplicado_es_invalido(self):
        Usuarios.objects.create(
            nombre='Existente',
            email='otro@usuarios.test',
            login='nuevo',
            password='hash',
            nivel_acceso=2,
            activo=True,
        )

        respuesta = self.client.post(
            reverse('usuarios:registro'), self.datos_registro()
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('login', respuesta.context['form'].errors)


class UsuariosLoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Hash real: check_password lo necesita para validar de verdad.
        cls.admin = Usuarios.objects.create(
            nombre='Admin',
            email='admin@login.test',
            login='admin_login',
            password=make_password('Secreto123'),
            nivel_acceso=2,
            activo=True,
        )
        cls.inactivo = Usuarios.objects.create(
            nombre='Inactivo',
            email='inactivo@login.test',
            login='inactivo_login',
            password=make_password('Secreto123'),
            nivel_acceso=2,
            activo=False,
        )

    def test_login_correcto_crea_la_sesion(self):
        respuesta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'admin_login', 'password': 'Secreto123'},
        )

        self.assertRedirects(respuesta, reverse('dashboard'))
        self.assertEqual(self.client.session['usuario_id'], self.admin.pk)
        self.assertEqual(self.client.session['usuario_nivel'], 2)

    def test_login_con_contrasena_incorrecta_falla(self):
        respuesta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'admin_login', 'password': 'Incorrecta999'},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_de_usuario_inactivo_falla(self):
        # login_view exige 'check_password(...) and usuario.activo'.
        respuesta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'inactivo_login', 'password': 'Secreto123'},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_con_usuario_inexistente_falla(self):
        respuesta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'nadie', 'password': 'Secreto123'},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_vacio_es_invalido(self):
        respuesta = self.client.post(
            reverse('usuarios:login'), {'username': '', 'password': ''}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn('usuario_id', self.client.session)

    def test_logout_vacia_la_sesion(self):
        session = self.client.session
        session['usuario_id'] = self.admin.pk
        session['usuario_login'] = self.admin.login
        session.save()

        respuesta = self.client.get(reverse('usuarios:logout'))

        self.assertRedirects(respuesta, reverse('usuarios:login'))
        self.assertNotIn('usuario_id', self.client.session)


# Estos 4 tests comprueban los controles de administrador {% if request.session.usuario_nivel == 2 %} de las plantillas.
class UsuariosContorlPlantillaTest(UsuariosTestMixin, TestCase):
    def test_basico_no_ve_el_boton_nuevo_usuario(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertNotContains(respuesta, reverse('usuarios:crear'))

    def test_admin_ve_el_boton_nuevo_usuario(self):
        self.iniciar_sesion(self.admin)
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertContains(respuesta, reverse('usuarios:crear'))

    def test_basico_no_ve_los_botones_editar_ni_eliminar(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertNotContains(respuesta, reverse('usuarios:editar', args=[self.admin.pk]))
        self.assertNotContains(respuesta, reverse('usuarios:eliminar', args=[self.admin.pk]))

    def test_basico_no_ve_crear_usuario_en_el_sidebar(self):
        self.iniciar_sesion(self.basico)
        respuesta = self.client.get(reverse('usuarios:lista'))
        self.assertNotContains(respuesta, 'Crear Usuario')
