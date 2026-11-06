package dev.selenium.lab06.soporte;

import java.time.Duration;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

/**
 * Page Object de las pantallas de producto de springbootwebapp.
 * Concentra los localizadores para que los casos de prueba solo describan
 * el escenario y el resultado esperado.
 */
public class ProductFormPage {

    private final WebDriver driver;
    private final String baseUrl;

    public ProductFormPage(WebDriver driver, String baseUrl) {
        this.driver = driver;
        this.baseUrl = baseUrl;
    }

    public ProductFormPage abrirFormulario() {
        driver.get(baseUrl + "/product/new");
        return this;
    }

    public ProductFormPage abrirDesdeMenu() {
        driver.get(baseUrl + "/");
        driver.findElement(By.linkText("Create Product")).click();
        return this;
    }

    public ProductFormPage llenar(String productId, String descripcion, String precio, String imagen) {
        escribir("productId", productId);
        escribir("description", descripcion);
        escribir("price", precio);
        escribir("imageUrl", imagen);
        return this;
    }

    /** Envia el formulario y espera a que el navegador abandone /product/new o /edit. */
    public void enviar() {
        String antes = driver.getCurrentUrl();
        driver.findElement(By.cssSelector("button[type='submit']")).click();
        new WebDriverWait(driver, Duration.ofSeconds(10))
                .until(ExpectedConditions.not(ExpectedConditions.urlToBe(antes)));
    }

    public void crear(String productId, String descripcion, String precio, String imagen) {
        abrirFormulario().llenar(productId, descripcion, precio, imagen).enviar();
    }

    /** Valor mostrado en la pagina de detalle para la etiqueta dada (p.ej. "Price:"). */
    public String detalle(String etiqueta) {
        return driver.findElement(By.xpath(
                "//label[normalize-space()='" + etiqueta + "']/following-sibling::div/p")).getText();
    }

    public String valorDelCampo(String id) {
        return driver.findElement(By.id(id)).getAttribute("value");
    }

    /** Titulo de la seccion (el segundo h2; el primero es el banner del sitio). */
    public String titulo() {
        List<WebElement> titulos = driver.findElements(By.cssSelector(".container > h2"));
        return titulos.isEmpty() ? "" : titulos.get(titulos.size() - 1).getText();
    }

    public String textoDeLaPagina() {
        return driver.findElement(By.tagName("body")).getText();
    }

    public String urlActual() {
        return driver.getCurrentUrl();
    }

    public boolean estaEnDetalleDeProducto() {
        return urlActual().matches(".*/product/\\d+$")
                && !driver.findElements(By.xpath("//label[normalize-space()='Price:']"
                        + "/following-sibling::div/p")).isEmpty();
    }

    public List<WebElement> filasDelListado() {
        driver.get(baseUrl + "/products");
        return driver.findElements(By.cssSelector("table tr"));
    }

    private void escribir(String id, String valor) {
        WebElement campo = driver.findElement(By.id(id));
        campo.clear();
        if (valor != null && !valor.isEmpty()) {
            campo.sendKeys(valor);
        }
    }
}
