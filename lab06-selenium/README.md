# Lab 06 – Pruebas funcionales de *Create Product*

Automatización con **Selenium WebDriver 4.26.0** y **JUnit 5.11.3** de la funcionalidad
*Create Product* del proyecto de prueba
[springbootwebapp](https://github.com/springframeworkguru/springbootwebapp).

## Requisitos

- JDK 17 y Maven 3.9 o superior
- Firefox. Selenium Manager descarga geckodriver automáticamente.

## 1. Levantar el proyecto de prueba

```bash
git clone https://github.com/springframeworkguru/springbootwebapp.git
cd springbootwebapp
mvn clean package
java -jar target/spring-boot-web-0.0.1-SNAPSHOT.jar --server.port=8083
```

## 2. Ejecutar las pruebas

```bash
cd lab06-selenium
mvn test                                   # los 27 casos (navegador en modo headless)
mvn test -Dheadless=false                  # viendo el navegador
mvn test -Dtest=AngeloCasosUsoTest         # solo una técnica
mvn test -Dtest=CreateProductSuite         # Test Suite xUnit
mvn surefire-report:report-only            # reporte HTML en target/reports/surefire.html
mvn exec:java -Dexec.mainClass=dev.selenium.lab06.CreateProductScript -Dexec.classpathScope=test
```

Cada caso guarda una captura en `target/capturas/<Clase>/`.

## Técnicas de caja negra por integrante

| Integrante | Clase | Técnica | Casos | Defectos |
|---|---|---|---|---|
| Carlos Gutierrez | `CarlosClasesEquivalenciaTest` | Clases de equivalencia | 5 | 2 |
| Lizzy Huayhua | `LizzyValoresLimiteTest` | Valores límite | 7 | 2 |
| Alejandro Condori | `AlejandroTablaDecisionTest` | Tabla de decisión | 5 | 2 |
| Angelo Quispe | `AngeloCasosUsoTest` | Casos de uso | 5 | 1 |
| Javier Peñalva | `JavierBddTest` | BDD (Given/When/Then) | 5 | 2 |

## Resultado

**27 casos: 18 pasan y 9 fallan.** Los casos que fallan están marcados como `[DEFECTO]`.
Evidencian que `ProductController` no valida las entradas: acepta precios negativos,
descripción vacía, formularios vacíos y URLs inválidas. Además, la descripción de 256
caracteres provoca un error 500 y el detalle muestra el id interno en lugar del
*Product Id* que se ingresó. Surefire está configurado con `testFailureIgnore` para
que el reporte se genere completo.
