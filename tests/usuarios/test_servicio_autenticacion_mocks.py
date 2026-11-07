"""Suite de servicio: ServicioAutenticacion y ServicioGestionUsuarios con mocks.

Los tres repositorios se reemplazan con `create_autospec`. El hasher de Django
se cambia por MD5 solo en la prueba (fixture `hasher_rapido`) para que los
casos sean instantaneos; la logica del servicio no cambia.
"""

from unittest.mock import ANY, create_autospec

import pytest
from django.contrib.auth.hashers import make_password

from apps.compartido.domain.enums import EstadoUsuario, ResultadoLogin
from apps.usuarios.application.services import (
    ServicioAutenticacion,
    ServicioGestionUsuarios,
)
from apps.usuarios.domain.exceptions import (
    CredencialesInvalidasError,
    RecursoDuplicadoError,
    UsuarioInactivoError,
)
from apps.usuarios.domain.repositorios import (
    RepositorioIntentoLogin,
    RepositorioRol,
    RepositorioSesion,
    RepositorioUsuario,
)
from apps.usuarios.domain.usuario import Rol, UsuarioSistemaFabrica

PASSWORD = "Clave-Segura-2026"


@pytest.fixture(autouse=True)
def hasher_rapido(settings) -> None:
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


class TestServicioAutenticacionConMocks:
    def setup_method(self) -> None:
        self.repo_usuario = create_autospec(RepositorioUsuario, instance=True)
        self.repo_sesion = create_autospec(RepositorioSesion, instance=True)
        self.repo_intentos = create_autospec(RepositorioIntentoLogin, instance=True)
        self.servicio = ServicioAutenticacion(
            self.repo_usuario, self.repo_sesion, self.repo_intentos
        )
        self.usuario = UsuarioSistemaFabrica.crear(
            "Ana", "ana@textil.pe", "ana", Rol(id="r-1", nombre="Cliente")
        )

    def _intento_registrado(self):
        self.repo_intentos.guardar.assert_called_once()
        return self.repo_intentos.guardar.call_args.args[0]

    def test_login_exitoso_crea_sesion_y_registra_intento(self) -> None:
        self.repo_usuario.buscar_por_username.return_value = self.usuario
        self.repo_usuario.get_password.return_value = make_password(PASSWORD)

        resultado = self.servicio.login("  ana ", PASSWORD, ip="10.0.0.1")

        assert resultado["usuario_id"] == self.usuario.id
        assert resultado["rol"] == "Cliente"
        self.repo_usuario.buscar_por_username.assert_called_once_with("ana")
        self.repo_sesion.guardar.assert_called_once_with(ANY)
        sesion = self.repo_sesion.guardar.call_args.args[0]
        assert sesion.token == resultado["token"]
        assert self._intento_registrado().exitoso is True

    def test_password_incorrecto_no_crea_sesion(self) -> None:
        self.repo_usuario.buscar_por_username.return_value = self.usuario
        self.repo_usuario.get_password.return_value = make_password(PASSWORD)

        with pytest.raises(CredencialesInvalidasError):
            self.servicio.login("ana", "otra-clave")

        self.repo_sesion.guardar.assert_not_called()
        intento = self._intento_registrado()
        assert intento.exitoso is False
        assert intento.motivo_fallo == ResultadoLogin.CREDENCIALES_INVALIDAS.value

    def test_usuario_inexistente_es_credencial_invalida(self) -> None:
        self.repo_usuario.buscar_por_username.return_value = None
        self.repo_usuario.get_password.return_value = ""

        with pytest.raises(CredencialesInvalidasError):
            self.servicio.login("nadie", PASSWORD)

        self.repo_sesion.guardar.assert_not_called()

    def test_usuario_inactivo_no_inicia_sesion(self) -> None:
        self.usuario.estado = EstadoUsuario.INACTIVO
        self.repo_usuario.buscar_por_username.return_value = self.usuario
        self.repo_usuario.get_password.return_value = make_password(PASSWORD)

        with pytest.raises(UsuarioInactivoError):
            self.servicio.login("ana", PASSWORD)

        self.repo_sesion.guardar.assert_not_called()
        assert (
            self._intento_registrado().motivo_fallo
            == ResultadoLogin.USUARIO_INACTIVO.value
        )

    def test_cerrar_otras_sesiones_delega_en_repositorio(self) -> None:
        self.servicio.cerrar_otras_sesiones("u-1", "token-actual")
        self.repo_sesion.cerrar_por_usuario.assert_called_once_with(
            "u-1", excepto_token="token-actual"
        )


class TestServicioGestionUsuariosConMocks:
    def setup_method(self) -> None:
        self.repo_usuario = create_autospec(RepositorioUsuario, instance=True)
        self.repo_rol = create_autospec(RepositorioRol, instance=True)
        self.servicio = ServicioGestionUsuarios(self.repo_usuario, self.repo_rol)
        self.repo_rol.buscar_por_id.return_value = Rol(id="r-1", nombre="Cliente")

    def test_crear_usuario_normaliza_y_guarda_hash(self) -> None:
        self.repo_usuario.buscar_por_email.return_value = None
        self.repo_usuario.buscar_por_username.return_value = None

        usuario = self.servicio.crear_usuario(
            " Ana ", " ANA@Textil.pe ", "r-1", " Ana ", PASSWORD
        )

        assert (usuario.email, usuario.username) == ("ana@textil.pe", "ana")
        self.repo_usuario.guardar.assert_called_once_with(usuario)
        usuario_id, password_hash = self.repo_usuario.set_password.call_args.args
        assert usuario_id == usuario.id
        assert password_hash != PASSWORD

    def test_email_duplicado_no_guarda(self) -> None:
        self.repo_usuario.buscar_por_email.return_value = UsuarioSistemaFabrica.crear(
            "Otra", "ana@textil.pe", "otra", Rol(id="r-1", nombre="Cliente")
        )

        with pytest.raises(RecursoDuplicadoError):
            self.servicio.crear_usuario("Ana", "ana@textil.pe", "r-1", "ana", PASSWORD)

        self.repo_usuario.guardar.assert_not_called()
        self.repo_usuario.set_password.assert_not_called()
