package dev.selenium.lab06.integrantes;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import dev.selenium.lab06.soporte.PruebaFuncionalBase;

/**
 * Angelo Quispe - Pruebas basadas en el caso de uso "Crear producto".
 * Flujo principal: Home -> Create Product -> llenar -> Submit -> Product Details.
 * Postcondiciones: el producto aparece en el listado y puede editarse.
 */
@DisplayName("Angelo - Casos de uso (Create Product)")
class AngeloCasosUsoTest extends PruebaFuncionalBase {

    @Test
    @DisplayName("CU-01 flujo principal desde el menu de navegacion")
    void flujoPrincipalDesdeElMenu() {
        pagina.abrirDesdeMenu()
                .llenar(codigo("CU01"), "Chompa de alpaca", "149.90", "https://img.test/chompa.png")
                .enviar();

        assertAll(
                () -> assertTrue(pagina.estaEnDetalleDeProducto()),
                () -> assertEquals("Chompa de alpaca", pagina.detalle("Description:")),
                () -> assertEquals("149.90", pagina.detalle("Price:")),
                () -> assertEquals("https://img.test/chompa.png", pagina.detalle("Image Url:")));
    }

    @Test
    @DisplayName("CU-02 postcondicion: el producto aparece en el listado con su Product Id")
    void productoApareceEnElListado() {
        String productId = codigo("CU02");
        pagina.crear(productId, "Bufanda", "35.00", "");

        String listado = pagina.filasDelListado().stream()
                .map(fila -> fila.getText()).reduce("", String::concat);
        assertTrue(listado.contains(productId) && listado.contains("Bufanda"));
    }

    @Test
    @DisplayName("CU-03 postcondicion: el formulario de edicion conserva los datos")
    void edicionConservaLosDatos() {
        String productId = codigo("CU03");
        pagina.crear(productId, "Guantes", "22.00", "");
        String id = pagina.urlActual().replaceAll(".*/", "");

        driver.get(BASE_URL + "/product/edit/" + id);

        assertAll(
                () -> assertEquals(productId, pagina.valorDelCampo("productId")),
                () -> assertEquals("Guantes", pagina.valorDelCampo("description")),
                () -> assertEquals("22.00", pagina.valorDelCampo("price")));
    }

    @Test
    @DisplayName("CU-04 el detalle muestra el Product Id ingresado por el usuario [DEFECTO]")
    void detalleMuestraElProductIdIngresado() {
        String productId = codigo("CU04");
        pagina.crear(productId, "Chalina", "40.00", "");

        assertEquals(productId, pagina.detalle("Product Id:"),
                "La etiqueta 'Product Id' muestra el id interno de la base de datos");
    }

    @Test
    @DisplayName("CU-05 flujo de excepcion: precio invalido muestra pagina de error")
    void flujoDeExcepcionPrecioInvalido() {
        pagina.crear(codigo("CU05"), "Poncho", "cien", "");

        assertTrue(pagina.textoDeLaPagina().contains("Whitelabel Error Page"));
    }
}
