"""Repositorios concretos con Django ORM para usuarios."""

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario
from apps.compartido.infrastructure.mapeo import a_texto, uuid_valido
from apps.usuarios.domain.repositorios import (
    RepositorioIntentoLogin,
    RepositorioPermiso,
    RepositorioRol,
    RepositorioSesion,
    RepositorioUsuario,
)
from apps.usuarios.domain.usuario import IntentoLogin, Permiso, Rol, Sesion, Usuario
from apps.usuarios.infrastructure.models import (
    IntentoLoginModel,
    PermisoModel,
    RolModel,
    RolPermisoModel,
    SesionModel,
    UsuarioModel,
)


def _sin_ip(ip: str | None) -> str:
    """La columna guarda `NULL` cuando no hay IP; el dominio espera texto."""
    return ip or ""


def _permiso_from_model(model: PermisoModel) -> Permiso:
    return Permiso(
        id=str(model.id),
        codigo=model.codigo,
        descripcion=model.descripcion,
        modulo=model.modulo,
    )


def _rol_from_model(model: RolModel) -> Rol:
    return Rol(
        id=str(model.id),
        nombre=model.nombre,
        descripcion=model.descripcion,
        permisos=[_permiso_from_model(permiso) for permiso in model.permisos.all()],
    )


def _usuario_from_model(model: UsuarioModel) -> Usuario:
    rol = _rol_from_model(model.rol)
    return Usuario(
        id=str(model.id),
        nombre=model.nombre,
        email=model.email,
        username=model.username,
        rol=rol,
        estado=EstadoUsuario(model.estado),
        creado_por=a_texto(model.creado_por_id),
        fecha_creacion=model.fecha_creacion,
    )


def _sesion_from_model(model: SesionModel) -> Sesion:
    return Sesion(
        id=str(model.id),
        usuario_id=str(model.usuario_id),
        token=model.token,
        fecha_inicio=model.fecha_inicio,
        fecha_expiracion=model.fecha_expiracion,
        ip=_sin_ip(model.ip),
        estado=EstadoSesion(model.estado),
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
        model.creado_por_id = usuario.creado_por
        model.save()

    def buscar_por_id(self, usuario_id: str) -> Usuario | None:
        if uuid_valido(usuario_id) is None:
            return None
        model = self._con_rol().filter(id=usuario_id).first()
        return _usuario_from_model(model) if model else None

    def buscar_por_email(self, email: str) -> Usuario | None:
        model = self._con_rol().filter(email__iexact=email).first()
        return _usuario_from_model(model) if model else None

    def buscar_por_username(self, username: str) -> Usuario | None:
        model = self._con_rol().filter(username__iexact=username).first()
        return _usuario_from_model(model) if model else None

    def set_password(self, usuario_id: str, password_hash: str) -> None:
        UsuarioModel.objects.filter(id=usuario_id).update(password_hash=password_hash)

    def get_password(self, username: str) -> str:
        model = UsuarioModel.objects.filter(username__iexact=username).first()
        return model.password_hash if model else ""

    def get_password_por_id(self, usuario_id: str) -> str:
        if uuid_valido(usuario_id) is None:
            return ""
        model = UsuarioModel.objects.filter(id=usuario_id).first()
        return model.password_hash if model else ""

    def listar(self) -> list[Usuario]:
        modelos = self._con_rol().order_by("nombre")
        return [_usuario_from_model(model) for model in modelos]

    @staticmethod
    def _con_rol():
        """Evita una consulta por usuario al reconstruir su rol y permisos."""
        return UsuarioModel.objects.select_related("rol").prefetch_related(
            "rol__permisos"
        )


class DjangoRepositorioRol(RepositorioRol):
    def guardar(self, rol: Rol) -> None:
        model = RolModel.objects.filter(id=rol.id).first()
        if model is None:
            model = RolModel(id=rol.id)
        model.nombre = rol.nombre
        model.descripcion = rol.descripcion
        model.save()
        self._sincronizar_permisos(model, rol.permisos)

    def buscar_por_id(self, rol_id: str) -> Rol | None:
        if uuid_valido(rol_id) is None:
            return None
        model = self._con_permisos().filter(id=rol_id).first()
        return _rol_from_model(model) if model else None

    def buscar_por_nombre(self, nombre: str) -> Rol | None:
        model = self._con_permisos().filter(nombre__iexact=nombre).first()
        return _rol_from_model(model) if model else None

    def listar(self) -> list[Rol]:
        modelos = self._con_permisos().order_by("nombre")
        return [_rol_from_model(model) for model in modelos]

    @staticmethod
    def _con_permisos():
        return RolModel.objects.prefetch_related("permisos")

    @staticmethod
    def _sincronizar_permisos(model: RolModel, permisos: list[Permiso]) -> None:
        """Refleja en `roles_permisos` la lista de permisos del agregado."""
        identificadores = [permiso.id for permiso in permisos]
        RolPermisoModel.objects.filter(rol=model).exclude(
            permiso_id__in=identificadores
        ).delete()
        for permiso_id in identificadores:
            RolPermisoModel.objects.get_or_create(rol=model, permiso_id=permiso_id)


class DjangoRepositorioPermiso(RepositorioPermiso):
    def guardar(self, permiso: Permiso) -> None:
        PermisoModel.objects.update_or_create(
            id=permiso.id,
            defaults={
                "codigo": permiso.codigo,
                "descripcion": permiso.descripcion,
                "modulo": permiso.modulo,
            },
        )

    def buscar_por_codigo(self, codigo: str) -> Permiso | None:
        model = PermisoModel.objects.filter(codigo__iexact=codigo).first()
        return _permiso_from_model(model) if model else None

    def listar(self) -> list[Permiso]:
        modelos = PermisoModel.objects.order_by("modulo", "codigo")
        return [_permiso_from_model(model) for model in modelos]

    def listar_por_rol(self, rol_id: str) -> list[Permiso]:
        if uuid_valido(rol_id) is None:
            return []
        modelos = PermisoModel.objects.filter(roles__id=rol_id).order_by("codigo")
        return [_permiso_from_model(model) for model in modelos]


class DjangoRepositorioSesion(RepositorioSesion):
    def guardar(self, sesion: Sesion) -> None:
        model = SesionModel.objects.filter(id=sesion.id).first()
        if model is None:
            model = SesionModel(id=sesion.id)
        model.usuario_id = sesion.usuario_id
        model.token = sesion.token
        model.fecha_expiracion = sesion.fecha_expiracion
        model.ip = sesion.ip or None
        model.estado = sesion.estado.value
        model.save()

    def buscar_por_token(self, token: str) -> Sesion | None:
        model = SesionModel.objects.filter(token=token).first()
        return _sesion_from_model(model) if model else None

    def cerrar_por_token(self, token: str) -> None:
        SesionModel.objects.filter(token=token).update(
            estado=EstadoSesion.CERRADA.value
        )

    def cerrar_por_usuario(self, usuario_id: str, excepto_token: str = "") -> None:
        sesiones = SesionModel.objects.filter(
            usuario_id=usuario_id,
            estado=EstadoSesion.ACTIVA.value,
        )
        if excepto_token:
            sesiones = sesiones.exclude(token=excepto_token)
        sesiones.update(estado=EstadoSesion.CERRADA.value)


class DjangoRepositorioIntentoLogin(RepositorioIntentoLogin):
    def guardar(self, intento: IntentoLogin) -> None:
        IntentoLoginModel.objects.create(
            id=intento.id,
            username=intento.username,
            ip=intento.ip or None,
            exitoso=intento.exitoso,
            motivo_fallo=intento.motivo_fallo,
        )
