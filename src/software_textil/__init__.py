"""Aplicacion web SoftwareTextil."""

from flask import Flask

from software_textil.bootstrap import crear_servicios
from software_textil.infrastructure.persistence.database import db
from software_textil.presentation.error_handlers import register_error_handlers
from software_textil.presentation.controllers.auth_controller import auth_bp
from software_textil.presentation.controllers.catalogo_controller import catalogo_bp
from software_textil.presentation.controllers.compras_controller import compras_bp
from software_textil.presentation.controllers.configuracion_controller import configuracion_bp
from software_textil.presentation.controllers.contabilidad_controller import contabilidad_bp
from software_textil.presentation.controllers.despachos_controller import despachos_bp
from software_textil.presentation.controllers.facturacion_controller import facturacion_bp
from software_textil.presentation.controllers.inventario_controller import inventario_bp
from software_textil.presentation.controllers.pagos_controller import pagos_bp
from software_textil.presentation.controllers.pedidos_controller import pedidos_bp
from software_textil.presentation.controllers.reportes_controller import reportes_bp
from software_textil.presentation.controllers.usuarios_controller import usuarios_bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///software_textil.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    if "services" not in app.config:
        persistence_backend = app.config.get("PERSISTENCE_BACKEND", app.config.get("PERSISTENCE", "memory"))
        app.config["services"] = crear_servicios(persistence_backend)
    if app.config.get("CREATE_DATABASE"):
        with app.app_context():
            db.create_all()
    register_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalogo_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(despachos_bp)
    app.register_blueprint(contabilidad_bp)
    app.register_blueprint(facturacion_bp)
    app.register_blueprint(configuracion_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(pagos_bp)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
