"""Repositorios concretos con Django ORM para usuarios."""

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario
from apps.usuarios.domain.repositorios import (
    RepositorioIntentoLogin,
    RepositorioRol,
    RepositorioSesion,
    RepositorioUsuario,
)
from apps.usuarios.domain.usuario import IntentoLogin, Rol, Sesion, Usuario
from apps.usuarios.infrastructure.models import (
    IntentoLoginModel,
    RolModel,
    SesionModel,
    UsuarioModel,
)


def _rol_from_model(model: RolModel) -> Rol:
    return Rol(id=str(model.id), nombre=model.nombre, descripcion=model.descripcion)


def _usuario_from_model(model: UsuarioModel) -> Usuario:
    rol = _rol_from_model(model.rol)
    return Usuario(
        id=str(model.id),
        nombre=model.nombre,
        email=model.email,
        username=model.username,
        rol=rol,
        estado=EstadoUsuario(model.estado),
        creado_por=model.creado_por,
        fecha_creacion=model.fecha_creacion,
    )


class DjangoRepositorioUsuario(RepositorioUsuario):
    def guardar(self, usuario: Usuario) -> None:
        model = UsuarioModel.objects.filter(id=usuario.id).first()
        if model is None:
            model = UsuarioModel(id=usuario.id)
        model.nombre = usuario.nombre
        model.email = usuario.email
        model.username = usuario.username
        model.rol_id = usuario.rol.id
        model.estado = usuario.estado.value
        model.creado_por = usuario.creado_por
        model.save()

    def buscar_por_id(self, usuario_id: str) -> Usuario | None:
        model = UsuarioModel.objects.filter(id=usuario_id).first()
        return _usuario_from_model(model) if model else None

    def buscar_por_email(self, email: str) -> Usuario | None:
        model = UsuarioModel.objects.filter(email__iexact=email).first()
        return _usuario_from_model(model) if model else None

    def buscar_por_username(self, username: str) -> Usuario | None:
        model = UsuarioModel.objects.filter(username__iexact=username).first()
        return _usuario_from_model(model) if model else None

    def set_password(self, usuario_id: str, password_hash: str) -> None:
        UsuarioModel.objects.filter(id=usuario_id).update(password_hash=password_hash)

    def get_password(self, username: str) -> str:
        model = UsuarioModel.objects.filter(username__iexact=username).first()
        return model.password_hash if model else ""

    def get_password_por_id(self, usuario_id: str) -> str:
        model = UsuarioModel.objects.filter(id=usuario_id).first()
        return model.password_hash if model else ""

    def listar(self) -> list[Usuario]:
        modelos = UsuarioModel.objects.select_related("rol").order_by("nombre")
        return [_usuario_from_model(model) for model in modelos]


class DjangoRepositorioRol(RepositorioRol):
    def guardar(self, rol: Rol) -> None:
        model = RolModel.objects.filter(id=rol.id).first()
        if model is None:
            model = RolModel(id=rol.id)
        model.nombre = rol.nombre
        model.descripcion = rol.descripcion
        model.save()

    def buscar_por_id(self, rol_id: str) -> Rol | None:
        model = RolModel.objects.filter(id=rol_id).first()
        return _rol_from_model(model) if model else None

    def buscar_por_nombre(self, nombre: str) -> Rol | None:
        model = RolModel.objects.filter(nombre__iexact=nombre).first()
        return _rol_from_model(model) if model else None

    def listar(self) -> list[Rol]:
        return [_rol_from_model(model) for model in RolModel.objects.order_by("nombre")]


class DjangoRepositorioSesion(RepositorioSesion):
    def guardar(self, sesion: Sesion) -> None:
        model = SesionModel.objects.filter(id=sesion.id).first()
        if model is None:
            model = SesionModel(id=sesion.id)
        model.usuario_id = sesion.usuario_id
        model.token = sesion.token
        model.fecha_inicio = sesion.fecha_inicio
        model.fecha_expiracion = sesion.fecha_expiracion
        model.ip = sesion.ip
        model.estado = sesion.estado.value
        model.save()

    def buscar_por_token(self, token: str) -> Sesion | None:
        model = SesionModel.objects.filter(token=token).first()
        if not model:
            return None
        return Sesion(
            id=str(model.id),
            usuario_id=str(model.usuario_id),
            token=model.token,
            fecha_inicio=model.fecha_inicio,
            fecha_expiracion=model.fecha_expiracion,
            ip=model.ip,
            estado=EstadoSesion(model.estado),
        )

    def cerrar_por_token(self, token: str) -> None:
        SesionModel.objects.filter(token=token).update(estado="cerrada")

    def cerrar_por_usuario(self, usuario_id: str, excepto_token: str = "") -> None:
        sesiones = SesionModel.objects.filter(usuario_id=usuario_id, estado="activa")
        if excepto_token:
            sesiones = sesiones.exclude(token=excepto_token)
        sesiones.update(estado="cerrada")


class DjangoRepositorioIntentoLogin(RepositorioIntentoLogin):
    def guardar(self, intento: IntentoLogin) -> None:
        IntentoLoginModel.objects.create(
            id=intento.id,
            username=intento.username,
            fecha=intento.fecha,
            ip=intento.ip,
            exitoso=intento.exitoso,
            motivo_fallo=intento.motivo_fallo,
        )
