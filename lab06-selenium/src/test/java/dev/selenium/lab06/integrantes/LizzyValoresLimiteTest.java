package dev.selenium.lab06.integrantes;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import dev.selenium.lab06.soporte.PruebaFuncionalBase;

/**
 * Lizzy Huayhua - Analisis de valores limite.
 * Precio: limite inferior 0 (min-, min, min+) y precision de 2 decimales.
 * Descripcion: columna VARCHAR(255) -> 255 (max) y 256 (max+).
 */
@DisplayName("Lizzy - Valores limite (Create Product)")
class LizzyValoresLimiteTest extends PruebaFuncionalBase {

    @ParameterizedTest(name = "VL-0{index} precio {0} se muestra como {1}")
    @DisplayName("VL-01..03 precio en el limite inferior y su vecino superior")
    @CsvSource({"0, 0.00", "0.01, 0.01", "19.99, 19.99"})
    void preciosEnElLimiteSonAceptados(String precio, String mostrado) {
        pagina.crear(codigo("VL"), "Medias", precio, "");

        assertTrue(pagina.estaEnDetalleDeProducto());
        assertEquals(mostrado, pagina.detalle("Price:"));
    }

    @Test
    @DisplayName("VL-04 precio -0.01 (min-) deberia ser rechazado [DEFECTO]")
    void precioJustoBajoCeroDeberiaSerRechazado() {
        pagina.crear(codigo("VL04"), "Medias", "-0.01", "");

        assertFalse(pagina.estaEnDetalleDeProducto(),
                "El sistema acepto un precio por debajo del limite inferior");
    }

    @Test
    @DisplayName("VL-05 precio con 3 decimales se redondea a 2 (19.999 -> 20.00)")
    void precioConTresDecimalesSeRedondea() {
        pagina.crear(codigo("VL05"), "Medias", "19.999", "");

        assertEquals("20.00", pagina.detalle("Price:"));
    }

    @Test
    @DisplayName("VL-06 descripcion de 255 caracteres (max) es aceptada")
    void descripcionEnElMaximoEsAceptada() {
        String descripcion = "a".repeat(255);
        pagina.crear(codigo("VL06"), descripcion, "10.00", "");

        assertEquals(descripcion, pagina.detalle("Description:"));
    }

    @Test
    @DisplayName("VL-07 descripcion de 256 caracteres (max+) muestra un mensaje de validacion [DEFECTO]")
    void descripcionSobreElMaximoMuestraValidacion() {
        pagina.crear(codigo("VL07"), "a".repeat(256), "10.00", "");

        assertFalse(pagina.textoDeLaPagina().contains("status=500"),
                "El sistema respondio con un error interno 500 en lugar de validar");
    }
}
