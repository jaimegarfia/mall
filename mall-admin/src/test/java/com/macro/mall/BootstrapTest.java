package com.macro.mall;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Bootstrap test to ensure Surefire executes at least one test, enabling JaCoCo to produce execution data.
 */
public class BootstrapTest {

    @Test
    public void shouldRunTests() {
        assertEquals(2, 1 + 1);
    }
}
