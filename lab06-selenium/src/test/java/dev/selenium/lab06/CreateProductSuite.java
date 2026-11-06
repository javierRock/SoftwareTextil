package dev.selenium.lab06;

import org.junit.platform.suite.api.SelectPackages;
import org.junit.platform.suite.api.Suite;
import org.junit.platform.suite.api.SuiteDisplayName;

/** Test Suite xUnit: agrupa los casos de los cinco integrantes. */
@Suite
@SuiteDisplayName("Lab 06 - Create Product (springbootwebapp)")
@SelectPackages("dev.selenium.lab06.integrantes")
public class CreateProductSuite {
}
