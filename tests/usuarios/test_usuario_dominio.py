"""Suite de dominio: Usuario, Rol y Sesion (Lab 05).

Pruebas unitarias puras sobre las entidades del contexto de usuarios.
`setup_method` crea un rol y un usuario nuevos antes de cada caso.
"""

from datetime import UTC, datetime, timedelta

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario
from apps.usuarios.domain.usuario import Permiso, Rol, Sesion, UsuarioSistemaFabrica

AHORA = datetime(2026, 11, 6, 10, 0, tzinfo=UTC)


class TestUsuarioDominio:
    def setup_method(self) -> None:
        self.rol = Rol(id="rol-1", nombre="Cliente")
        self.usuario = UsuarioSistemaFabrica.crear(
            nombre="Ana Torres",
            email="ana@textil.pe",
            username="ana",
            rol=self.rol,
        )

    def teardown_method(self) -> None:
        self.usuario = None

    def test_fabrica_crea_usuario_activo_con_id(self) -> None:
        assert self.usuario.id
        assert self.usuario.estado == EstadoUsuario.ACTIVO
        assert self.usuario.rol is self.rol

    def test_desactivar_y_reactivar_usuario(self) -> None:
        self.usuario.desactivar()
        assert self.usuario.estado == EstadoUsuario.INACTIVO
        self.usuario.activar()
        assert self.usuario.estado == EstadoUsuario.ACTIVO

    def test_actualizar_perfil_normaliza_nombre_y_email(self) -> None:
        self.usuario.actualizar_perfil("  Ana María  ", "  ANA.Maria@Textil.PE ")
        assert self.usuario.nombre == "Ana María"
        assert self.usuario.email == "ana.maria@textil.pe"

    def test_asignar_rol_reemplaza_el_anterior(self) -> None:
        admin = Rol(id="rol-2", nombre="Administrador")
        self.usuario.asignar_rol(admin)
        assert self.usuario.rol.nombre == "Administrador"

    def test_rol_no_duplica_permisos(self) -> None:
        permiso = Permiso("p-1", "ver_catalogo", "Ver catalogo", "catalogo")
        self.rol.asignar_permiso(permiso)
        self.rol.asignar_permiso(permiso)
        assert self.rol.permisos == [permiso]


class TestSesionDominio:
    def setup_method(self) -> None:
        self.sesion = Sesion(
            id="s-1",
            usuario_id="u-1",
            token="tkn",
            fecha_inicio=AHORA,
            fecha_expiracion=AHORA + timedelta(hours=8),
            ip="127.0.0.1",
        )

    def test_sesion_activa_antes_de_expirar(self) -> None:
        assert self.sesion.esta_activa(AHORA + timedelta(hours=7, minutes=59))

    def test_sesion_no_activa_en_el_instante_de_expiracion(self) -> None:
        assert not self.sesion.esta_activa(AHORA + timedelta(hours=8))

    def test_sesion_cerrada_no_esta_activa(self) -> None:
        self.sesion.cerrar()
        assert self.sesion.estado == EstadoSesion.CERRADA
        assert not self.sesion.esta_activa(AHORA)
