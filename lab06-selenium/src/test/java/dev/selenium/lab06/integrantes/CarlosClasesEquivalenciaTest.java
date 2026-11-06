package dev.selenium.lab06.integrantes;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import dev.selenium.lab06.soporte.PruebaFuncionalBase;

/**
 * Carlos Gutierrez - Particion en clases de equivalencia.
 * Precio: CV1 numerico >= 0 | CI1 texto no numerico | CI2 numerico negativo.
 * Descripcion: CV2 texto no vacio | CI3 vacia.
 */
@DisplayName("Carlos - Clases de equivalencia (Create Product)")
class CarlosClasesEquivalenciaTest extends PruebaFuncionalBase {

    @Test
    @DisplayName("CE-01 CV1+CV2: datos validos crean el producto")
    void datosValidosCreanElProducto() {
        pagina.crear(codigo("CE01"), "Polo de algodon", "25.50", "https://img.test/polo.png");

        assertAll(
                () -> assertTrue(pagina.estaEnDetalleDeProducto()),
                () -> assertEquals("Polo de algodon", pagina.detalle("Description:")),
                () -> assertEquals("25.50", pagina.detalle("Price:")));
    }

    @Test
    @DisplayName("CE-02 CV1: precio en notacion cientifica (1e3) es numerico valido")
    void precioEnNotacionCientificaEsValido() {
        pagina.crear(codigo("CE02"), "Taza", "1e3", "");

        assertEquals("1000.00", pagina.detalle("Price:"));
    }

    @Test
    @DisplayName("CE-03 CI1: precio no numerico es rechazado")
    void precioNoNumericoEsRechazado() {
        pagina.crear(codigo("CE03"), "Gorra", "abc", "");

        assertFalse(pagina.estaEnDetalleDeProducto());
        assertTrue(pagina.textoDeLaPagina().contains("status=400"));
    }

    @Test
    @DisplayName("CE-04 CI2: precio negativo deberia ser rechazado [DEFECTO]")
    void precioNegativoDeberiaSerRechazado() {
        pagina.crear(codigo("CE04"), "Casaca", "-10", "");

        assertFalse(pagina.estaEnDetalleDeProducto(),
                "El sistema guardo un producto con precio negativo");
    }

    @Test
    @DisplayName("CE-05 CI3: descripcion vacia deberia ser rechazada [DEFECTO]")
    void descripcionVaciaDeberiaSerRechazada() {
        pagina.crear(codigo("CE05"), "", "15.00", "");

        assertFalse(pagina.estaEnDetalleDeProducto(),
                "El sistema guardo un producto sin descripcion");
    }
}
