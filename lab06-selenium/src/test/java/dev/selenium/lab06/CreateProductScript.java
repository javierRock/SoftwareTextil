package dev.selenium.lab06;

import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

/**
 * Paso d) del laboratorio: script Selenium sin xUnit (metodo main).
 * mvn exec:java -Dexec.mainClass=dev.selenium.lab06.CreateProductScript -Dexec.classpathScope=test
 */
public class CreateProductScript {

    public static void main(String[] args) {
        String baseUrl = System.getProperty("base.url", "http://localhost:8083");
        FirefoxOptions opciones = new FirefoxOptions();
        if (Boolean.parseBoolean(System.getProperty("headless", "false"))) {
            opciones.addArguments("-headless");
        }
        WebDriver driver = new FirefoxDriver(opciones);
        try {
            driver.manage().timeouts().implicitlyWait(Duration.ofMillis(500));
            driver.get(baseUrl + "/product/new");
            System.out.println("Pagina: " + driver.getTitle());

            driver.findElement(By.id("productId")).sendKeys("SCRIPT-001");
            driver.findElement(By.id("description")).sendKeys("Producto creado por script");
            driver.findElement(By.id("price")).sendKeys("12.34");
            driver.findElement(By.id("imageUrl")).sendKeys("https://img.test/script.png");
            driver.findElement(By.cssSelector("button[type='submit']")).click();

            String precio = driver.findElement(By.xpath(
                    "//label[normalize-space()='Price:']/following-sibling::div/p")).getText();
            System.out.println("URL resultante: " + driver.getCurrentUrl());
            System.out.println("Precio mostrado: " + precio);
            System.out.println("12.34".equals(precio) ? "RESULTADO: PASO" : "RESULTADO: FALLO");
        } finally {
            driver.quit();
        }
    }
}
