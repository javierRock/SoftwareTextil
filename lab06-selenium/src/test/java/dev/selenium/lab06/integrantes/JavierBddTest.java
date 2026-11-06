package dev.selenium.lab06.integrantes;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import dev.selenium.lab06.soporte.PruebaFuncionalBase;

/**
 * Javier Penalva - BDD (Given / When / Then).
 * Feature: Crear producto
 *   Como administrador de la tienda
 *   Quiero registrar productos desde un formulario
 *   Para que aparezcan en el catalogo
 */
@DisplayName("Javier - BDD (Feature: Crear producto)")
class JavierBddTest extends PruebaFuncionalBase {

    @Test
    @DisplayName("BDD-01 Given el formulario vacio, When envio datos validos, Then veo el detalle")
    void datosValidosMuestranElDetalle() {
        // Given
        pagina.abrirFormulario();
        // When
        pagina.llenar(codigo("BDD01"), "Camisa lino", "79.00", "").enviar();
        // Then
        assertEquals("Product Details", pagina.titulo());
        assertEquals("Camisa lino", pagina.detalle("Description:"));
    }

    @Test
    @DisplayName("BDD-02 Given N productos, When creo uno, Then el listado tiene N+1 filas")
    void listadoCreceEnUno() {
        // Given
        int antes = pagina.filasDelListado().size();
        // When
        pagina.crear(codigo("BDD02"), "Short", "45.00", "");
        // Then
        assertEquals(antes + 1, pagina.filasDelListado().size());
    }

    @Test
    @DisplayName("BDD-03 Given el formulario, When envio todo vacio, Then no se guarda [DEFECTO]")
    void formularioVacioNoSeGuarda() {
        // Given
        pagina.abrirFormulario();
        // When
        pagina.llenar("", "", "", "").enviar();
        // Then
        assertFalse(pagina.estaEnDetalleDeProducto(),
                "Se creo un producto sin ningun dato");
    }

    @Test
    @DisplayName("BDD-04 Given el formulario, When el precio tiene letras, Then veo error 400")
    void precioConLetrasMuestraError() {
        // Given
        pagina.abrirFormulario();
        // When
        pagina.llenar(codigo("BDD04"), "Falda", "12,50 soles", "").enviar();
        // Then
        assertTrue(pagina.textoDeLaPagina().contains("status=400"));
    }

    @Test
    @DisplayName("BDD-05 Given el formulario, When la URL de imagen no es valida, Then se rechaza [DEFECTO]")
    void urlDeImagenInvalidaSeRechaza() {
        // Given
        pagina.abrirFormulario();
        // When
        pagina.llenar(codigo("BDD05"), "Vestido", "99.00", "esto no es una url").enviar();
        // Then
        assertFalse(pagina.estaEnDetalleDeProducto(),
                "Se guardo una URL de imagen con formato invalido");
    }
}
