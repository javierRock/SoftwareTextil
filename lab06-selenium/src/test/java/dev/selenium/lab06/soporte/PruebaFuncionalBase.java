package dev.selenium.lab06.soporte;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Duration;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.TestInfo;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

/**
 * SetUp y TearDown comunes: cada caso abre un navegador limpio y, al terminar,
 * guarda una captura de pantalla como evidencia y cierra el navegador.
 */
public abstract class PruebaFuncionalBase {

    protected static final String BASE_URL = System.getProperty("base.url", "http://localhost:8083");
    private static final boolean HEADLESS = Boolean.parseBoolean(System.getProperty("headless", "true"));

    protected WebDriver driver;
    protected ProductFormPage pagina;

    @BeforeEach
    void setUp() {
        FirefoxOptions opciones = new FirefoxOptions();
        if (HEADLESS) {
            opciones.addArguments("-headless");
        }
        opciones.addArguments("--width=1280", "--height=900");
        driver = new FirefoxDriver(opciones);
        driver.manage().timeouts().implicitlyWait(Duration.ofMillis(500));
        pagina = new ProductFormPage(driver, BASE_URL);
    }

    @AfterEach
    void tearDown(TestInfo info) throws IOException {
        if (driver != null) {
            Path carpeta = Path.of("target", "capturas", getClass().getSimpleName());
            Files.createDirectories(carpeta);
            Path png = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE).toPath();
            String metodo = info.getTestMethod().map(m -> m.getName()).orElse("caso");
            String indice = info.getDisplayName().matches("^\\S+-0\\d.*|^R\\d.*")
                    ? "-" + info.getDisplayName().split("[ :]")[0] : "";
            String nombre = metodo + indice;
            Files.copy(png, carpeta.resolve(nombre + ".png"), StandardCopyOption.REPLACE_EXISTING);
            driver.quit();
        }
    }

    /** Identificador unico por ejecucion, para que los casos no dependan entre si. */
    protected static String codigo(String prefijo) {
        return prefijo + "-" + Long.toString(System.nanoTime(), 36).toUpperCase();
    }
}
