package dev.selenium.lab06.integrantes;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import dev.selenium.lab06.soporte.PruebaFuncionalBase;

/**
 * Alejandro Condori - Tabla de decision.
 * C1: descripcion no vacia | C2: precio numerico | C3: precio >= 0.
 * Accion esperada: GUARDAR solo si C1, C2 y C3 son verdaderas; si no, RECHAZAR.
 *
 * | Regla | C1 | C2 | C3 | Accion   |
 * |  R1   | S  | S  | S  | GUARDAR  |
 * |  R2   | S  | S  | N  | RECHAZAR |
 * |  R3   | S  | N  | -  | RECHAZAR |
 * |  R4   | N  | S  | S  | RECHAZAR |
 * |  R5   | N  | N  | -  | RECHAZAR |
 */
@DisplayName("Alejandro - Tabla de decision (Create Product)")
class AlejandroTablaDecisionTest extends PruebaFuncionalBase {

    @ParameterizedTest(name = "{0}: descripcion=''{1}'' precio=''{2}'' -> {3}")
    @DisplayName("TD R1..R5")
    @CsvSource(value = {
            "R1 | Pantalon jean | 89.90 | GUARDAR",
            "R2 | Pantalon jean | -1    | RECHAZAR",
            "R3 | Pantalon jean | diez  | RECHAZAR",
            "R4 | ''            | 89.90 | RECHAZAR",
            "R5 | ''            | diez  | RECHAZAR",
    }, delimiter = '|')
    void reglaDeDecision(String regla, String descripcion, String precio, String accionEsperada) {
        pagina.crear(codigo(regla), descripcion, precio, "");

        String accionObtenida = pagina.estaEnDetalleDeProducto() ? "GUARDAR" : "RECHAZAR";
        assertEquals(accionEsperada, accionObtenida, "Regla " + regla);
    }
}
